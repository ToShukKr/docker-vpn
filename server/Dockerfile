FROM alpine:3.20

RUN apk add --no-cache \
        openvpn \
        easy-rsa

ENV SUBNET_RANGE="10.100.100.0 255.255.255.0"
ENV EASYRSA_BATCH=1
ENV EASYRSA_WORKDIR=/etc/openvpn/easy-rsa
ENV CLIENTS_CONFIG_DIR=/etc/openvpn/ccd
ENV OVPN_CONFIG_DIR=/etc/openvpn/ovpn-configs

COPY bin/client-mgr /usr/local/bin/client-mgr

WORKDIR /

COPY ./docker-entrypoint.sh /.

ENTRYPOINT ["/docker-entrypoint.sh"]
