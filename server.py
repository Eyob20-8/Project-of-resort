from flask import (
    Flask, render_template, request, redirect,
    flash, url_for, session, jsonify
)
import sqlite3
import re
import os
from uuid import uuid4
import uuid
from functools import wraps
from dotenv import load_dotenv

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename


load_dotenv()

app = Flask(__name__)

# ---------------------------------------------------------
# APP CONFIGURATION
# ---------------------------------------------------------
CHAPA_SECRET_KEY = os.getenv("CHAPA_SECRET_KEY")
CHAPA_BASE_URL = os.getenv(
    "CHAPA_BASE_URL",
    "https://api.chapa.global/v2"
)

app.secret_key = os.getenv("FLASK_SECRET_KEY")
if not app.secret_key:
    raise RuntimeError("FLASK_SECRET_KEY is missing. Add it to your .env file.")

DATABASE = "users.db"
UPLOAD_FOLDER = os.path.join("static", "uploads")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

ALLOWED_IMAGE_EXTENSIONS = {
    "png", "jpg", "jpeg", "gif", "webp"
}


# ---------------------------------------------------------
# DATABASE HELPERS
# ---------------------------------------------------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            profile_image TEXT,
            fan_number INTEGER
        )
    """)

    # Bookings
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            Room_number INTEGER NOT NULL,
            email TEXT NOT NULL,
            Room_type TEXT NOT NULL,
            checkin TEXT NOT NULL,
            checkout TEXT NOT NULL
        )
    """)

    # Previous bookings / checkout history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            USER_ID INTEGER,
            fullname TEXT,
            email TEXT,
            room_number INTEGER,
            room_type TEXT NOT NULL,
            FOREIGN KEY (USER_ID) REFERENCES users(id)
        )
    """)
    cursor.execute("""
         CREATE TABLE IF NOT EXISTS admin (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             username TEXT NOT NULL UNIQUE,
             email TEXT NOT NULL UNIQUE,
             password TEXT NOT NULL
         )
    """)

    # Rooms
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Room (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Room_No INTEGER NOT NULL UNIQUE,
            Room_type TEXT NOT NULL,
            price REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'available'
        )
    """)

    # -----------------------------------------------------
    # Create 100 rooms if they do not already exist.
    # This fixes the indentation problem in the old code.
    # -----------------------------------------------------

    for i in range(1, 101):

        room_no = 100 + i

        if i <= 40:
            room_type = "Single"
            price = 1000

        elif i <= 80:
            room_type = "Double"
            price = 1500

        else:
            room_type = "Deluxe"
            price = 3000

        cursor.execute("""
            INSERT OR IGNORE INTO Room
            (Room_No, Room_type, price, status)
            VALUES (?, ?, ?, 'available')
        """, (room_no, room_type, price))


    conn.commit()
    conn.close()


init_db()


# ---------------------------------------------------------
# UTILITY FUNCTIONS
# ---------------------------------------------------------

def allowed_image(filename):
    if "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()
    return extension in ALLOWED_IMAGE_EXTENSIONS


def get_logged_in_user():
    """Return the currently logged-in user or None."""
    user_id = session.get("user_id")

    if not user_id:
        return None

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()
    conn.close()

    return user

from functools import wraps
from flask import session, redirect, url_for, request, jsonify

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):

        # Check whether the user is logged in
        if "user_id" not in session:

            # API request
            if request.path.startswith("/api/"):
                return jsonify({
                    "success": False,
                    "message": "Please log in first."
                }), 401

            # Normal browser request
            flash("Please log in first.", "error")
            return redirect(url_for("login"))

        return view(*args, **kwargs)

    return wrapped_view


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            if request.path.startswith("/api/"):
                return jsonify({
                    "success": False,
                    "message": "Authentication required."
                }), 401

            return redirect(url_for("login"))

        if session.get("role") != "admin":
            if request.path.startswith("/api/"):
                return jsonify({
                    "success": False,
                    "message": "Administrator access required."
                }), 403

            return "Forbidden: administrator access required.", 403

        return view(*args, **kwargs)

    return wrapped_view
# ---------------------------------------------------------
# HOME
# ---------------------------------------------------------

@app.route("/")
def home():
    session.clear()
    return render_template("login.html")


