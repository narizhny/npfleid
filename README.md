# Nginx proxy for Let's Encrypt in Docker

# (npfleid)

## howto

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
"i" is optional if you want to restrict access.  
"u" is proxy pass (by default) or redirect url.  
"d" is you domain name. You can specify many for one host. ```-d docker.example.ru www.docker.example.ru``` for example
"r" use redirection instead of proxy

```bash
chmod +x scripts/*
scripts/add_host.py -d docker.example.ru -i acl.incl -u http://portainer:9000/
```

* Go to docker.example.ru in you browser.

* Add a script to automatically reissue the certificate.

```bash
sudo crontab -e
* 12 * * 7 /var/lib/docker/compose/base/scripts/renew.sh
```