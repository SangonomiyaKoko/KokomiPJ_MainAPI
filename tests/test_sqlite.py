import sqlite3
import json

def main():
    user_result = []
    clan_result = []
    region_id = 1
    db_path = r'F:\Kokomi_PJ_Api\temp\user_cn.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = "SELECT aid, clan_id FROM user"
    cursor.execute(query)
    rows = cursor.fetchall()
    for row in rows:
        user_result.append(row[0])
        if row[1] and row[1] not in clan_result:
            clan_result.append(row[1])
    conn.commit()
    cursor.close()
    conn.close()
    with open(r'F:\Kokomi_PJ_Api\temp\old_user_cn.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(user_result, ensure_ascii=False))
    f.close()
    with open(r'F:\Kokomi_PJ_Api\temp\old_clan_cn.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(clan_result, ensure_ascii=False))
    f.close()

if __name__ == '__main__':
    main()