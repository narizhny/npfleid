#!/bin/sh
docker run -it --rm -v $(realpath $(dirname "$0")/../volumes/nginx/etc/letsencrypt):/etc/letsencrypt webdevops/certbot /usr/bin/certbot "$@" 
