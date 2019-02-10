#!/usr/bin/env python

import argparse
import os
import subprocess
import nginx as n
import sys

def get_no_ssl_settings(domains):
	s = n.nginx_object()
	s.add_property('listen', 80)
	s.add_property('server_name', domains)
	s.add_property('location', ['~ /.well-known/acme-challenge/', n.nginx_object('root', '/etc/letsencrypt/challenges/')])
	http = n.nginx_object()
	http.add_property('server', s)
	return http

#if not redirect - proxy pass
def get_ssl_settings(domains, site, include, redirect):
	s = n.nginx_object()
	#http part - redirect to https
	http = n.nginx_object()
	http.add_property('listen', 80)
	http.add_property('server_name', domains)
	http.add_property('location', ['/', n.nginx_object('return', '301 https://$server_name$request_uri')])
	s.add_property('server', http)
	#https part
	https = n.nginx_object()
	https.add_property('listen', '443 ssl')
	https.add_property('server_name', args.d)
	#certbot location
	https.add_property('location', ['~ /.well-known/acme-challenge/', n.nginx_object('root', '/etc/letsencrypt/challenges/')])
	#proxy or redirect location
	l = n.nginx_object()
	if redirect:
		l.add_property('return', '301 ' + site)
	else:
		l.add_property('proxy_pass', site)
		l.add_property('proxy_set_header', ['X-Real-Ip', '$remote_addr'])
		l.add_property('proxy_set_header', ['X-Forwarded-For', '$proxy_add_x_forwarded_for'])
		l.add_property('proxy_set_header', ['Host', '$http_host'])
		l.add_property('proxy_redirect', 'off')
	if include:
		l.add_property('include', [os.path.join('conf.d', i) for i in include])
	https.add_property('location', ['/', l])
	#ssl cert properties
	https.add_property('ssl_certificate', '/etc/letsencrypt/live/{}/fullchain.pem'.format(domains[0]))
	https.add_property('ssl_certificate_key', '/etc/letsencrypt/live/{}/privkey.pem'.format(domains[0]))
	https.add_property('include', os.path.join('conf.d', 'ssl.incl'))

	s.add_property('server', https)
	return s

class readable_dir(argparse.Action):
	def __call__(self, parser, namespace, values, option_string=None):
		prospective_dir=values[0]
		if not os.path.isdir(prospective_dir):
			raise argparse.ArgumentTypeError("readable_dir:{0} is not a valid path".format(prospective_dir))
		if os.access(prospective_dir, os.R_OK):
			setattr(namespace,self.dest,prospective_dir)
		else:
			raise argparse.ArgumentTypeError("readable_dir:{0} is not a readable dir".format(prospective_dir))

parser = argparse.ArgumentParser(description='Add site to nginx')
parser.add_argument('-d', nargs='+', type=str, help='domains')
parser.add_argument('-u', nargs=1, type=str, help='proxy pass (by default) or redirect url')
parser.add_argument('-i', nargs='*', type=str, help='include file')
parser.add_argument('-r', action='store_true', help='redirect flag: redirect if present, proxy pass otherwise')
args = parser.parse_args()

conf_file_name = args.d[0] + '.conf'
conf_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../volumes/nginx/etc/nginx/conf.d', conf_file_name)
if os.path.exists(conf_file_path):
	print('file {} alredy exists, please remove it first'.format(conf_file_path))
	sys.exit(1)

conf_file = open(conf_file_path, 'w')
s = n.nginx_object_serializer('\t')
conf_file.write(s.to_string(get_no_ssl_settings(args.d)))
conf_file.flush()
return_code = subprocess.call('docker exec nginx nginx -s reload', shell=True)
if return_code:
	sys.exit(return_code)

print(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'certbot.sh') + ' certonly --webroot -w /etc/letsencrypt/challenges ' + ' '.join(['-d ' + d for d in args.d]))
return_code = subprocess.call(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'certbot.sh') + ' certonly --webroot -w /etc/letsencrypt/challenges ' + ' '.join([' -d ' + d for d in args.d]),
								shell=True)
if return_code:
	sys.exit(return_code)

conf_file.truncate(0)
conf_file.seek(0)
conf_file.write(s.to_string(get_ssl_settings(args.d, args.u[0], args.i, args.r)))
conf_file.flush()
subprocess.call('docker exec nginx nginx -s reload', shell=True)
