import sqlite3

# =====================================================
# INIT DATABASE
# =====================================================
def init_db():

    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()

    # ================= CHAT MESSAGES =================
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

    # ================= BLOCKED USERS =================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blocked_users (
            phone TEXT PRIMARY KEY
        )
    """)

    # ================= AI MEMORY =================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT,
            memory_key TEXT,
            memory_value TEXT
        )
    """)

    conn.commit()
    conn.close()

# =====================================================
# SAVE MESSAGE
# =====================================================
def save_message(phone_number, role, message):

    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO messages (phone_number, role, message) VALUES (?, ?, ?)",
        (phone_number, role, message)
    )

    conn.commit()
    conn.close()

# =====================================================
# GET CHAT HISTORY
# =====================================================
def get_chat_history(phone_number):

    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT role, message
        FROM messages
        WHERE phone_number=?
        ORDER BY timestamp ASC
        """,
        (phone_number,)
    )

    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "type": role,
            "message": message
        }
        for role, message in rows
    ]

# =====================================================
# GET ALL USERS
# =====================================================
def get_all_users():

    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT phone_number,
               MAX(is_problem)
        FROM messages
        GROUP BY phone_number
        ORDER BY MAX(timestamp) DESC
    """)

    users = cursor.fetchall()

    conn.close()

    return users

# =====================================================
# DUPLICATE MESSAGE CHECK
# =====================================================
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

# =====================================================
# BLOCK USER
# =====================================================
def block_user(phone):

    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO blocked_users (phone) VALUES (?)",
        (phone,)
    )

    conn.commit()
    conn.close()

# =====================================================
# CHECK BLOCKED USER
# =====================================================
def is_user_blocked(phone):

    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT phone FROM blocked_users WHERE phone=?",
        (phone,)
    )

    result = cursor.fetchone()

    conn.close()

    return result is not None

# =====================================================
# SAVE AI MEMORY
# =====================================================
def save_user_memory(phone, key, value):

    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO user_memory
        (phone, memory_key, memory_value)
        VALUES (?, ?, ?)
    """, (phone, key, value))

    conn.commit()
    conn.close()

# =====================================================
# GET AI MEMORY
# =====================================================
def get_user_memory(phone, key):

    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT memory_value
        FROM user_memory
        WHERE phone=? AND memory_key=?
        ORDER BY id DESC
        LIMIT 1
    """, (phone, key))

    row = cursor.fetchone()

    conn.close()

    if row:
        return row[0]

    return None