# ---------------------------------------------------------
# REGISTER
# ---------------------------------------------------------


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        fullname = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not fullname:
            flash("Username is required.", "error")
            return redirect(url_for("register"))

        if not email or not re.match(EMAIL_REGEX, email):
            flash("Invalid email address format.", "error")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash("Password must contain at least 6 characters.", "error")
            return redirect(url_for("register"))

        conn = get_db()

        try:
            existing = conn.execute("""
                SELECT id
                FROM users
                WHERE username = ? OR email = ?
            """, (fullname, email)).fetchone()

            if existing:
                flash("Username or email already exists.", "error")
                return redirect(url_for("register"))

            hashed_password = generate_password_hash(password)

            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO users (
                    username,
                    fullname,
                    email,
                    password,
                    fan_number,
                    profile_image
                )
                VALUES (?,?, ?, ?, ?, ?)
            """, (
                "",
                fullname,
                email,
                hashed_password,
                0,
                "default.png"
            ))

            # Get the newly generated database ID
            user_id = cursor.lastrowid

            # Generate the public user ID
            custom_id = f"USR/{4560 + user_id}/19"

            cursor.execute("""
                UPDATE users
                SET username = ?
                WHERE id = ?
            """, (custom_id, user_id))

            conn.commit()

            flash(f"{fullname}, welcome!", "success")
            return redirect(url_for("login"))

        except sqlite3.Error as e:
            conn.rollback()
            return f"Database error: {e}", 500

        finally:
            conn.close()

    return render_template("register.html")

# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    conn=get_db()
    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = conn.execute("""
        SELECT id, username, email, password, 'user' AS role
        FROM users
        WHERE username = ?

        UNION ALL

        SELECT id, username, email, password, 'admin' AS role
        FROM admin
        WHERE username = ?
         """,(username, username)).fetchone()
        if user and check_password_hash(user["password"], password):

            session.clear()

            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["email"] = user["email"]
            session["role"] = user["role"]

            if user["role"] == "admin":
                 return redirect(url_for("admin_dashboard"))
            return redirect(url_for("Dashboard"))
        flash("Invalid username or password.", "error")

    return render_template("login.html")


# ---------------------------------------------------------
# LOGOUT
# ---------------------------------------------------------

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("login"))


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------

@app.route("/Dashboard", methods=["GET"])
@login_required
def Dashboard():

    
    user = get_logged_in_user()

    if not user:
        session.clear()
        return redirect(url_for("login"))

    return render_template(
        "Dashboard.html",
        user=user
    )


# ---------------------------------------------------------
# PROFILE
# ---------------------------------------------------------

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    
    user_id = session["user_id"]

    # -----------------------------------------------------
    # GET: Display current user's profile
    # -----------------------------------------------------

    if request.method == "GET":

        conn = get_db()

        user = conn.execute("""
            SELECT id, username, email, profile_image, fan_number
            FROM users
            WHERE id = ?
        """, (user_id,)).fetchone()

        conn.close()

        if not user:
            session.clear()
            return redirect(url_for("login"))

        return render_template(
            "profile.html",
            user=user
        )

    # -----------------------------------------------------
    # POST: Update profile information
    # -----------------------------------------------------

    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    fan_number = request.form.get("id", "").strip()

    if not username:
        return jsonify({
            "status": "error",
            "message": "Username is required."
        }), 400

    if not email or not re.match(EMAIL_REGEX, email):
        return jsonify({
            "status": "error",
            "message": "Invalid email address."
        }), 400

    if fan_number:
        try:
            fan_number = int(fan_number)
        except ValueError:
            return jsonify({
                "status": "error",
                "message": "FAN Number must be a number."
            }), 400
    else:
        fan_number = None

    conn = get_db()

    try:

        # Check whether another account already uses this email.
        duplicate = conn.execute("""
            SELECT id
            FROM users
            WHERE email = ? AND id != ?
        """, (email, user_id)).fetchone()

        if duplicate:
            return jsonify({
                "status": "error",
                "message": "That email is already registered."
            }), 409

        # -------------------------------------------------
        # IMAGE UPLOAD
        # -------------------------------------------------

        file = request.files.get("file")
        image_path = None

        if file and file.filename:

            if not allowed_image(file.filename):
                return jsonify({
                    "status": "error",
                    "message": "Only PNG, JPG, JPEG, GIF and WEBP images are allowed."
                }), 400

            original_name = secure_filename(file.filename)

            # Unique filename prevents two users from overwriting
            # each other's profile pictures.
            extension = original_name.rsplit(".", 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{extension}"

            full_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )

            file.save(full_path)

            # Store a path relative to /static.
            # Example: uploads/abc123.jpg
            image_path = f"uploads/{filename}"

        # -------------------------------------------------
        # UPDATE DATABASE
        # -------------------------------------------------

        if password:

            if len(password) < 6:
                return jsonify({
                    "status": "error",
                    "message": "Password must contain at least 6 characters."
                }), 400

            hashed_password = generate_password_hash(password)

            if image_path:
                conn.execute("""
                    UPDATE users
                    SET username = ?,
                        email = ?,
                        password = ?,
                        fan_number = ?,
                        profile_image = ?
                    WHERE id = ?
                """, (
                    username,
                    email,
                    hashed_password,
                    fan_number,
                    image_path,
                    user_id
                ))
            else:
                conn.execute("""
                    UPDATE users
                    SET username = ?,
                        email = ?,
                        password = ?,
                        fan_number = ?
                    WHERE id = ?
                """, (
                    username,
                    email,
                    hashed_password,
                    fan_number,
                    user_id
                ))

        else:

            if image_path:
                conn.execute("""
                    UPDATE users
                    SET username = ?,
                        email = ?,
                        fan_number = ?,
                        profile_image = ?
                    WHERE id = ?
                """, (
                    username,
                    email,
                    fan_number,
                    image_path,
                    user_id
                ))
            else:
                conn.execute("""
                    UPDATE users
                    SET username = ?,
                        email = ?,
                        fan_number = ?
                    WHERE id = ?
                """, (
                    username,
                    email,
                    fan_number,
                    user_id
                ))

        conn.commit()

        # Keep session information synchronized.
        session["username"] = username
        session["email"] = email

        return jsonify({
            "status": "success",
            "message": "Profile updated successfully.",
            "profile_image": image_path
        })

    except sqlite3.IntegrityError:
        conn.rollback()

        return jsonify({
            "status": "error",
            "message": "That email is already registered."
        }), 409

    except Exception as e:
        conn.rollback()

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        conn.close()


# ---------------------------------------------------------
# OPTIONAL /upload ROUTE
#
# This allows your separate uploadForm in profile.html
# to upload an image independently using JavaScript.
# ---------------------------------------------------------

@app.route("/upload", methods=["POST"])
@login_required
def upload():

    if not login_required():
        return jsonify({
            "status": "error",
            "message": "Please log in first."
        }), 401

    file = request.files.get("file")

    if not file or not file.filename:
        return jsonify({
            "status": "error",
            "message": "No image was selected."
        }), 400

    if not allowed_image(file.filename):
        return jsonify({
            "status": "error",
            "message": "Invalid image type."
        }), 400

    original_name = secure_filename(file.filename)
    extension = original_name.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{extension}"

    full_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    file.save(full_path)

    image_path = f"uploads/{filename}"

    conn = get_db()

    try:
        conn.execute("""
            UPDATE users
            SET profile_image = ?
            WHERE id = ?
        """, (image_path, session["user_id"]))

        conn.commit()

        return jsonify({
            "status": "success",
            "message": "Profile image uploaded successfully.",
            "profile_image": image_path,
            "url": url_for("static", filename=image_path)
        })

    except Exception as e:
        conn.rollback()

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        conn.close()


# ---------------------------------------------------------
# BOOKING
# ---------------------------------------------------------

@app.route("/booking", methods=["GET", "POST"])
@login_required
def booking():

    if request.method == "POST":

        fullname = request.form.get("fullname", "").strip()
        email = request.form.get("email", "").strip().lower()
        room_type = request.form.get("room_type", "").strip()
        checkin = request.form.get("checkin", "")
        checkout = request.form.get("checkout", "")

        if not all([
            fullname,
            email,
            room_type,
            checkin,
            checkout
        ]):
            flash("Please fill in all booking fields.")
            return redirect(url_for("booking"))

        conn = get_db()

        try:

            room = conn.execute("""
                SELECT Room_No
                FROM Room
                WHERE status = 'available'
                AND Room_type = ?
                LIMIT 1
            """, (room_type,)).fetchone()

            if not room:
                flash(f"No available room for {room_type}.")
                return redirect(url_for("booking"))

            room_no = room["Room_No"]

            conn.execute("""
                INSERT INTO bookings
                (fullname, Room_number, email, Room_type, checkin, checkout)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                fullname,
                room_no,
                email,
                room_type,
                checkin,
                checkout
            ))

            conn.execute("""
                UPDATE Room
                SET status = 'booked'
                WHERE Room_No = ?
            """, (room_no,))

            conn.commit()

            flash(f"Room {room_no} has been booked for {fullname}.")
            return redirect(url_for("Dashboard"))

        except sqlite3.Error as e:
            conn.rollback()
            return f"Database error: {e}", 500

        finally:
            conn.close()

    return render_template("book.html")

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    return render_template("admin_dashboard.html")

