#!/bin/bash

set -e

NGINX_CONF=/etc/nginx/nginx.conf 
STUNNEL_IVS=/etc/stunnel/conf.d/ivs.conf
IVS_INGEST_ENDPOINT=$(curl -X GET $SERVER_ADDRESSES"/nacos/v1/cs/configs?dataId="$DATA_ID"&group="$GROUP"&tenant="$NAMESPACE | grep ivs_address | awk -F '["]' '{print $4}')

# if [ -n "${IVS_URL}" ] && [ -n "${IVS_KEY}" ]; then
# 	sed -i 's|<IVS_URL><IVS_KEY>|'"$IVS_URL""${IVS_KEY}"'|g' $NGINX_CONF
# fi

if [ -n "${DEBUG}" ]; then 
	echo $NGINX_CONF
	cat $NGINX_CONF
fi

if [ -n "${IVS_INGEST_ENDPOINT}" ]; then
	echo "Ivs ingest endpoint ${IVS_INGEST_ENDPOINT}"
	sed -i 's|connect=|connect='${IVS_INGEST_ENDPOINT}'|g' $STUNNEL_IVS
fi

echo "Starting NginX server..."

stunnel4

exec "$@"
