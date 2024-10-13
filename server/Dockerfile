FROM alpine:3.17

RUN apk add --no-cache \
        iptables \
        pptpd \
        bash

ENV SUBNET 10.100.100.0/24
ENV LOCAL_IP 10.100.100.1
ENV REMOTE_IP 10.100.100.1-200

COPY ./configs/options.pptp /etc/ppp/options.pptp

COPY ./docker-entrypoint.sh /.

EXPOSE 1723

ENTRYPOINT ["/docker-entrypoint.sh"]