@app.route("/admin/panel")
@admin_required
def admin_panel():
    return render_template ("panel.html")

@app.route("/admin/users",methods=["GET"])
@admin_required
def admin_users():
    return render_template ("user.html")
@app.route("/admin/check_gallery",methods=["GET"])
@admin_required
def check_gallery():
    return render_template("cost.html")

# Get all users for the admin user-management table
@app.route("/api/admin/users", methods=["GET"])
@admin_required
def api_admin_users():
    db = get_db()

    try:
        # Check the current users table structure
        columns = {
            row["name"]
            for row in db.execute("PRAGMA table_info(users)").fetchall()
        }

        if not columns:
            return jsonify({
                "success": False,
                "message": "The users table does not exist."
            }), 500

        # Add missing columns for older databases
        if "role" not in columns:
            db.execute("""
                ALTER TABLE users
                ADD COLUMN role TEXT NOT NULL DEFAULT 'user'
            """)

        if "is_active" not in columns:
            db.execute("""
                ALTER TABLE users
                ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1
            """)

        db.commit()

        rows = db.execute("""
            SELECT id, username, email, role, is_active
            FROM users
            ORDER BY id DESC
        """).fetchall()

        # Your JavaScript expects an ARRAY, not an object
        users = [
            {
                "id": row["id"],
                "username": row["username"],
                "email": row["email"],
                "role": row["role"] or "user",
                "is_active": row["is_active"]
            }
            for row in rows
        ]

        return jsonify(users), 200

    except sqlite3.Error:
        db.rollback()
        app.logger.exception("Failed to retrieve admin users")

        return jsonify({
            "success": False,
            "message": "Database error while retrieving users."
        }), 500

    finally:
        db.close()


