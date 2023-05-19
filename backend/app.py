from flask import Flask, jsonify
from flask_cors import CORS
from urllib.parse import urlparse
from pathlib import Path
import psycopg2
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(os.path.join(BASE_DIR, '.env'))

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["api.cardcognition.com", "https://api.cardcognition.com", "http://api.cardcognition.com"]}})

# Database Configuration
db_config = {
    'name': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

# Connect to the database
conn = psycopg2.connect(
    dbname=db_config['name'],
    user=db_config['user'],
    password=db_config['password'],
    host=db_config['host'],
    port=db_config['port']
)
cur = conn.cursor()

@app.route('/<commander_name>/suggestions/<count>', methods=['GET'])
def get_suggestions(commander_name, count):
    # Get the suggestions for the commander
    try:
        int(count)
    except ValueError:
        return jsonify({"error": "Count must be an integer."}), 400
    
    if int(count) > 100:
        count = 100
    cur.execute("""
    SELECT c.card_name, c.synergy_score
    FROM edhrec_cards c
    JOIN edhrec_commanders cmd ON c.commander_id = cmd.id
    WHERE cmd.name = %s
    ORDER BY c.synergy_score DESC
    LIMIT %s
    """, (commander_name, count))
    suggestions = cur.fetchall()
    if not suggestions:
        return jsonify({"error": "No suggestions found for this commander."}), 404
    return jsonify({"suggestions": suggestions, "count": count}), 200

@app.route('/<commander_name>/suggestions/range/<start>/<end>', methods=['GET'])
def get_suggestions_range(commander_name, start, end):
    # Get the suggestions for the commander
    try:
        int(start)
        int(end)
    except ValueError:
        return jsonify({"error": "Start and end must be integers."}), 400

    if int(start) < 0:
        start = 0
    if int(end) > start + 100:
        end = start + 100

    cur.execute("""
    SELECT c.card_name, c.synergy_score
    FROM edhrec_cards c
    JOIN edhrec_commanders cmd ON c.commander_id = cmd.id
    WHERE cmd.name = %s
    ORDER BY c.synergy_score DESC
    LIMIT %s
    OFFSET %s
    """, (commander_name, end, start))
    suggestions = cur.fetchall()
    if not suggestions:
        return jsonify({"error": "No suggestions found for this commander."}), 404
    return jsonify({"suggestions": suggestions, "start": start, "end": end}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)