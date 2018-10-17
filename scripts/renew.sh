$(dirname "$0")/certbot.sh  renew
docker exec nginx nginx -s reload
