#!/bin/bash

# install openssl
sudo apt-get install openssl

# Generate self-signed SSL certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout certs/nginx-selfsigned.key -out certs/nginx-selfsigned.crt -subj "/CN=localhost"
