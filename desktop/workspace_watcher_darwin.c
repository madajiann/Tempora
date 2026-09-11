//go:build darwin && cgo

#include <CoreServices/CoreServices.h>
#include <dispatch/dispatch.h>
#include <stdint.h>
#include <stdlib.h>

extern void temporaFSEventsEvent(uintptr_t token, char *path, uint32_t flags);

typedef struct tempora_fsevents_subscription {
    FSEventStreamRef stream;
    dispatch_queue_t queue;
} tempora_fsevents_subscription;

static void tempora_fsevents_callback(
    ConstFSEventStreamRef stream_ref,
    void *callback_info,
    size_t event_count,
    void *event_paths,
    const FSEventStreamEventFlags event_flags[],
    const FSEventStreamEventId event_ids[]
) {
    (void)stream_ref;
    (void)event_ids;
    char **paths = event_paths;
    uintptr_t token = (uintptr_t)callback_info;
    for (size_t index = 0; index < event_count; index++) {
        if (paths[index] != NULL) {
            temporaFSEventsEvent(token, paths[index], (uint32_t)event_flags[index]);
        }
    }
}

static void tempora_fsevents_barrier(void *context) {
    (void)context;
}

tempora_fsevents_subscription *tempora_fsevents_start(
    const char *path,
    uintptr_t token,
    double latency,
    int *error_code
) {
    if (error_code != NULL) {
        *error_code = 0;
    }
    if (path == NULL || path[0] == '\0') {
        if (error_code != NULL) {
            *error_code = 1;
        }
        return NULL;
    }

    tempora_fsevents_subscription *subscription = calloc(1, sizeof(*subscription));
    if (subscription == NULL) {
        if (error_code != NULL) {
            *error_code = 2;
        }
        return NULL;
    }

    CFStringRef path_string = CFStringCreateWithFileSystemRepresentation(kCFAllocatorDefault, path);
    if (path_string == NULL) {
        if (error_code != NULL) {
            *error_code = 1;
        }
        free(subscription);
        return NULL;
    }
    const void *values[] = { path_string };
    CFArrayRef paths = CFArrayCreate(kCFAllocatorDefault, values, 1, &kCFTypeArrayCallBacks);
    CFRelease(path_string);
    if (paths == NULL) {
        if (error_code != NULL) {
            *error_code = 2;
        }
        free(subscription);
        return NULL;
    }

    subscription->queue = dispatch_queue_create("com.tempora.workspace-fsevents", DISPATCH_QUEUE_SERIAL);
    if (subscription->queue == NULL) {
        if (error_code != NULL) {
            *error_code = 3;
        }
        CFRelease(paths);
        free(subscription);
        return NULL;
    }

    FSEventStreamContext context = {0, (void *)token, NULL, NULL, NULL};
    FSEventStreamCreateFlags flags = kFSEventStreamCreateFlagFileEvents |
        kFSEventStreamCreateFlagWatchRoot |
        kFSEventStreamCreateFlagNoDefer;
    subscription->stream = FSEventStreamCreate(
        kCFAllocatorDefault,
        tempora_fsevents_callback,
        &context,
        paths,
        kFSEventStreamEventIdSinceNow,
        latency,
        flags
    );
    CFRelease(paths);
    if (subscription->stream == NULL) {
        if (error_code != NULL) {
            *error_code = 4;
        }
#if !OS_OBJECT_USE_OBJC
        dispatch_release(subscription->queue);
#endif
        free(subscription);
        return NULL;
    }

    FSEventStreamSetDispatchQueue(subscription->stream, subscription->queue);
    if (!FSEventStreamStart(subscription->stream)) {
        if (error_code != NULL) {
            *error_code = 5;
        }
        FSEventStreamInvalidate(subscription->stream);
        FSEventStreamRelease(subscription->stream);
#if !OS_OBJECT_USE_OBJC
        dispatch_release(subscription->queue);
#endif
        free(subscription);
        return NULL;
    }
    return subscription;
}

void tempora_fsevents_stop(tempora_fsevents_subscription *subscription) {
    if (subscription == NULL) {
        return;
    }
    FSEventStreamStop(subscription->stream);
    FSEventStreamInvalidate(subscription->stream);
    dispatch_sync_f(subscription->queue, NULL, tempora_fsevents_barrier);
    FSEventStreamRelease(subscription->stream);
#if !OS_OBJECT_USE_OBJC
    dispatch_release(subscription->queue);
#endif
    free(subscription);
}
