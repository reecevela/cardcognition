from flask import Flask, jsonify
from urllib.parse import urlparse
from pathlib import Path
import psycopg2
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))

app = Flask(__name__)

# Database Configuration
url = urlparse(os.environ['DATABASE_URL'])
conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)
cur = conn.cursor()

@app.route('/api/<commander_name>/suggestions/<count>', methods=['GET'])
def get_suggestions(commander_name, count):
    # Get the suggestions for the commander
    COUNT_LIMIT = 100
    cur.execute("""
    SELECT c.card_name, c.synergy_score
    FROM edhrec_cards c
    JOIN edhrec_commanders cmd ON c.commander_id = cmd.id
    WHERE cmd.name = %s
    ORDER BY c.synergy_score DESC
    LIMIT %s
    """, (commander_name, COUNT_LIMIT))
    suggestions = cur.fetchall()
    if not suggestions:
        return jsonify({"error": "No suggestions found for this commander."}), 404
    return jsonify({"suggestions": suggestions}), 200

if __name__ == '__main__':
    app.run(debug=True)