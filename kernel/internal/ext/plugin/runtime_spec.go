// Ported from DeepSeek-Reasonix (MIT) — upstream PR #11468.
package plugin

import (
	"reflect"
	"strings"
	"time"

	"tempora/internal/safety/sandbox"
)

// MCPRuntimeSpecMatches compares the complete host-local runtime behavior of
// two specs while deliberately excluding non-behavioral handles such as the
// stderr writer and LaunchManager pointer. Secret values are compared only in
// memory and are never serialized into diagnostics or provider-visible state.
func MCPRuntimeSpecMatches(a, b Spec) bool {
	return reflect.DeepEqual(mcpRuntimeSpecIdentityOf(a), mcpRuntimeSpecIdentityOf(b))
}

// mcpRuntimeSpecIdentity is the comparable shape of one server's runtime: the
// fields that decide how it behaves, and therefore whether two specs may share
// one connection. A policy field that changes what the model can call belongs
// here, so a host never hands a caller the tools of a different policy.
type mcpRuntimeSpecIdentity struct {
	Name                    string
	Package                 string
	Type                    string
	Command                 string
	Args                    []string
	Env                     map[string]string
	URL                     string
	Headers                 map[string]string
	DefaultStartupTimeout   time.Duration
	StartupTimeout          time.Duration
	DefaultCallTimeout      time.Duration
	CallTimeout             time.Duration
	ToolTimeouts            map[string]time.Duration
	DisabledTools           []string
	Dir                     string
	WorkspaceRoot           string
	LaunchWorkspace         string
	ConfigSource            string
	RequireLaunchApproval   bool
	LaunchArgs              []string
	LauncherIdentityArgs    []string
	LauncherLocator         string
	LauncherResolvedVersion string
	LauncherDigest          string
	ProcessMode             MCPProcessMode
	Sandbox                 sandbox.Spec
	StateDir                string
	StripRawPrefix          string
	LowPriority             bool
}

// mcpRuntimeSpecIdentityOf projects a Spec onto its comparable identity.
// Disabled tools enter it normalized (sorted, de-duplicated), so nil and empty
// are the same policy and order never changes the identity.
func mcpRuntimeSpecIdentityOf(s Spec) mcpRuntimeSpecIdentity {
	launchWorkspace := ""
	if s.LaunchManager != nil {
		launchWorkspace = s.LaunchManager.WorkspaceFingerprint()
	}
	return mcpRuntimeSpecIdentity{
		Name:                    strings.TrimSpace(s.Name),
		Package:                 strings.TrimSpace(s.Package),
		Type:                    canonicalMCPRuntimeTransport(s.Type),
		Command:                 s.Command,
		Args:                    nonEmptyStrings(s.Args),
		Env:                     nonEmptyStringMap(s.Env),
		URL:                     s.URL,
		Headers:                 nonEmptyStringMap(s.Headers),
		DefaultStartupTimeout:   s.DefaultStartupTimeout,
		StartupTimeout:          s.StartupTimeout,
		DefaultCallTimeout:      s.DefaultCallTimeout,
		CallTimeout:             s.CallTimeout,
		ToolTimeouts:            nonEmptyDurationMap(s.ToolTimeouts),
		DisabledTools:           disabledToolNames(s.DisabledTools),
		Dir:                     s.Dir,
		WorkspaceRoot:           s.WorkspaceRoot,
		LaunchWorkspace:         launchWorkspace,
		ConfigSource:            strings.TrimSpace(s.ConfigSource),
		RequireLaunchApproval:   s.RequireLaunchApproval,
		LaunchArgs:              nonEmptyStrings(s.LaunchArgs),
		LauncherIdentityArgs:    nonEmptyStrings(s.LauncherIdentityArgs),
		LauncherLocator:         s.LauncherLocator,
		LauncherResolvedVersion: s.LauncherResolvedVersion,
		LauncherDigest:          s.LauncherDigest,
		ProcessMode:             s.ResolvedProcessMode(),
		Sandbox:                 canonicalMCPRuntimeSandbox(s.Sandbox),
		StateDir:                s.StateDir,
		StripRawPrefix:          s.StripRawPrefix,
		LowPriority:             s.LowPriority,
	}
}

func canonicalMCPRuntimeTransport(raw string) string {
	switch strings.ToLower(strings.TrimSpace(raw)) {
	case "", "stdio":
		return "stdio"
	case "http", "streamable-http", "streamable_http":
		return "streamable-http"
	case "sse":
		return "sse"
	default:
		return strings.ToLower(strings.TrimSpace(raw))
	}
}

func canonicalMCPRuntimeSandbox(in sandbox.Spec) sandbox.Spec {
	in.WriteRoots = nonEmptyStrings(in.WriteRoots)
	in.ReadRoots = nonEmptyStrings(in.ReadRoots)
	in.AppContainerWriteRoots = nonEmptyStrings(in.AppContainerWriteRoots)
	in.ForbidReadRoots = nonEmptyStrings(in.ForbidReadRoots)
	return in
}

func nonEmptyStrings(in []string) []string {
	if len(in) == 0 {
		return nil
	}
	return in
}

func nonEmptyStringMap(in map[string]string) map[string]string {
	if len(in) == 0 {
		return nil
	}
	return in
}

func nonEmptyDurationMap(in map[string]time.Duration) map[string]time.Duration {
	if len(in) == 0 {
		return nil
	}
	return in
}
