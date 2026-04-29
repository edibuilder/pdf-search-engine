import sqlite3
import bcrypt

DB_NAME = "pdf_search.db"

def init_database():
    """Създава таблиците при първо стартиране"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Таблица за потребителите
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # Таблица за индекса на PDF (засега празна, ще я разширим после)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pdf_index (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            page_number INTEGER,
            word TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Базата данни е инициализирана.")

def hash_password(password):
    """Хешира парола с bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, password_hash):
    """Проверява дали паролата съвпада с хеша"""
    return bcrypt.checkpw(password.encode(), password_hash.encode())

def register_user(username, password):
    """Регистрира нов потребител"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        password_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash)
        )
        conn.commit()
        conn.close()
        return True, "Регистрацията е успешна!"
    except sqlite3.IntegrityError:
        return False, "Потребителското име вече съществува."
    except Exception as e:
        return False, f"Грешка: {e}"

def login_user(username, password):
    """Проверява дали потребителят съществува и паролата е вярна"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT password_hash FROM users WHERE username = ?",
        (username,)
    )
    result = cursor.fetchone()
    conn.close()
    
    if result and check_password(password, result[0]):
        return True, "Успешен вход!"
    return False, "Грешно потребителско име или парола."

# ========== НОВИ ФУНКЦИИ ЗА PDF ИНДЕКСА ==========

def get_user_id(username):
    """Връща ID на потребител по username"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def clear_user_index(user_id):
    """Изчиства целия индекс на даден потребител"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pdf_index WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def add_word_to_index(user_id, filename, page_number, word):
    """Добавя една дума в индекса"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pdf_index (user_id, filename, page_number, word)
        VALUES (?, ?, ?, ?)
    """, (user_id, filename, page_number, word))
    conn.commit()
    conn.close()

def search_words(user_id, search_term):
    """
    Търси дадена дума в индекса на потребителя.
    Връща списък от tuples: (filename, page_number)
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Търси точна дума или дума, която започва с търсения термин
    cursor.execute("""
        SELECT DISTINCT filename, page_number 
        FROM pdf_index 
        WHERE user_id = ? AND word LIKE ?
        ORDER BY filename, page_number
    """, (user_id, f"%{search_term.lower()}%"))
    
    results = cursor.fetchall()
    conn.close()
    return results

def get_user_files(user_id):
    """Връща списък с уникалните файлове, индексирани от потребителя"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT filename 
        FROM pdf_index 
        WHERE user_id = ?
        ORDER BY filename
    """, (user_id,))
    results = [row[0] for row in cursor.fetchall()]
    conn.close()
    return results

def delete_file_from_index(user_id, filename):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Първо проверяваме колко записа ще се изтрият
    cursor.execute(
        "SELECT COUNT(*) FROM pdf_index WHERE user_id = ? AND filename = ?",
        (user_id, filename)
    )
    count = cursor.fetchone()[0]
    
    if count == 0:
        conn.close()
        return False, 0, f"Файлът '{filename}' не е намерен в индекса."
    
    # Изтриваме записите
    cursor.execute(
        "DELETE FROM pdf_index WHERE user_id = ? AND filename = ?",
        (user_id, filename)
    )
    conn.commit()
    conn.close()
    
    return True, count, f"Успешно изтрит файл '{filename}' ({count} записа)."