# Deactivate or reactivate a user without deleting their record
@app.route("/api/admin/users/<int:user_id>", methods=["DELETE"])
@admin_required
def toggle_user_status(user_id):
    db = get_db()

    try:
        columns = {
            row["name"]
            for row in db.execute("PRAGMA table_info(users)").fetchall()
        }

        if "is_active" not in columns:
            return jsonify({
                "success": False,
                "message": "The is_active column is missing."
            }), 500

        user = db.execute("""
            SELECT id, username, role, is_active
            FROM users
            WHERE id = ?
        """, (user_id,)).fetchone()

        if user is None:
            return jsonify({
                "success": False,
                "message": "User not found."
            }), 404

        # Prevent accidental deactivation of an admin account
        if user["role"] == "admin":
            return jsonify({
                "success": False,
                "message": "Administrator accounts cannot be deactivated here."
            }), 403

        # 1 = active, 0 = inactive
        new_status = 0 if int(user["is_active"]) == 1 else 1

        db.execute("""
            UPDATE users
            SET is_active = ?
            WHERE id = ?
        """, (new_status, user_id))

        db.commit()

        action = "deactivated" if new_status == 0 else "reactivated"

        return jsonify({
            "success": True,
            "message": f"User {user['username']} {action} successfully.",
            "id": user_id,
            "is_active": new_status
        }), 200

    except sqlite3.Error:
        db.rollback()
        app.logger.exception("Failed to update user status")

        return jsonify({
            "success": False,
            "message": "Database error while updating user status."
        }), 500

    finally:
        db.close()


