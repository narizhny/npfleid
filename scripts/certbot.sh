#!/bin/sh
docker run --rm -v $(realpath $(dirname "$0")/../volumes/nginx/etc/letsencrypt):/etc/letsencrypt -v $(realpath $(dirname "$0")/../volumes/nginx/var/log/letsencrypt):/var/log/letsencrypt certbot/certbot "$@" 
