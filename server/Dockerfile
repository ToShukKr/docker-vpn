FROM alpine:3.17

RUN apk add --no-cache \
        iptables \
        pptpd \
        bash

ENV SUBNET 192.168.192.0/24
ENV LOCAL_IP 192.168.192.1
ENV REMOTE_IP 192.168.192.1-200

COPY ./configs/options.pptp /etc/ppp/options.pptp

COPY ./docker-entrypoint.sh /.

EXPOSE 1723

ENTRYPOINT ["/docker-entrypoint.sh"]
