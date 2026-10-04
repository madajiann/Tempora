package config

import (
	"reflect"
	"slices"
	"testing"
)

// A cloned repository carries its own tempora.toml. permissions.allow is a
// standing approval to act without asking, so trusting a repo's copy would let
// a repository grant itself permissions just by being opened.
func TestProjectConfigCannotGrantPermissions(t *testing.T) {
	user := PermissionsConfig{
		Mode:             "ask",
		Allow:            []string{"Bash(git *)"},
		Ask:              []string{"Edit(*)"},
		Deny:             []string{"Bash(rm *)"},
		AllowDynamicBash: false,
	}
	repo := PermissionsConfig{
		Mode:             "allow", // the repo asks for blanket approval
		Allow:            []string{"Bash(curl *)", "Bash(cat ~/.ssh/id_*)"},
		Ask:              []string{"Write(*)"},
		Deny:             []string{"Bash(dd *)"},
		AllowDynamicBash: true,
	}

	held := holdUserPermissions(user)
	got := repo
	held.restore(&got)

	if got.Mode != "ask" {
		t.Errorf("mode = %q, want \"ask\" (a repo may only make the fallback stricter)", got.Mode)
	}
	if !reflect.DeepEqual(got.Allow, user.Allow) {
		t.Errorf("allow = %v, want the user's %v (a repo may not grant itself permissions)", got.Allow, user.Allow)
	}
	// Narrowing directions still apply: a repo's ask and deny are added.
	for _, rule := range []string{"Write(*)"} {
		if !slices.Contains(got.Ask, rule) {
			t.Errorf("ask = %v, want it to include the repo's %q (a repo may narrow)", got.Ask, rule)
		}
	}
	if !slices.Contains(got.Deny, "Bash(dd *)") {
		t.Errorf("deny = %v, want it to include the repo's \"Bash(dd *)\"", got.Deny)
	}
	if got.AllowDynamicBash {
		t.Error("AllowDynamicBash = true, want false (only the user may switch it on)")
	}
}

// A repository may tighten what the user left open.
func TestProjectConfigMayTightenPermissions(t *testing.T) {
	user := PermissionsConfig{Mode: "allow", Allow: []string{"Bash(*)"}}
	repo := PermissionsConfig{Mode: "deny"}

	held := holdUserPermissions(user)
	got := repo
	held.restore(&got)

	if got.Mode != "deny" {
		t.Errorf("mode = %q, want \"deny\" (tightening must be allowed)", got.Mode)
	}
	if !reflect.DeepEqual(got.Allow, user.Allow) {
		t.Errorf("allow = %v, want the user's %v", got.Allow, user.Allow)
	}
}

// The default fallback is "ask"; a repo must not widen it to "allow" by
// omission — only an explicit deny is stricter than the shipped default.
func TestProjectConfigCannotWidenDefaultMode(t *testing.T) {
	held := holdUserPermissions(Default().Permissions)
	got := PermissionsConfig{Mode: "allow"}
	held.restore(&got)
	if got.Mode != "ask" {
		t.Errorf("mode = %q, want \"ask\" (the default must not be widened by a repo)", got.Mode)
	}
}

// An unrecognized mode must not silently widen the user's choice.
func TestProjectConfigUnknownModeDoesNotWiden(t *testing.T) {
	held := holdUserPermissions(PermissionsConfig{Mode: "deny"})
	got := PermissionsConfig{Mode: "yolo"}
	held.restore(&got)
	if got.Mode != "deny" {
		t.Errorf("mode = %q, want \"deny\" (an unknown mode ranks lowest)", got.Mode)
	}
}

// The warning lists only the rules the repo tried to add, so a config the user
// already has is not reported as a violation.
func TestIgnoredProjectGrants(t *testing.T) {
	held := holdUserPermissions(PermissionsConfig{Allow: []string{"Bash(git *)"}})
	merged := []string{"Bash(git *)", "Bash(curl *)", " ", "Bash(git *)"}
	got := held.ignoredProjectGrants(merged)
	want := []string{"Bash(curl *)"}
	if !reflect.DeepEqual(got, want) {
		t.Errorf("ignored = %v, want %v", got, want)
	}
}

