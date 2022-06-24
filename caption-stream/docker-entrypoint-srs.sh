#!/bin/bash

set -e

STUNNEL_IVS_CONF=/etc/stunnel/conf.d/ivs.conf

sed -i 's|<IVS_ENDPOINT>|'"$IVS_ENDPOINT"'|g' $STUNNEL_IVS_CONF

stunnel4

cd /srs/trunk

./objs/srs -c conf/docker.conf

exec "$@"