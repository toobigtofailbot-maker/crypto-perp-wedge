#!/bin/sh
set -eu
umask 077
private=/keys/private/id_ed25519
public=/keys/public/id_ed25519.pub
if [ ! -e "$private" ] && [ ! -e "$public" ]; then
    ssh-keygen -q -t ed25519 -N '' -f "$private"
    mv "$private.pub" "$public"
fi
test -s "$private"
test -s "$public"
# Validate the pair without writing key bytes to output or logs.
ssh-keygen -y -f "$private" | cut -d ' ' -f 1,2 > /tmp/cpw-public-check
cut -d ' ' -f 1,2 "$public" > /tmp/cpw-public-expected
cmp -s /tmp/cpw-public-check /tmp/cpw-public-expected
rm /tmp/cpw-public-check /tmp/cpw-public-expected
chown 0:0 "$private"
chmod 0400 "$private"
chown 10000:10000 "$private"
chmod 0444 "$public"
