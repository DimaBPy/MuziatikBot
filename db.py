import sqlite3


def connect_db():
    con = sqlite3.connect('MuziatikBot.db')
    con.cursor()
    return con


def remember(user_id: int, value, field=None):
    """Save or update a field for a specific user (nested dictionary)."""
    con = connect_db()
    try:
        con.execute('''
                    INSERT
                    OR IGNORE INTO users (tg_id) values (?)
                    ''', (user_id,))
        con.commit()
        if field in ('name', 'voice_time', 'voice_counter', 'beta'):
            con.execute(f'''
                        UPDATE users
                        SET {field} = ?
                        WHERE tg_id = ?
                        ''', (value, user_id))
        else:
            con.execute(
                """
                INSERT INTO memory (user_id, data)
                SELECT id, ?
                FROM users
                WHERE tg_id = ?
                """,
                (value, user_id)
            )
        con.commit()
    finally:
        con.close()


# remember(1183930315, 1, 'voice_counter')

def recall(user_id: int, field=None):
    con = connect_db()
    try:
        if field in ('name', 'voice_time', 'voice_counter', 'beta'):
            cursor = con.execute(f'''
                                 SELECT {field}
                                 FROM users
                                 WHERE tg_id = ?''', (user_id,))
            result = cursor.fetchone()
            print(result)
            result = result[0]
            print(result)
        else:
            cursor = con.execute('''SELECT memory.id, data
                                    FROM memory
                                             JOIN users ON memory.user_id = users.id
                                    WHERE users.tg_id = ?
                                 ''', (user_id,))
            result = list()
            data = cursor.fetchall()
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
    con = connect_db()
    try:
        if not data_id:
            con.execute('''
                        DELETE
                        FROM memory
                        WHERE user_id = (SELECT id FROM users WHERE tg_id = ?)''', (user_id,))
        else:
            con.execute('''
                        DELETE
                        FROM memory
                        WHERE id = ?
                          AND user_id = (SELECT id FROM users WHERE tg_id = ?)''',
                        (data_id, user_id))
        con.commit()
    finally:
        con.close()


if __name__ == "__main__":
    recall(5862759148, 'name')
    print("Database schema and script setup complete.")
