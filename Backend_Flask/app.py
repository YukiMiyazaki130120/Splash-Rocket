from flask import Flask, request, jsonify
from flask_cors import CORS
import heapq

app = Flask(__name__)
CORS(app)

# ユーザー名をキーとした辞書にする
ranking_data = {}

@app.route('/submit', methods=['POST'])
def submit_score():
    data = request.get_json()
    username = data.get('username')
    score = data.get('score')

    if not username or score is None:
        return jsonify({'error': 'Missing data'}), 400

    # 同じユーザー名なら、スコアが高い方のみを保持
    if username in ranking_data:
        if score > ranking_data[username]:
            ranking_data[username] = score
    else:
        ranking_data[username] = score

    # ✅ 上位10件を抽出
    top_10 = heapq.nlargest(10, ranking_data.items(), key=lambda x: x[1])
    formatted = [{"username": u, "score": s} for u, s in top_10]

    return jsonify({'message': 'Success', 'ranking': formatted})

@app.route('/ranking', methods=['GET'])
def get_ranking():
    top_10 = heapq.nlargest(10, ranking_data.items(), key=lambda x: x[1])
    formatted = [{"username": u, "score": s} for u, s in top_10]
    return jsonify({'ranking': formatted})
