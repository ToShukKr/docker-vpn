FROM alpine:3.20

RUN apk add --no-cache openvpn

COPY client.ovpn /client.ovpn

CMD openvpn --config client.ovpn
