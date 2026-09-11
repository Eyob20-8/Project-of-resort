from flask import Flask, render_template,request, redirect,flash, url_for,session,jsonify
import sqlite3,re
from werkzeug.security import generate_password_hash
app = Flask(__name__)
app.secret_key = "mekdem_resort_secret_key_2026" 
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# Create tables
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fullname TEXT  NOT NULL,
        Room_number INTERGER,
        email TEXT NOT NULL,
        Room_type TEXT NOT NULL,
        checkin TEXT NOT NULL,
        checkout TEXT NOT NULL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Records(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            USER_ID INTEGER,
            fullname TEXT ,
            email TEXT,
            room_number INTEGER ,
            room_type TEXT NOT NULL,
            FOREIGN KEY (USER_ID) REFERENCES users(id)          
        )
        """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Room(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Room_No INTEGER NOT NULL,
        Room_type TEXT NOT NULL,
        price REAL NOT NULL,
        status TEXT DEFAULT 'available'
    )
    """)
    cursor.execute("SELECT * FROM Room")
    existing_rooms = cursor.fetchall()
    if len(existing_rooms)<100:
        for i in range(1,101):
             Room_No=100+i
             if i<=40:
                 Room_type="Single"
                 price=1000
             elif i<=80:
                 Room_type="Double"
                 price=1500
             else:
                 Room_type="Deluxe"
                 price=3000
                 cursor.execute("""
                 INSERT OR IGNORE INTO Room
                (Room_No,Room_type,price)
                 VALUES (?,?,?)""",(Room_No,Room_type,price)
                )
    conn.commit()
    conn.close()

init_db()

# Home page
@app.route("/")
def home():
    return render_template("login.html")


# Registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]
        if not email or not re.match(EMAIL_REGEX, email):
                        flash("Invalid email address format!", "error")
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        try:
            
            cursor.execute(
                        "SELECT * FROM users WHERE username=? AND email=?",
                        (username, email)
                    )
            
            customer = cursor.fetchone()
            if customer:
                if customer[1] == username: # Assuming username is index 1
                    flash("Username already exists.", "error")
                else:
                    flash("Email already registered.", "error")
            else:
                cursor.execute(
            "INSERT INTO users(username,email,password) VALUES(?,?,?)",
            (username, email, password)
        )
            conn.commit()
            flash(f"{username},welcome")
        except sqlite3.IntegrityError:            
            return "Username already exists!"
        finally:
            conn.close()
        return redirect("/login")

    return render_template("register.html")


# Login
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            # ---> SAVE USER DATA TO SESSION HERE <---
            session["user_id"] = user[0]
            session["username"] = user[1]
            session["email"] = user[2]
            
            return redirect("/Dashboard")
        else:
            flash("Invalid Username or password")

    return render_template("login.html")


# Booking
@app.route("/booking", methods=["GET", "POST"])
def booking():
    if request.method == "POST":
        fullname = request.form["fullname"]
        email = request.form["email"]
        Room_type=request.form["room_type"]
        checkin = request.form["checkin"]
        checkout = request.form["checkout"]

        conn = sqlite3.connect("users.db")
        cursor=conn.cursor()
        cursor.execute(
            "SELECT Room_No FROM Room WHERE status='available'AND Room_type=? LIMIT 1",
            (Room_type,)
                       )
        Room_data=cursor.fetchone()
        if not Room_data:
            conn.close()
            flash(f"No available room for:{Room_type}")
            return redirect(url_for("booking"))
        room_no=Room_data[0]     
        try:
             cursor.execute(
                 "INSERT INTO bookings(fullname,Room_number,Room_type,email, checkin, checkout) VALUES(?,?,?,?,?,?)",
                 (fullname,room_no,Room_type,email, checkin, checkout)
             )
             cursor.execute(
                "UPDATE Room SET status='booked' WHERE Room_No=?", 
                (room_no,)
            )
             conn.commit()
             conn.close()
             flash(f'Room:{room_no},{fullname}')
             return redirect(url_for("Dashboard"))
        except Exception as e:
                    return f"Database error: {str(e)}", 500
        finally:
            conn.close()

    return render_template("book.html")
@app.route("/Dashboard",methods=["GET","POST"])
def Dashboard():
    return render_template("Dashboard.html")
@app.route('/gallery',methods=['GET'])
def gallery():
    return render_template('Gallery.html')
@app.route('/leave', methods=['GET','POST'])
def checkout():
     if request.method == 'GET':
        return render_template('checkout.html')

    # POST Request: Process the form submission data
     try:
        data = request.get_json()
        username = data.get('user')
        room_raw = data.get('Room')
        rating_value = data.get('rating')

        try:
            room = int(room_raw)
        except (ValueError, TypeError):
            return jsonify({"status": "error", "message": "Room number must be a valid number."}), 400

        # One database session handles everything sequentially
        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            
            # 1. Verify user booking
            cursor.execute("SELECT fullname FROM bookings WHERE fullname=? AND Room_number=? LIMIT 1", (username, room))
            user = cursor.fetchone()
            
            if user:
                print(f"Processing checkout - User: {username}, Room: {room}, Rating: {rating_value}/10")
                
                # 2. Archive the record into historical logs
                cursor.execute("""
                    INSERT INTO Records (user_id, fullname, email, room_number, room_type) 
                    SELECT users.id, bookings.fullname, bookings.email, bookings.Room_number, bookings.Room_type 
                    FROM bookings 
                    INNER JOIN users ON bookings.email = users.email
                    WHERE bookings.fullname = ? AND bookings.Room_number = ?;
                """, (username, room))
                cursor.execute("DELETE FROM bookings WHERE fullname = ?;", (username,))

                # 3. Update room status to available
                cursor.execute("UPDATE Room SET status='available' WHERE Room_No=?", (room,))
                conn.commit()
                
                # Success: Send back a clear confirmation to JavaScript
                return jsonify({
                    "status": "success", 
                    "message": "Checkout completed successfully."
                }), 200
            else:
                print(f"Booking not found for {username}")
                return jsonify({"status": "error", "message": "No matching booking found."}), 404

     except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
@app.route('/history', methods=['GET'])
def history():
    # Check if the user is logged in
    if "user_id" not in session:
        flash("Please log in to view your history.")
        return redirect(url_for("login"))
    
    # Get active customer's id from session
    current_user_id = session["user_id"]

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # Query only the history belonging to this user
    cursor.execute("""
        SELECT room_number, room_type, fullname, email 
        FROM Records 
        WHERE USER_ID = ?
    """, (current_user_id,))
    
    user_records = cursor.fetchall()
    conn.close()

    # Pass the records array into your HTML template
    return render_template('History.html', records=user_records)
@app.route('/profile', methods=['GET','POST'])
def profile():
    if "user_id" in session:
        return render_template('profile.html') 
    
    return "User does not exist. Please log in."

if __name__ == "__main__":
    app.run(port=8000,debug=True)