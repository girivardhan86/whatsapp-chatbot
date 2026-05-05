import sqlite3


def init_db():

    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT,
            role TEXT,
            message TEXT,
            is_problem INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def save_message(phone_number, role, message):

    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO messages (phone_number, role, message) VALUES (?, ?, ?)",
        (phone_number, role, message)
    )

    conn.commit()
    conn.close()


def get_chat_history(phone_number):

    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT role, message FROM messages WHERE phone_number=? ORDER BY timestamp ASC",
        (phone_number,)
    )

    rows = cursor.fetchall()
    conn.close()

    return [{"type": role, "message": message} for role, message in rows]


def get_all_users():

    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT phone_number,
               MAX(is_problem)
        FROM messages
        GROUP BY phone_number
        ORDER BY MAX(is_problem) DESC, MAX(timestamp) DESC
    """)

    users = cursor.fetchall()

    conn.close()

    return users


def is_duplicate_message(phone, message):

    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT message
        FROM messages
        WHERE phone_number=?
        ORDER BY timestamp DESC
        LIMIT 1
    """, (phone,))

    last = cursor.fetchone()
    conn.close()

    if last and last[0].strip().lower() == message.strip().lower():
        return True

    return False


def block_user(phone):
    cursor.execute("INSERT OR IGNORE INTO blocked_users (phone) VALUES (?)", (phone,))
    conn.commit()


def is_user_blocked(phone):
    cursor.execute("SELECT phone FROM blocked_users WHERE phone=?", (phone,))
    return cursor.fetchone() is not None