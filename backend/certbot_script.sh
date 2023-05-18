while ! nc -z nginx 80; do   
  echo "nginx is unavailable - sleeping"
  sleep 1
done

echo "nginx is up - executing command"

certbot certonly --webroot --webroot-path=/var/www/html --email reecevela@outlook.com --agree-tos --no-eff-email --force-renewal -d cardcognition.com -d www.cardcognition.com
