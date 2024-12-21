import sqlite3 as sq


# Create database connection
def create_connection():
    conn = sq.connect('health_data.db')
    return conn

# Create necessary tables
def create_tables():
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS health_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT,
            date TEXT,
            weight REAL,
            bp_systolic INTEGER,
            bp_diastolic INTEGER,
            glucose_level REAL,
            exercise_time INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# Insert health data
def insert_health_data(user_name, date, weight, bp_systolic, bp_diastolic, glucose_level, exercise_time):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO health_data (user_name,date, weight, bp_systolic, bp_diastolic, glucose_level, exercise_time)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', ( user_name, date, weight, bp_systolic, bp_diastolic, glucose_level, exercise_time))
    conn.commit()
    conn.close()

# Fetch health data for visualization
def fetch_health_data(user_name):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM health_data WHERE user_name = ? ORDER BY date ASC', (user_name,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def initialize_db():
    conn = sq.connect("auth.db")
    cursor = conn.cursor()
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def profiles_set():
    conn = sq.connect("profiles.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT,
            full_name TEXT,
            age INTEGER,
            gender TEXT,
            height REAL,
            weight REAL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

def fetch_user_info(user_name):
    """Fetch user personal information from the database."""
    conn = sq.connect("profiles.db")
    c = conn.cursor()
    c.execute("""
        SELECT full_name, age, gender, height, weight
        FROM profiles
        WHERE user_name = ?
    """, (user_name,))
    user_info = c.fetchone()  # Fetch one record
    conn.close()
    if user_info:
        return {
            "Full Name": user_info[0],
            "Age": user_info[1],
            "Gender": user_info[2],
            "Height (meters)": user_info[3],
            "Weight (kg)": user_info[4]
        }
    return None
create_tables()