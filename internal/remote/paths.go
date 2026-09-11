package remote

import "tempora/internal/config"

// defaultManagedKnownHosts is the Tempora-managed known_hosts path. It is a
// thin indirection over config so tests can leave HostKeyPolicy.ManagedPath
// empty and still get an isolated file under TEMPORA_HOME.
func defaultManagedKnownHosts() string {
	return config.RemoteKnownHostsPath()
}
