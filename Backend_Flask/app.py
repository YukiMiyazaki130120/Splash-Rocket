import mysql.connector
from flask import Flask, request, jsonify
from flask_cors import CORS
import heapq
from datetime import datetime, timedelta
import logging
import os

logger = logging.getLogger('flask-app')
logger.setLevel(logging.INFO)

log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tmp', 'flask-app.log')
file_handler = logging.FileHandler(log_path)
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

print("LOG PATH:", log_path)

app = Flask(__name__)
CORS(app)

# MySQL 接続設定
db_config = {
    'host': 'splash-rocket-db.cxeai88c4vza.ap-northeast-1.rds.amazonaws.com',
    'user': 'admin',               # RDS作成時に設定したユーザ名
    'password': 'Splash123!',  # RDS作成時のパスワード
    'database': 'splash_rocket' 
}

@app.route('/')
def health_check():
    logger.info(f"通信成功！")
    return 'OK', 200

@app.route('/submit', methods=['POST'])
def submit_score():
    data = request.get_json()
    username = data.get('username')
    score = data.get('score')
    uuid = data.get('uuid')

    if not username or score is None or uuid is None:
        logger.error("エラー: データが欠損しています")
        return jsonify({'error': 'Missing data'}), 400

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # 既にuuidが存在するか確認
    cursor.execute("SELECT score FROM rankings WHERE uuid = %s", (uuid,))
    existing = cursor.fetchone()

    if existing:
        # 既存スコアより高ければ更新
        if score > existing[0]:
            logger.info(f"スコアを更新しました！uuid={uuid}, score={score}")
            cursor.execute(
                "UPDATE rankings SET username = %s, score = %s, created_at = CURRENT_TIMESTAMP WHERE uuid = %s",
                (username, score, uuid)
            )
    else:
        # 新規登録
        logger.info(f"スコアを登録しました！username={username}, score={score}！")
        cursor.execute(
            "INSERT INTO rankings (uuid, username, score) VALUES (%s, %s, %s)",
            (uuid, username, score)
        )

    conn.commit()
    cursor.close()
    conn.close()
    logger.info(f"スコアの提出が成功しました！")
    return jsonify({'message': 'Score submitted successfully'})


@app.route('/ranking', methods=['GET'])
def get_ranking():
    range_type = request.args.get('range', 'all')  # 'daily', 'weekly', 'monthly', or 'all'

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # 日付フィルタ
    date_filter = ""
    if range_type == 'daily':
        date_filter = "WHERE created_at >= NOW() - INTERVAL 1 DAY"
    elif range_type == 'weekly':
        date_filter = "WHERE created_at >= NOW() - INTERVAL 7 DAY"
    elif range_type == 'monthly':
        date_filter = "WHERE created_at >= NOW() - INTERVAL 1 MONTH"

    # UUID単位の最新スコアを集計
    query = f"""
        SELECT username, MAX(score) AS score
        FROM rankings
        {date_filter}
        GROUP BY uuid
    """
    cursor.execute(query)
    all_data = cursor.fetchall()

    # 上位10件抽出
    top_10 = heapq.nlargest(10, all_data, key=lambda x: x['score'])

    cursor.close()
    conn.close()
    logger.info(f"ランキング情報を送信しました！")
    return jsonify({'ranking': top_10})

def init_db():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rankings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            uuid VARCHAR(64) NOT NULL UNIQUE,
            username VARCHAR(255) NOT NULL,
            score INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()
    print("MySQL rankings テーブル初期化完了")
    logger.info(f"MySQL rankings テーブル初期化完了")

# Flask アプリのエントリポイント
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=80)
