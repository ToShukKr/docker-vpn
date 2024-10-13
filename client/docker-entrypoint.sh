#!/bin/sh
set -e

if [ -z "$VPN_USERNAME" ] || [ -z "$VPN_PASSWORD" ] || [ -z "$VPN_HOSTNAME" ]; then
  echo "Error: Please check required variables (VPN_USERNAME, VPN_PASSWORD, VPN_HOSTNAME)"
  exit 1
fi

config="
pty \"pptp $VPN_HOSTNAME --nolaunchpppd\"
name $VPN_USERNAME
password $VPN_PASSWORD
require-mppe-128
refuse-eap
refuse-pap
refuse-chap
refuse-mschap
require-mschap-v2
noauth
nodefaultroute
persist
maxfail 0
debug
nodetach
"
echo "$config" > /etc/ppp/peers/client

pppd call client &

while ! ip addr show ppp0 > /dev/null 2>&1; do
  echo "Waiting for ppp0 interface..."
  sleep 1
done

VPN_IP=""
TRIES=0
MAX_TRIES=20

while [ -z "$VPN_IP" ] && [ "$TRIES" -lt "$MAX_TRIES" ]; do
  VPN_IP=$(ip addr show ppp0 | grep 'inet ' | awk '{print $2}' | cut -d'/' -f1)
  if [ -z "$VPN_IP" ]; then
    echo "Waiting for IP address on ppp0..."
    sleep 2
    TRIES=$((TRIES + 1))
  fi
done

if [ -z "$VPN_IP" ]; then
  echo "Error: Failed to obtain IP address on ppp0 after $MAX_TRIES attempts"
  exit 1
fi

echo "VPN IP: $VPN_IP"
NETWORK=$(echo "$VPN_IP" | awk -F. '{print $1"."$2"."$3".0"}')

echo "VPN Network (for routing): $NETWORK"
echo "Adding route to network $NETWORK/24 via interface ppp0..."
route add -net "$NETWORK/24" dev ppp0

if [ $? -eq 0 ]; then
  echo "Route added successfully."
else
  echo "Error: Failed to add route."
fi

wait
