FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt and install the python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app
COPY . .

# Add and give permissions to the script that will wait for the database
ADD wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Run the script before starting the app
CMD /wait-for-it.sh db:5432 -- gunicorn -b 0.0.0.0:8000 app:app
