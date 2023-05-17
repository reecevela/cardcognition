# Use the Nginx image from Docker Hub as a base
FROM nginx:latest

# Remove the default Nginx configuration file
RUN rm /etc/nginx/conf.d/default.conf

# Copy our custom Nginx configuration file to the proper location
COPY nginx.conf /etc/nginx/conf.d/

# Copy the wait-for-web.sh script to the root directory
COPY wait-for-web.sh /wait-for-web.sh

# Make the wait-for-web.sh script executable
RUN chmod +x /wait-for-web.sh

# Run Nginx in the foreground to prevent Docker from thinking the container has crashed
CMD ["/wait-for-web.sh", "web:8000", "--", "nginx", "-g", "daemon off;"]
