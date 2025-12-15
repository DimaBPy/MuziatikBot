import os

from db import connect_db

DB = "muziatikbot"
print("Recreating schema in:", os.path.abspath(DB))

cur, con = connect_db()


def drop():
    cur.execute("""
                DROP TABLE IF EXISTS feedback CASCADE;
                DROP TABLE IF EXISTS memory CASCADE;
                DROP TABLE IF EXISTS users CASCADE;
                """)


def create():
    cur.execute("""
                CREATE TABLE if not exists users
                (
                    id            SMALLSERIAL PRIMARY KEY,
                    tg_id         BIGINT NOT NULL UNIQUE,
                    name          TEXT,
                    beta          VARCHAR,
                    voice_time    INTEGER,
                    voice_counter INTEGER
                );

                CREATE TABLE if not exists memory
                (
                    id      SMALLSERIAL PRIMARY KEY,
                    user_id INTEGER,
                    data    TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );

                CREATE TABLE if not exists feedback
                (
                    id      SMALLSERIAL PRIMARY KEY,
                    user_id INTEGER,
                    message TEXT,
                    urgent BOOLEAN NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );
                """)


if __name__ == '__main__':
    drop()
    create()
    print("Done — tables recreated.")
con.commit()
con.close()
