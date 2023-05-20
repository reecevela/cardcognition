#!/bin/bash

# install openssl
apk add --no-cache openssl

# Create the directory for certificates if it doesn't exist
mkdir -p /etc/nginx/certs

# Generate self-signed SSL certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/nginx/certs/nginx-selfsigned.key -out /etc/nginx/certs/nginx-selfsigned.crt -subj "/CN=localhost"
