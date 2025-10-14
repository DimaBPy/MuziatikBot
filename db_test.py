import sqlite3, os, sys

db = 'muziatikBot.db'
print("DB PATH:", os.path.abspath(db))
if not os.path.exists(db):
    print("ERROR: database file not found:", db);
    sys.exit(1)
con = sqlite3.connect(db)
cur = con.cursor()
print("\n--- TABLES ---");
print(cur.execute("SELECT name,type FROM sqlite_master WHERE type IN ('table','view')").fetchall())
print("\n--- SCHEMA users ---")
for row in cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'"): print(row[0])
print("\n--- SCHEMA memory ---")
for row in cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='memory'"): print(row[0])
print("\n--- PRAGMAS ---")
for p in ['journal_mode', 'synchronous', 'foreign_keys']: print(p, cur.execute(f"PRAGMA {p};").fetchone())
print("\n--- PRAGMA table_info(users) ---");
print(cur.execute("PRAGMA table_info('users')").fetchall())
print("\n--- PRAGMA table_info(memory) ---");
print(cur.execute("PRAGMA table_info('memory')").fetchall())
print("\n--- DUPLICATE USERS (tg_id count>1) ---");
print(cur.execute("SELECT tg_id, COUNT(*) FROM users GROUP BY tg_id HAVING COUNT(*)>1").fetchall())
print("\n--- DUPLICATE MEMORY (user_id,data count>1) ---");
print(cur.execute("SELECT user_id, data, COUNT(*) FROM memory GROUP BY user_id, data HAVING COUNT(*)>1").fetchall())
print("\n--- SAMPLE users (first 20) ---");
print(cur.execute("SELECT id,tg_id,name FROM users ORDER BY id LIMIT 20").fetchall())
print("\n--- SAMPLE memory (first 20) ---");
print(cur.execute("SELECT id,user_id,data FROM memory ORDER BY id LIMIT 20").fetchall())
con.close()
