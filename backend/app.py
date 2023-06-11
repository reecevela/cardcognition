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
CORS(app, resources={r"/*": {"origins": [
    "https://cardcognition.com", 
    "http://cardcognition.com", 
    "https://www.cardcognition.com", 
    "http://www.cardcognition.com",
    "https://api.cardcognition.com",
    "http://api.cardcognition.com",
    "https://www.api.cardcognition.com",
    "http://www.api.cardcognition.com",
    "http://localhost:3000",
]}})

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

@app.route('/dbinfo', methods=['GET'])
def get_db_info():
    cur.execute("""
        SELECT 
            AVG(c.synergy_score) as avg_synergy_score,
            (SELECT AVG(avg_synergy_score)
            FROM (
                SELECT AVG(c.synergy_score) as avg_synergy_score
                FROM edhrec_cards c
                GROUP BY c.commander_id
            ) AS commander_avg_synergies) as avg_commander_synergy_score,
        COUNT(DISTINCT cmd.id) as commander_count,
        COUNT(*) as card_commander_pairs_count,
        COUNT(DISTINCT c.card_name) as unique_card_count
        FROM edhrec_cards c
        JOIN edhrec_commanders cmd ON c.commander_id = cmd.id
    """)
    data = cur.fetchone()
    avg_synergy_score, avg_commander_synergy_score, commander_count, card_commander_pairs_count, unique_card_count = data
    return jsonify({"avg_synergy_score": avg_synergy_score, "avg_commander_synergy_score": avg_commander_synergy_score, "commander_count": commander_count, "card_commander_pairs_count": card_commander_pairs_count, "unique_card_count": unique_card_count}), 200


@app.route('/<commander_name>/info', methods=['GET'])
def get_commander_info(commander_name):
    cur.execute("""
        SELECT cmd.name, cmd.scryfall_id,
        (SELECT AVG(c.synergy_score) FROM edhrec_cards c WHERE c.commander_id = cmd.id) as avg_synergy_score,
        (SELECT COUNT(*) FROM edhrec_cards c WHERE c.commander_id = cmd.id) as card_count
        FROM edhrec_commanders cmd
        WHERE cmd.name = %s
    """, (commander_name,))

    data = cur.fetchone()
    if not data:
        return jsonify({"error": "Commander not found."}), 404
    name, scryfall_id, avg_synergy_score, card_count = data

    cur.execute("""
        SELECT cmd2.card_name, cmd2.name, cmd2.scryfall_id, COUNT(DISTINCT c2.card_name), COUNT(DISTINCT c2.card_name) * 100.0 / %s as overlap_percentage
        FROM edhrec_cards c1
        JOIN edhrec_commanders cmd1 ON c1.commander_id = cmd1.id
        JOIN edhrec_cards c2 ON c1.card_name = c2.card_name
        JOIN edhrec_commanders cmd2 ON c2.commander_id = cmd2.id
        WHERE cmd1.name = %s AND cmd1.id != cmd2.id
        GROUP BY cmd2.card_name, cmd2.name, cmd2.scryfall_id
        ORDER BY overlap_percentage DESC
        LIMIT 5
    """, (card_count, commander_name))


    similar_commanders = [{"card_name": card_name, "name": name, "scryfall_id": scryfall_id, "overlap_count": overlap_count, "overlap_percentage": overlap_percentage} for card_name, name, scryfall_id, overlap_count, overlap_percentage in cur.fetchall()]

    return jsonify({
        "name": name,
        "scryfall_id": scryfall_id,
        "avg_synergy_score": avg_synergy_score,
        "card_count": card_count,
        "similar_commanders": similar_commanders
    }), 200


@app.route('/<commander_name>/suggestions/<count>', methods=['GET'])
def get_suggestions(commander_name, count):
    # Get the suggestions for the commander
    try:
        int(count)
    except ValueError:
        # Probably using range, so count would look like "range/100/200"
        # Redirect to range endpoint
        return get_suggestions_range(commander_name, count.split('/')[1], count.split('/')[2])

    if int(count) > 100:
        count = 100

    cur.execute("""
    SELECT c.card_name, c.synergy_score, c.scryfall_id
    FROM edhrec_cards c
    JOIN edhrec_commanders cmd ON c.commander_id = cmd.id
    WHERE cmd.name = %s
    ORDER BY c.synergy_score DESC
    LIMIT %s
    """, (commander_name, count))

    data = cur.fetchall()
    suggestions = [{'name': name, 'score': score, 'scryfall_id': scryfall_id} for name, score, scryfall_id in data]
    
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
    if int(end) > int(start) + 100:
        end = start + 100

    cur.execute("""
    SELECT c.card_name, c.synergy_score, c.scryfall_id
    FROM edhrec_cards c
    JOIN edhrec_commanders cmd ON c.commander_id = cmd.id
    WHERE cmd.name = %s
    ORDER BY c.synergy_score DESC
    LIMIT %s
    OFFSET %s
    """, (commander_name, end, start))
    data = cur.fetchall()
    suggestions = [{'name': name, 'score': score, 'scryfall_id': scryfall_id} for name, score, scryfall_id in data]
    if not suggestions:
        return jsonify({"error": "No suggestions found for this commander."}), 404
    return jsonify({"suggestions": suggestions, "start": start, "end": end}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)