@app.route("/api/admin/room", methods=["GET"])
@admin_required
def api_admin_room():
    db = get_db()

    try:
        # 1. Get room counts.
        count_row = db.execute("""
            SELECT
                COUNT(*) AS total,

                COALESCE(SUM(
                    CASE
                        WHEN LOWER(TRIM(COALESCE(status, '')))
                             = 'available'
                        THEN 1 ELSE 0
                    END
                ), 0) AS available,

                COALESCE(SUM(
                    CASE
                        WHEN LOWER(TRIM(COALESCE(status, ''))) IN (
                            'occupied',
                            'occupy',
                            'ocuppy',
                            'ocuupied'
                        )
                        THEN 1 ELSE 0
                    END
                ), 0) AS occupied,

                COALESCE(SUM(
                    CASE
                        WHEN LOWER(TRIM(COALESCE(status, ''))) IN (
                            'maintenance',
                            'under maintenance'
                        )
                        THEN 1 ELSE 0
                    END
                ), 0) AS maintenance

            FROM Room
        """).fetchone()

        count = {
            "total": count_row["total"],
            "available": count_row["available"],
            "occupied": count_row["occupied"],
            "maintenance": count_row["maintenance"]
        }

        # 2. Read search filters from the JavaScript URL.
        room_number = request.args.get("room_number", "").strip()
        room_type = request.args.get("room_type", "").strip()

        # 3. Get the latest booking record for each room.
        # This avoids showing multiple rows for rooms with booking history.
        sql = """
            SELECT
                r.Room_No AS Room_No,
                b.fullname AS fullname,
                r.Room_type AS Room_type,
                r.status AS status,
                b.checkin AS checkin,
                b.checkout AS checkout,
                b.email AS email
            FROM Room AS r

            LEFT JOIN (
                SELECT b1.*
                FROM bookings AS b1
                INNER JOIN (
                    SELECT Room_number, MAX(id) AS latest_id
                    FROM bookings
                    GROUP BY Room_number
                ) AS latest
                ON b1.id = latest.latest_id
            ) AS b
            ON CAST(b.Room_number AS TEXT) = CAST(r.Room_No AS TEXT)

            WHERE 1 = 1
        """

        params = []

        if room_number:
            sql += " AND CAST(r.Room_No AS TEXT) LIKE ?"
            params.append(f"%{room_number}%")

        if room_type and room_type.lower() != "all":
            sql += " AND LOWER(r.Room_type) = LOWER(?)"
            params.append(room_type)

        sql += " ORDER BY r.Room_No ASC"

        room_rows = db.execute(sql, params).fetchall()

        rooms = [
            {
                "Room_No": row["Room_No"],
                "fullname": row["fullname"],
                "Room_type": row["Room_type"],
                "status": row["status"],
                "checkin": row["checkin"],
                "checkout": row["checkout"],
                "email": row["email"]
            }
            for row in room_rows
        ]

        # 4. Return both the counts and search results.
        return jsonify({
            "success": True,
            "count": count,
            "rooms": rooms
        }), 200

    except sqlite3.Error:
        app.logger.exception("Failed to load admin room data")
        return jsonify({
            "success": False,
            "message": "Could not load room information."
        }), 500

    finally:
        db.close()


@app.route('/admin/room',methods=["GET"])
@admin_required
def admin_room():
    return render_template("room_manage.html")
#admin booking management
@app.route('/api/admin/book', methods=["GET"])
@admin_required
def api_admin_bookings():
    conn = get_db()

    try:
        amount = conn.execute("""
            SELECT
                COUNT(*) AS total,

                COALESCE(SUM(
                    CASE
                        WHEN LOWER(TRIM(status)) = 'pending'
                        THEN 1 ELSE 0
                    END
                ), 0) AS pending,

                COALESCE(SUM(
                    CASE
                        WHEN LOWER(TRIM(status)) IN ('cancel', 'cancelled')
                        THEN 1 ELSE 0
                    END
                ), 0) AS cancel,

                COALESCE(SUM(
                    CASE
                        WHEN LOWER(TRIM(status)) = 'checked_in'
                        THEN 1 ELSE 0
                    END
                ), 0) AS checkin,

                COALESCE(SUM(
                    CASE
                        WHEN LOWER(TRIM(status)) = 'checked_out'
                        THEN 1 ELSE 0
                    END
                ), 0) AS checkout

            FROM bookings
        """).fetchone()

        customers = conn.execute("""
            SELECT
                b.id,
                COALESCE(u.username, b.fullname) AS username,
                b.checkin,
                b.checkout,
                b.status
            FROM bookings AS b
            LEFT JOIN users AS u ON b.user_id = u.id
            ORDER BY b.id ASC
        """).fetchall()

        return jsonify({
            "total": amount["total"],
            "pending": amount["pending"],
            "cancel": amount["cancel"],
            "checkin": amount["checkin"],
            "checkout": amount["checkout"],
            "customers": [
                dict(customer) for customer in customers
            ]
        })

    except Exception as e:
        app.logger.exception("Failed to load admin bookings")
        return jsonify({"error": "Failed to load bookings"}), 500

    finally:
        conn.close()
