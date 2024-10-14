#!/bin/sh
set -e

export EASYRSA_REQ_CN="OpenVPN CA Server"
export OPENVPN_CONFIG_FILE=/etc/openvpn/server.conf

mkdir -p ${EASYRSA_WORKDIR} ${CLIENTS_CONFIG_DIR} ${OVPN_CONFIG_DIR}
cp -r /usr/share/easy-rsa/* ${EASYRSA_WORKDIR}
cd ${EASYRSA_WORKDIR}

if [ ! -f ${OPENVPN_CONFIG_FILE} ]; then
  echo "Initializing PKI"
  ./easyrsa init-pki  > /dev/null 2>&1
  echo "Build CA Cetrificate"
  ./easyrsa build-ca nopass  > /dev/null 2>&1
  echo "Generation REQ"
  ./easyrsa gen-req server nopass  > /dev/null 2>&1
  echo "Sign REQ"
  ./easyrsa sign-req server server  > /dev/null 2>&1
  echo "Generating DH"
  ./easyrsa gen-dh  > /dev/null 2>&1
else
  echo "Generatin RSA is skipped"
fi

echo "Generatin OpenVPN Server Configuration File"
cat <<EOF > ${OPENVPN_CONFIG_FILE}
port 1194
proto tcp
dev tap
ca /etc/openvpn/easy-rsa/pki/ca.crt
cert /etc/openvpn/easy-rsa/pki/issued/server.crt
key /etc/openvpn/easy-rsa/pki/private/server.key
dh /etc/openvpn/easy-rsa/pki/dh.pem
server ${SUBNET_RANGE}
client-to-client
ifconfig-pool-persist ipp.txt
client-config-dir ${CLIENTS_CONFIG_DIR}
route-nopull
keepalive 10 120
persist-key
persist-tun
status openvpn-status.log
verb 5
EOF

openvpn --config /etc/openvpn/server.conf
