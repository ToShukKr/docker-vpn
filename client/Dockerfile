FROM alpine:3.17

RUN echo "https://dl-cdn.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories && \
    echo "https://dl-cdn.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories && \
    echo "https://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories

RUN apk update && \
    apk add --no-cache \
        ppp \
        pptpclient

COPY ./docker-entrypoint.sh /.

ENTRYPOINT ["/docker-entrypoint.sh"]
