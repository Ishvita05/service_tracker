import sqlite3
import os
from datetime import datetime

# Connect to the SQLite database
db_path = os.path.abspath("data.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# ---------------- Function to raise a ticket ----------------
def raise_ticket():
    print("\n🎫 Raise a New Ticket")

    user_id = int(input("Enter your user ID: "))
    department = input("Department (IT/Library/Hostel): ")
    category = input("Issue Category (e.g., Internet, Fan, Mess): ")
    description = input("Describe the issue: ")
    priority = input("Priority (Low/Medium/High): ")
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO tickets (user_id, department, category, description, priority, status, created_at)
        VALUES (?, ?, ?, ?, ?, 'New', ?)
    """, (user_id, department, category, description, priority, created_at))

    conn.commit()
    print("✅ Ticket submitted successfully!\n")

# ---------------- Function to view all tickets ----------------
def view_tickets():
    print("\n📋 All Tickets:")
    cursor.execute("SELECT * FROM tickets")
    for row in cursor.fetchall():
        print(row)
def assign_ticket():
    print("\n🛠️ Assign a Ticket")

    # Step 1: Show unassigned tickets
    cursor.execute("SELECT * FROM tickets WHERE status = 'New'")
    new_tickets = cursor.fetchall()

    if not new_tickets:
        print("No new tickets to assign.")
        return

    print("\n📋 Unassigned Tickets:")
    for t in new_tickets:
        print(f"Ticket ID: {t[0]}, User ID: {t[1]}, Dept: {t[2]}, Desc: {t[4]}")

    try:
        ticket_id = int(input("\nEnter the Ticket ID to assign: "))
        support_id = int(input("Enter Support Staff User ID: "))
        admin_id = int(input("Enter Your (Admin) User ID: "))

        # Step 2: Update the ticket
        cursor.execute("""
            UPDATE tickets
            SET assigned_to = ?, status = 'Assigned'
            WHERE ticket_id = ? AND status = 'New'
        """, (support_id, ticket_id))

        # Step 3: Add entry in logs
        cursor.execute("""
            INSERT INTO logs (action, user_id, ticket_id)
            VALUES (?, ?, ?)
        """, ("Assigned ticket", admin_id, ticket_id))

        conn.commit()
        print(f"✅ Ticket {ticket_id} assigned to Support Staff ID {support_id}.")

    except Exception as e:
        print(f"❌ Error: {e}")

from textblob import TextBlob

def resolve_ticket():
    print("\n✅ Resolve a Ticket")

    # Show assigned tickets
    cursor.execute("SELECT * FROM tickets WHERE status = 'Assigned'")
    assigned = cursor.fetchall()

    if not assigned:
        print("No assigned tickets to resolve.")
        return

    print("\n📋 Assigned Tickets:")
    for t in assigned:
        print(f"Ticket ID: {t[0]}, Assigned To: {t[8]}, Desc: {t[4]}")

    try:
        ticket_id = int(input("\nEnter Ticket ID to mark as resolved: "))
        user_id = int(input("Enter your (support staff) user ID: "))
        resolved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Update ticket status
        cursor.execute("""
            UPDATE tickets
            SET status = 'Resolved', resolved_at = ?
            WHERE ticket_id = ? AND assigned_to = ?
        """, (resolved_at, ticket_id, user_id))

        # Add log entry
        cursor.execute("""
            INSERT INTO logs (action, user_id, ticket_id)
            VALUES (?, ?, ?)
        """, ("Resolved ticket", user_id, ticket_id))

        # Collect feedback from user
        print("\n📝 Ask the user for feedback...")
        rating = int(input("Rating (1 to 5): "))
        comment = input("Feedback Comment: ")
        sentiment = TextBlob(comment).sentiment.polarity

        if sentiment > 0.2:
            sentiment_label = "Positive"
        elif sentiment < -0.2:
            sentiment_label = "Negative"
        else:
            sentiment_label = "Neutral"

        cursor.execute("""
            INSERT INTO feedback (ticket_id, user_id, rating, comment, sentiment)
            VALUES (?, ?, ?, ?, ?)
        """, (ticket_id, user_id, rating, comment, sentiment_label))

        conn.commit()
        print(f"🎉 Ticket {ticket_id} resolved with feedback: {sentiment_label}")

    except Exception as e:
        print(f"❌ Error: {e}")


# ---------------- Menu loop ----------------
while True:
    print("\n--- Service Tracker Menu ---")
    print("1. Raise Ticket")
    print("2. View All Tickets")
    print("3. Assign Ticket")  # new
    print("4. Resolve Ticket")  # new
    print("5. Exit")            

    choice = input("Enter your choice: ")

    if choice == "1":
        raise_ticket()
    elif choice == "2":
        view_tickets()
    elif choice == "3":
        assign_ticket()
    elif choice == "4":
        resolve_ticket()
    elif choice == "5":
        print("Exiting... 👋")
        break
    else:
        print("Invalid choice. Try again.")

# Close DB connection
conn.close()
