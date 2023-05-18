# Max tries of 100

MaxTries=100

while ! nc -z backend_nginx_1 80; do   
  echo "nginx is unavailable - sleeping"
  sleep 1
    ((MaxTries--))
    if [ $MaxTries -le 0 ]; then
        echo "Max tries reached"
        exit 1
    fi
done

echo "nginx is up - executing command"

certbot certonly --webroot --webroot-path=/var/www/html --email reecevela@outlook.com --agree-tos --no-eff-email --force-renewal -d cardcognition.com -d www.cardcognition.com
