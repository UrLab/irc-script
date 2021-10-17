#!/bin/sh
grep password .weechat/relay.conf | awk -F " = " '{gsub(/"/, "", $2); print $2}'
