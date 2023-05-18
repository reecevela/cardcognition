FROM nginx:alpine

# Remove the default nginx.conf
RUN rm /etc/nginx/conf.d/default.conf

# Replace with our own nginx.conf
COPY nginx.conf /etc/nginx/conf.d/

RUN apk add --no-cache openssl

# Create a self-signed certificate
RUN mkdir -p /etc/letsencrypt/live/cardcognition.com/
RUN openssl req -x509 -nodes -newkey rsa:1024 -days 1\
    -keyout '/etc/letsencrypt/live/cardcognition.com/privkey.pem' \
    -out '/etc/letsencrypt/live/cardcognition.com/fullchain.pem' \
    -subj '/CN=localhost'