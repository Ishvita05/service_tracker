import sqlite3
import os

# DELETE existing corrupted DB if it exists
try:
    os.remove("data.db")
    print("🗑️ Old data.db deleted.")
except FileNotFoundError:
    pass

# Now recreate DB
conn = sqlite3.connect("data.db")
cursor = conn.cursor()

# Create schema
cursor.executescript("""
CREATE TABLE IF NOT EXISTS users (
  user_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  role TEXT CHECK(role IN ('user', 'support', 'admin')),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tickets (
  ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  department TEXT,
  category TEXT,
  description TEXT,
  priority TEXT CHECK(priority IN ('Low', 'Medium', 'High')),
  status TEXT CHECK(status IN ('New', 'Assigned', 'Resolved', 'Escalated')),
  assigned_to INTEGER,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  resolved_at DATETIME,
  FOREIGN KEY(user_id) REFERENCES users(user_id),
  FOREIGN KEY(assigned_to) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS feedback (
  feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
  ticket_id INTEGER,
  user_id INTEGER,
  rating INTEGER CHECK(rating >= 1 AND rating <= 5),
  comment TEXT,
  sentiment TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(ticket_id) REFERENCES tickets(ticket_id),
  FOREIGN KEY(user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS logs (
  log_id INTEGER PRIMARY KEY AUTOINCREMENT,
  action TEXT,
  user_id INTEGER,
  ticket_id INTEGER,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(user_id) REFERENCES users(user_id),
  FOREIGN KEY(ticket_id) REFERENCES tickets(ticket_id)
);
""")

# Add sample users
cursor.execute("INSERT INTO users (name, email, role) VALUES ('Ishvita Sharma', 'ishvita@example.com', 'user')")
cursor.execute("INSERT INTO users (name, email, role) VALUES ('Rohit Mehra', 'rohit@example.com', 'support')")
cursor.execute("INSERT INTO users (name, email, role) VALUES ('Sneha Arora', 'sneha@example.com', 'admin')")

conn.commit()
conn.close()

print("✅ data.db created successfully with all tables and 3 sample users.")
