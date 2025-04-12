import mysql.connector
from flask import Flask, request, jsonify
from flask_cors import CORS
import heapq

app = Flask(__name__)
CORS(app)

# MySQL 接続設定
db_config = {
    'host': 'localhost',  # EC2 の場合は 127.0.0.1
    'user': 'root',
    'password': '',
    'database': 'splash_rocket'
}

@app.route('/submit', methods=['POST'])
def submit_score():
    data = request.get_json()
    username = data.get('username')
    score = data.get('score')

    if not username or score is None:
        return jsonify({'error': 'Missing data'}), 400

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # 既存ユーザの最高スコアと比較
    cursor.execute("SELECT score FROM rankings WHERE username = %s ORDER BY score DESC LIMIT 1", (username,))
    existing = cursor.fetchone()

    if not existing or score > existing[0]:
        cursor.execute("INSERT INTO rankings (username, score) VALUES (%s, %s)", (username, score))
        conn.commit()

    cursor.close()
    conn.close()

    return jsonify({'message': 'Score submitted successfully'})

@app.route('/ranking', methods=['GET'])
def get_ranking():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT username, MAX(score) AS score
        FROM rankings
        GROUP BY username
    """)
    all_data = cursor.fetchall()

    top_10 = heapq.nlargest(10, all_data, key=lambda x: x['score'])

    cursor.close()
    conn.close()

    return jsonify({'ranking': top_10})