@app.route("/admin/book",methods=["GET"])
@admin_required
def admin_bookings():
    return render_template("book_manage.html")

@app.route("/admiiin/payment",methods=["GET"])
@admin_required
def admin_paymeeents():
    return render_template("payment.html")
#---------------------------------------------------------
@app.route("/admin/payment", methods=["GET"])
@admin_required
def admin_payments():

    conn = get_db()
    conn.row_factory = sqlite3.Row

    bookings = conn.execute("""
        SELECT rowid AS id, *
        FROM bookings
        ORDER BY rowid DESC
    """).fetchall()

    conn.close()

    return render_template(
        "payment.html",
        bookings=bookings
    )
#-----------

@app.route("/admin/admin_feedback")
@admin_required
def admin_feedback():
    return "feedback"
@app.route("/admin/reports")
@admin_required
def admin_reports():
    return "report"
# ---------------------------------------------------------
# GALLERY
# ---------------------------------------------------------

@app.route("/gallery")
def gallery():
    return render_template("Gallery.html")


# ---------------------------------------------------------
# CHECKOUT
# ---------------------------------------------------------

@app.route("/leave", methods=["GET", "POST"])
def checkout():

    if request.method == "GET":
        return render_template("checkout.html")

    try:
        data = request.get_json(silent=True) or {}

        username = data.get("user")
        room_raw = data.get("Room")
        rating_value = data.get("rating")

        if not username or room_raw is None:
            return jsonify({
                "status": "error",
                "message": "Username and room number are required."
            }), 400

        try:
            room = int(room_raw)
        except (ValueError, TypeError):
            return jsonify({
                "status": "error",
                "message": "Room number must be a valid number."
            }), 400

        with get_db() as conn:

            booking_row = conn.execute("""
                SELECT fullname, email, Room_number, Room_type
                FROM bookings
                WHERE fullname = ?
                AND Room_number = ?
                LIMIT 1
            """, (username, room)).fetchone()

            if not booking_row:
                return jsonify({
                    "status": "error",
                    "message": "No matching booking found."
                }), 404

            # Find the account connected to this booking.
            user = conn.execute("""
                SELECT id
                FROM users
                WHERE email = ?
                LIMIT 1
            """, (booking_row["email"],)).fetchone()

            user_id = user["id"] if user else None

            # Save checkout information in Records.
            conn.execute("""
                INSERT INTO Records
                (USER_ID, fullname, email, room_number, room_type)
                VALUES (?, ?, ?, ?, ?)
            """, (
                user_id,
                booking_row["fullname"],
                booking_row["email"],
                booking_row["Room_number"],
                booking_row["Room_type"]
            ))

            # Delete the active booking.
            conn.execute("""
                DELETE FROM bookings
                WHERE fullname = ?
                AND Room_number = ?
            """, (username, room))

            # Make room available again.
            conn.execute("""
                UPDATE Room
                SET status = 'available'
                WHERE Room_No = ?
            """, (room,))

        print(
            f"Checkout: user={username}, "
            f"room={room}, rating={rating_value}"
        )

        return jsonify({
            "status": "success",
            "message": "Checkout completed successfully."
        }), 200

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/feedback",methods=["GET","POST"])
def feedback():
    return render_template("feed-back.html")

# ---------------------------------------------------------
# HISTORY
# ---------------------------------------------------------

@app.route("/history",methods=["GET"])
@login_required
def history():

    current_user_id = session["user_id"]

    conn = get_db()

    records = conn.execute("""
        SELECT
            room_number,
            room_type,
            fullname,
            email
        FROM Records
        WHERE USER_ID = ?
        ORDER BY id DESC
    """, (current_user_id,)).fetchall()

    conn.close()

    return render_template(
        "History.html",
        records=records
    )


# ---------------------------------------------------------
# RUN APPLICATION
# ---------------------------------------------------------

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=8000,
        debug=True
    )
