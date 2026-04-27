import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "missing_persons.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()

    # Persons table - NOW INCLUDES EMAIL
    c.execute("""
        CREATE TABLE IF NOT EXISTS persons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age TEXT,
            gender TEXT,
            height TEXT,
            weight TEXT,
            image_filename TEXT,
            encoding_json TEXT,
            phone TEXT,
            email TEXT
        )
    """)

    # Sightings table
    c.execute("""
        CREATE TABLE IF NOT EXISTS sightings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER,
            image_filename TEXT,
            latitude TEXT,
            longitude TEXT,
            sms_status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(person_id) REFERENCES persons(id)
        )
    """)

    conn.commit()
    conn.close()

def add_person(name, age, gender, height, weight, image_filename, face_encoding, phone, email):
    conn = get_db_connection()
    c = conn.cursor()
    encoding_json = json.dumps(face_encoding) if face_encoding else None
    c.execute("""
        INSERT INTO persons (name, age, gender, height, weight, image_filename, encoding_json, phone, email)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, age, gender, height, weight, image_filename, encoding_json, phone, email))
    conn.commit()
    conn.close()

def get_all_persons():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM persons")
    rows = c.fetchall()
    conn.close()

    persons =[]
    for row in rows:
        encoding = None
        if row["encoding_json"]:
            try:
                encoding = json.loads(row["encoding_json"])
            except Exception:
                encoding = None
        persons.append({
            "id": row["id"],
            "name": row["name"],
            "age": row["age"],
            "gender": row["gender"],
            "height": row["height"],
            "weight": row["weight"],
            "image_filename": row["image_filename"],
            "face_encoding": encoding,
            "phone": row["phone"],
            "email": row["email"]
        })
    return persons

def log_sighting(person_id, image_filename, latitude, longitude, sms_status):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO sightings (person_id, image_filename, latitude, longitude, sms_status)
        VALUES (?, ?, ?, ?, ?)
    """, (person_id, image_filename, latitude, longitude, sms_status))
    conn.commit()
    conn.close()