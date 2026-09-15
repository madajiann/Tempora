package main

import (
	"context"
	"os"
	"path/filepath"
	"testing"

	"tempora/internal/config"
	"tempora/internal/worktree"
)

func TestDeliveryWorktreeAvailabilityDelegatesWithoutRequiringGit(t *testing.T) {
	original := inspectDeliveryWorktree
	t.Cleanup(func() { inspectDeliveryWorktree = original })
	inspectDeliveryWorktree = func(_ context.Context, root string) worktree.Availability {
		return worktree.Availability{Available: false, Reason: "Git is not installed", RepoRoot: root}
	}
	got := NewApp().DeliveryWorktreeAvailability("project")
	if got.Available || got.Reason != "Git is not installed" || got.RepoRoot != "project" {
		t.Fatalf("availability = %+v", got)
	}
}

func TestCreateDeliveryWorktreeRegistersAndOpensManagedProject(t *testing.T) {
	home := t.TempDir()
	t.Setenv("TEMPORA_HOME", home)
	t.Setenv("TEMPORA_STATE_HOME", home)
	t.Setenv("TEMPORA_CACHE_HOME", filepath.Join(home, "cache"))
	managed := config.DeliveryWorktreeDir()
	isolatedRoot := filepath.Join(managed, "repo", "id", "project")
	if err := os.MkdirAll(isolatedRoot, 0o755); err != nil {
		t.Fatal(err)
	}

	original := createDeliveryWorktree
	t.Cleanup(func() { createDeliveryWorktree = original })
	createDeliveryWorktree = func(_ context.Context, source, gotManaged string) (worktree.Result, error) {
		if source != "source-project" {
			t.Fatalf("source = %q", source)
		}
		if gotManaged != managed {
			t.Fatalf("managed root = %q, want %q", gotManaged, managed)
		}
		return worktree.Result{
			WorkspaceRoot: isolatedRoot,
			WorktreeRoot:  filepath.Dir(isolatedRoot),
			SourceRoot:    "source-project",
			Branch:        "tempora/delivery-test",
			SourceDirty:   true,
		}, nil
	}

	app := NewApp()
	t.Cleanup(func() { app.shutdown(context.Background()) })
	result, err := app.CreateDeliveryWorktree("source-project")
	if err != nil {
		t.Fatal(err)
	}
	if result.WorkspaceRoot != isolatedRoot || result.Branch != "tempora/delivery-test" || !result.SourceDirty {
		t.Fatalf("result = %+v", result)
	}
	if result.Tab.WorkspaceRoot != isolatedRoot || !result.Tab.IsolatedWorktree || !result.Tab.Active {
		t.Fatalf("opened tab = %+v", result.Tab)
	}
	if result.Tab.TokenMode != "full" {
		t.Fatalf("isolated worktree tokenMode = %q, want full", result.Tab.TokenMode)
	}
	if result.Tab.QualityFloor != "standard" || result.Tab.FloorInferred {
		t.Fatalf("isolated worktree floor = %q inferred=%v, want standard/false", result.Tab.QualityFloor, result.Tab.FloorInferred)
	}
}
