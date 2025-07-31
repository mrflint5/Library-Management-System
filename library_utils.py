import sqlite3
import bcrypt
import datetime
import openpyxl

def connect_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY,
        title TEXT,
        author TEXT,
        available INTEGER
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY,
        name TEXT,
        issued_book_id INTEGER,
        issue_date TEXT
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS admin (
        username TEXT PRIMARY KEY,
        password BLOB
    )''')

    cur.execute("SELECT * FROM admin WHERE username='admin'")
    if not cur.fetchone():
        password = bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt())
        cur.execute("INSERT INTO admin (username, password) VALUES (?, ?)", ('admin', password))

    conn.commit()
    conn.close()

def login_admin(username, password):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT password FROM admin WHERE username=?", (username,))
    result = cur.fetchone()
    conn.close()
    return result and bcrypt.checkpw(password.encode(), result[0])

def register_admin(username, password):
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO admin (username, password) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def add_book(title, author):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO books (title, author, available) VALUES (?, ?, 1)", (title, author))
    conn.commit()
    conn.close()

def get_books():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM books")
    books = cur.fetchall()
    conn.close()
    return books

def add_student(name):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO students (name, issued_book_id, issue_date) VALUES (?, NULL, NULL)", (name,))
    conn.commit()
    conn.close()

def get_students():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM students")
    students = cur.fetchall()
    conn.close()
    return students

def issue_book(book_id, student_id):
    today = datetime.date.today().isoformat()
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT available FROM books WHERE id=?", (book_id,))
    if cur.fetchone()[0] == 1:
        cur.execute("UPDATE books SET available=0 WHERE id=?", (book_id,))
        cur.execute("UPDATE students SET issued_book_id=?, issue_date=? WHERE id=?", (book_id, today, student_id))
        conn.commit()
        conn.close()
        return f"✅ Issued on {today}"
    else:
        return "❌ Book not available"

def return_book(student_id):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT issued_book_id, issue_date FROM students WHERE id=?", (student_id,))
    result = cur.fetchone()
    if result and result[0]:
        book_id, issue_date = result
        cur.execute("UPDATE books SET available=1 WHERE id=?", (book_id,))
        cur.execute("UPDATE students SET issued_book_id=NULL, issue_date=NULL WHERE id=?", (student_id,))
        conn.commit()

        issue_date = datetime.datetime.strptime(issue_date, "%Y-%m-%d").date()
        today = datetime.date.today()
        days = (today - issue_date).days
        fine = max(0, (days - 7) * 5)
        conn.close()
        return f"✅ Returned in {days} days. Fine: ₹{fine}"
    else:
        return "❌ No book issued"

def export_data():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    wb = openpyxl.Workbook()
    ws1 = wb.active
    ws1.title = "Books"
    ws1.append(["ID", "Title", "Author", "Available"])
    for row in cur.execute("SELECT * FROM books"):
        ws1.append(row)
    ws2 = wb.create_sheet(title="Students")
    ws2.append(["ID", "Name", "Issued Book ID", "Issue Date"])
    for row in cur.execute("SELECT * FROM students"):
        ws2.append(row)
    wb.save("Library_Data.xlsx")
    conn.close()
    return "✅ Exported to Library_Data.xlsx"

