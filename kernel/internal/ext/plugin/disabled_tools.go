// Ported from DeepSeek-Reasonix (MIT) — upstream PR #11468.
package plugin

import "slices"

// ToolEnabled matches the server's raw tool name, before prefix stripping.
func (s Spec) ToolEnabled(rawName string) bool {
	return !slices.Contains(s.DisabledTools, rawName)
}

// EnabledCachedTools applies current policy even to a stale schema snapshot.
func (s Spec) EnabledCachedTools(tools []CachedTool) []CachedTool {
	if len(s.DisabledTools) == 0 {
		return tools
	}
	return slices.DeleteFunc(slices.Clone(tools), func(t CachedTool) bool { return !s.ToolEnabled(t.Name) })
}

// disabledToolNames normalizes a disabled-tool policy for identity comparison:
// sorted, de-duplicated, and empty when nothing is disabled. Two policies that
// differ only in order or duplicates describe the same runtime.
func disabledToolNames(names []string) []string {
	if len(names) == 0 {
		return nil
	}
	names = slices.Clone(names)
	slices.Sort(names)
	return slices.Compact(names)
}
