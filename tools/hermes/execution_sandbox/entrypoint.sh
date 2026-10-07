#!/bin/sh
set -eu
umask 077
mkdir -p /run/sshd /run/cpw-sandbox-hostkeys
chmod 0700 /run/cpw-sandbox-hostkeys
chown cpw:cpw /workspace
if [ ! -f /run/cpw-sandbox-hostkeys/ssh_host_ed25519_key ]; then
    ssh-keygen -q -t ed25519 -N '' -f /run/cpw-sandbox-hostkeys/ssh_host_ed25519_key
fi
test -s /run/cpw-sandbox-public/id_ed25519.pub
exec /usr/sbin/sshd -D -e -f /etc/ssh/sshd_config
