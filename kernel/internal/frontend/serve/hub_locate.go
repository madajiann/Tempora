package serve

import (
	"encoding/json"
	"net/http"
	"os"
	"path/filepath"
	"strings"
)

const (
	codeWorkspaceUnknown = "workspace.not_listed"
	codeWorkspaceMissing = "workspace.folder_missing"
)

// revealWorkspace opens a listed project's folder in the system file manager.
// It reveals only folders the window already lists, so the page cannot use it
// to reach an arbitrary path. One step, unlike upstream's split locate+shell
// reveal: our kernel already owns revealFolder (themes_install.go) and the
// Tauri shell has no file-manager command of its own.
// Semantics ported from DeepSeek-Reasonix (MIT) (#11533).
func (h *Hub) revealWorkspace(w http.ResponseWriter, r *http.Request) {
	var body struct {
		Root string `json:"root"`
	}
	if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
		badBody(w)
		return
	}
	root := strings.TrimSpace(body.Root)
	if root == "" {
		missingField(w, "root")
		return
	}
	listed, ok := h.listedWorkspace(root)
	if !ok {
		refuse(w, http.StatusNotFound, codeWorkspaceUnknown, "that folder is not a project in this window", nil)
		return
	}
	abs, err := filepath.Abs(listed)
	if err != nil {
		writeErr(w, http.StatusInternalServerError, err)
		return
	}
	info, err := os.Stat(abs)
	if err != nil || !info.IsDir() {
		refuse(w, http.StatusNotFound, codeWorkspaceMissing, "the project folder is not on disk", nil)
		return
	}
	if err := revealFolder(abs); err != nil {
		refuse(w, http.StatusInternalServerError, "workspace.reveal_failed", err.Error(), nil)
		return
	}
	writeJSON(w, struct {
		Path string `json:"path"`
	}{Path: abs})
}

// listedWorkspace returns the window's own copy of the listed root that equals
// root, so nothing downstream touches the request's string.
func (h *Hub) listedWorkspace(root string) (string, bool) {
	for _, ref := range h.roots() {
		if ref.dir == root {
			return ref.dir, true
		}
	}
	h.mu.RLock()
	defer h.mu.RUnlock()
	for _, rt := range h.runtimes {
		if rt.Server == nil || !rt.Local() {
			continue
		}
		if dir := rt.Server.Controller().WorkspaceRoot(); dir == root {
			return dir, true
		}
	}
	return "", false
}
