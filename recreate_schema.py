import sqlite3
import os

DB = "muziatikBot.db"
print("Recreating schema in:", os.path.abspath(DB))

con = sqlite3.connect(DB)
cur = con.cursor()

cur.executescript("""
                  DROP TABLE IF EXISTS memory;
                  DROP TABLE IF EXISTS users;

                  CREATE TABLE users
                  (
                      id            INTEGER PRIMARY KEY AUTOINCREMENT,
                      tg_id         INTEGER NOT NULL UNIQUE,
                      name          TEXT,
                      beta          VARCHAR,
                      voice_time    INTEGER,
                      voice_counter INTEGER
                  );

                  CREATE TABLE memory
                  (
                      id      INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      data    TEXT,
                      FOREIGN KEY (user_id) REFERENCES users (id)
                  );
                  """)

con.commit()
con.close()
print("Done — tables recreated.")
