import datetime
import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def connect_db():
    con = psycopg2.connect(
        dbname=os.getenv('DATABASE'),
        user=os.getenv('DBUSER'),
        password=os.getenv('DB_PSWD'),
        host='localhost',
        port='5432',
    )
    cur = con.cursor()
    return cur, con


def log_event(event, user_id, value, field, extra=''):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] {event}: user_id={user_id}, field={field}, value={value} {extra}"
    with open('memory_log.txt', 'a', encoding='utf-8') as logf:
        logf.write(log_msg + '\n')
    print(log_msg)


def remember(user_id: int, value, field=None):
    """Save or update a field for a specific user (nested dictionary)."""
    cur, con = connect_db()
    try:
        cur.execute('''
                    INSERT
                    INTO users (tg_id)
                    values (%s)
                    on conflict do nothing
                    ''', (user_id,))
        con.commit()
        if field in ('name', 'voice_time', 'voice_counter', 'beta'):
            cur.execute(f'''
                        UPDATE users
                        SET {field} = %s
                        WHERE tg_id = %s
                        ''', (value, user_id))
            log_event('FIELD_UPDATE', user_id, value, field)
        else:
            cur.execute(
                """
                INSERT INTO memory (user_id, data)
                SELECT id, %s
                FROM users
                WHERE tg_id = %s
                """,
                (value, user_id)
            )
            log_event('MEMORY_INSERT', user_id, value, field)
        con.commit()
    finally:
        con.close()


# remember(1183930315, 1, 'voice_counter')

def recall(user_id: int, field=None):
    cur, con = connect_db()
    try:
        if field in ('name', 'voice_time', 'voice_counter', 'beta'):
            cur.execute(f'''
                                 SELECT {field}
                                 FROM users
                                 WHERE tg_id = %s''', (user_id,))
            row = cur.fetchone()
            result = row[0] if row else None
        else:
            cur.execute('''SELECT memory.id, data
                           FROM memory
                                    JOIN users ON memory.user_id = users.id
                           WHERE users.tg_id = %s
                        ''', (user_id,))
            result = list()
            data = cur.fetchall()
            if field == 'id':
                for i in data:
                    result.append(str(i[0]))
            else:
                for i in data:
                    result.append(str(i[0]) + ': ' + i[1])
        con.close()
        if not result:
            return ['Нет элементов в памяти😔']
        return result
    except Exception as e:
        print(e)
        con.close()


def forget(user_id: int, data_id: int = None):
    cur, con = connect_db()
    try:
        if not data_id:
            cur.execute('''
                        DELETE
                        FROM memory
                        WHERE user_id = (SELECT id FROM users WHERE tg_id = %s)''', (user_id,))
        else:
            cur.execute('''
                        DELETE
                        FROM memory
                        WHERE id = %s
                          AND user_id = (SELECT id FROM users WHERE tg_id = %s)''',
                        (data_id, user_id))
        con.commit()
    finally:
        con.close()


def forget_name(user_id: int):
    cur, con = connect_db()
    try:
        cur.execute('''
                    UPDATE users
                    SET name = NULL
                    WHERE tg_id = %s''', (user_id,))
        con.commit()
    finally:
        con.close()


def create_feedback(user_id: int, message: str, urgent: bool = False) -> int:
    cur, con = connect_db()
    try:
        cur.execute(
            """
            INSERT INTO feedback (user_id, message)
            VALUES ((SELECT id FROM users WHERE tg_id = %s), %s)
            RETURNING id
            """,
            (user_id, message),
        )
        feedback_id = cur.fetchone()[0]
        con.commit()
        return feedback_id
    finally:
        con.close()


def get_feedback(user_id: int, _id=None):
    cur, con = connect_db()
    try:
        if _id is None:
            cur.execute(
                """
                SELECT id, message
                FROM feedback
                WHERE user_id = (SELECT id FROM users WHERE tg_id = %s)
                ORDER BY id
                """,
                (user_id,),
            )
            rows = cur.fetchall()
            return [(row[0], row[1], bool(row[2])) for row in rows]
        else:
            cur.execute(
                """
                SELECT id, message
                FROM feedback
                WHERE user_id = (SELECT id FROM users WHERE tg_id = %s)
                  AND id = %s
                ORDER BY id
                """,
                (user_id, _id),
            )
            rows = cur.fetchall()
            return [(row[0], row[1]) for row in rows]
    finally:
        con.close()


def delete_feedback(user_id: int, feedback_id: int) -> None:
    cur, con = connect_db()
    try:
        cur.execute(
            """
            DELETE
            FROM feedback
            WHERE id = %s
              AND user_id = (SELECT id FROM users WHERE tg_id = %s)
            """,
            (feedback_id, user_id),
        )
        con.commit()
    finally:
        con.close()


if __name__ == "__main__":
    recall(5862759148, 'name')
    print("Database schema and script setup complete.")
