import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'splash_rocket'
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# 6ヶ月より古いデータを削除
cursor.execute("""
    DELETE FROM rankings
    WHERE created_at < DATE_SUB(NOW(), INTERVAL 6 MONTH)
""")

conn.commit()
cursor.close()
conn.close()

print("古いデータを削除しました。")
