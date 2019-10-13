# Nginx proxy for Let's Encrypt in Docker

# (npfleid)

## Usage

* Install docker, docker-compose.

```bash
apt-get install -y docker.io docker-compose
wget https://github.com/narizhny/npfleid/archive/master.zip
unzip master.zip
mkdir -p /var/lib/docker/compose/base
mv npfleid-master/* /var/lib/docker/compose/base
```

* (optional)
Create acl.incl file for access restriction. Change 8.8.8.0/24 to you network.

```bash
echo "allow 8.8.8.0/24;" >> /var/lib/docker/compose/base/volumes/nginx/etc/nginx/conf.d/acl.incl
echo "deny all;" >> /var/lib/docker/compose/base/volumes/nginx/etc/nginx/conf.d/acl.incl
```

* Start containers.

```bash
docker network create frontend
cd /var/lib/docker/compose/base
docker-compose up -d
```

* Add host. Do not forget to set the A record for your domain to this server. Do it for all sites that you need.  
"i" is optional if you want to include file in configuration.  
"u" is proxy pass (by default) or redirect url.  
"d" is you domain name. You can specify many for one host. ```-d docker.example.ru www.docker.example.ru``` for example
"r" optional flag, for using redirection instead of proxy

```bash
chmod +x scripts/*
scripts/add_host.py -d docker.example.ru -i acl.incl -u http://portainer:9000/
```

* Go to docker.example.ru in you browser.

* Add cron task to automatically reissue the certificate.

```bash
sudo crontab -e
0 12 * * 7 /var/lib/docker/compose/base/scripts/renew.sh
```

or 

```bash
(crontab -l; echo "0 12 * * 7 /var/lib/docker/compose/base/scripts/renew.sh" ) | crontab -
```

## How to ...

* ...add more services?

You can either add services in existing ```/var/lib/docker/compose/base/docker-compose.yml``` file and recreate services, or (better way) create another ```docker-compose.yml``` in different folder. You should add "backend" external network for each service, that should be available for nginx:

```
services:
  web_service_name:
    ...
    networks:
    - frontend
    - backend
    ...

networks:
    backend:
    frontend:
        external: true
```

* ...edit nginx configuration?

```
nano /var/lib/docker/compose/base/volumes/nginx/etc/nginx/conf.d/example.com.conf
...
docker exec nginx nginx -s reload
```

## Known limitations

* Nginx will fail to start, until all services are started. So, if you want to remove some services - you should also remove nginx configuration file from ```/var/lib/docker/compose/base/volumes/nginx/etc/nginx/conf.d/``` folder.