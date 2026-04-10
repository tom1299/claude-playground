#!/bin/sh
set -e

DNS_SERVER="${DNS_SERVER:-}"

create_proxy_config() {
  mkdir -p /root/.docker
  cat > /root/.docker/config.json <<-EOF
	{
	  "proxies": {
	    "default": {
	      "httpProxy": "${http_proxy}",
	      "httpsProxy": "${https_proxy}",
	      "noProxy": "${no_proxy}"
	    }
	  }
	}
	EOF
}

create_daemon_config() {
  mkdir -p /etc/docker
  # Only add dns server if it's reachable, otherwise not
  if [ -n "$DNS_SERVER" ] && nc -z -w 2 "$DNS_SERVER" 53 2>/dev/null; then
    cat > /etc/docker/daemon.json <<-EOF
	{
	  "tls": false,
	  "dns": ["${DNS_SERVER}"],
	  "hosts": ["unix:///var/run/docker.sock", "tcp://0.0.0.0:2375"]
	}
	EOF
  else
    cat > /etc/docker/daemon.json <<-EOF
	{
	  "tls": false,
	  "hosts": ["unix:///var/run/docker.sock", "tcp://0.0.0.0:2375"]
	}
	EOF
  fi
}

if [ -n "$http_proxy" ] || [ -n "$https_proxy" ]; then
  create_proxy_config
fi

create_daemon_config

exec "$@"
