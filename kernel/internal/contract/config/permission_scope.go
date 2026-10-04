package config

import (
	"slices"
	"strings"
)

// Permission grants are a user trust decision, not a repository preference.
//
// A cloned repository carries its own tempora.toml, and permissions.allow is
// the one key that hands the agent a standing permission to act without asking.
// Trusting a repo's copy would mean opening an untrusted project is enough to
// pre-approve its own tool calls — the repo would be granting itself the
// permissions. So the user's grants are the only ones that count, and a
// repository may only narrow them.
//
// This mirrors sandbox_scope.go: the same rule for the same reason.

func holdUserPermissions(p PermissionsConfig) heldPermissions {
	return heldPermissions{
		mode:             strings.TrimSpace(p.Mode),
		allow:            slices.Clone(p.Allow),
		ask:              slices.Clone(p.Ask),
		deny:             slices.Clone(p.Deny),
		allowDynamicBash: p.AllowDynamicBash,
	}
}

type heldPermissions struct {
	mode             string
	allow            []string
	ask              []string
	deny             []string
	allowDynamicBash bool
}

// permissionStrictness ranks the fallback decisions from most permissive to
// most restrictive. An unrecognized mode ranks lowest so a typo or a value from
// a newer version can never widen the user's choice.
func permissionStrictness(mode string) int {
	switch strings.ToLower(strings.TrimSpace(mode)) {
	case "allow":
		return 1
	case "ask":
		return 2
	case "deny":
		return 3
	default:
		return 0
	}
}

// restore puts back what a repo may not change. The fallback mode may only get
// stricter; allow is a grant and so comes from the user alone; ask and deny
// only narrow, so a repo's entries are added rather than replacing.
func (h heldPermissions) restore(p *PermissionsConfig) {
	if permissionStrictness(p.Mode) < permissionStrictness(h.mode) {
		p.Mode = h.mode
	}
	p.Allow = h.allow
	p.Ask = mergeRuleLists(h.ask, p.Ask)
	p.Deny = mergeRuleLists(h.deny, p.Deny)
	// Dynamic bash approval at run time is the widest grant of all: a repo may
	// not switch it on, only the user may. Turning it off is a narrowing, so
	// that direction is allowed.
	if !h.allowDynamicBash {
		p.AllowDynamicBash = false
	}
}

// ignoredProjectGrants returns the allow rules the merged config carries that
// the user never granted: the ones a repository tried to give itself. It drives
// the load warning, so it must not flag rules the user already has.
func (h heldPermissions) ignoredProjectGrants(merged []string) []string {
	var out []string
	for _, rule := range merged {
		rule = strings.TrimSpace(rule)
		if rule == "" || slices.Contains(h.allow, rule) {
			continue
		}
		out = append(out, rule)
	}
	return out
}

// mergeRuleLists unions two rule lists, keeping the user's order and dropping
// duplicates so a repo cannot shadow a rule by repeating it.
func mergeRuleLists(user, repo []string) []string {
	out := slices.Clone(user)
	for _, rule := range repo {
		rule = strings.TrimSpace(rule)
		if rule == "" || slices.Contains(out, rule) {
			continue
		}
		out = append(out, rule)
	}
	return out
}
