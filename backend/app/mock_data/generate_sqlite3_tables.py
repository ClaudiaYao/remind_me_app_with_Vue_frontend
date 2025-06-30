import sqlite3
conn = sqlite3.connect("dev.sqlite3")
cursor = conn.cursor()

# Enable foreign key constraints
cursor.execute("PRAGMA foreign_keys = ON;")

# Create user_summary (must be created before user_remindee)
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_summary (
    user_id TEXT PRIMARY KEY,
    nick_name TEXT,
    description TEXT,
    age INTEGER,
    phone_number TEXT,
    avatar_object_key TEXT
);
""")

# Create user_remindee with foreign key
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_remindee (
    remindee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    image_object_key TEXT NOT NULL,
    person_name TEXT NOT NULL,
    summary TEXT,
    relationship TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user_summary(user_id) ON DELETE CASCADE
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS remindee_summary (
    user_id TEXT NOT NULL,
    person_name TEXT NOT NULL,
    summary TEXT NOT NULL,
    FOREIGN KEY (user_id, person_name)
        REFERENCES user_remindee(user_id, person_name)
        ON DELETE CASCADE,
    PRIMARY KEY (user_id, person_name)
);
""")

conn.commit()
conn.close()
