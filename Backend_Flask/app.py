from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 仮のランキングDB（リストで保存）
ranking_data = []

@app.route('/submit', methods=['POST'])
def submit_score():
    data = request.get_json()
    username = data.get('username')
    score = data.get('score')
    
    if not username or score is None:
        return jsonify({'error': 'Missing data'}), 400

    ranking_data.append({'username': username, 'score': score})
    # スコアの高い順にソート（上位5件のみ）
    sorted_data = sorted(ranking_data, key=lambda x: x['score'], reverse=True)[:5]
    return jsonify({'message': 'Success', 'ranking': sorted_data})

@app.route('/ranking', methods=['GET'])
def get_ranking():
    sorted_data = sorted(ranking_data, key=lambda x: x['score'], reverse=True)[:5]
    return jsonify({'ranking': sorted_data})