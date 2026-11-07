from flask import Flask, render_template, request, redirect, url_for, flash, session

from decimal import Decimal

from database import get_connection



app = Flask(__name__)



app.secret_key = "cinebook-secret-key"





# =========================================================

# HOME PAGE

# =========================================================



@app.route("/")

def index():

    return render_template("index.html")





# =========================================================

# CUSTOMER REGISTER

# =========================================================



@app.route("/register", methods=["GET", "POST"])

def register():



    if request.method == "POST":



        name = request.form.get("name", "").strip()

        email = request.form.get("email", "").strip()

        password = request.form.get("password", "")



        connection = None

        cursor = None



        try:



            connection = get_connection()

            cursor = connection.cursor()



            # Check existing email

            cursor.execute(

                """

                SELECT user_id

                FROM users

                WHERE email = %s

                """,

                (email,)

            )



            existing_user = cursor.fetchone()



            if existing_user:



                return render_template(

                    "register.html",

                    error="An account with this email already exists."

                )



            # Insert customer

            cursor.execute(

                """

                INSERT INTO users

                (name, email, password)

                VALUES (%s, %s, %s)

                """,

                (name, email, password)

            )



            connection.commit()



            return redirect(url_for("login"))



        except Exception as error:



            print("Registration error:", error)



            if connection:

                connection.rollback()



            return render_template(

                "register.html",

                error="Something went wrong. Please try again."

            )



        finally:



            if cursor:

                cursor.close()



            if connection:

                connection.close()



    return render_template("register.html")





# =========================================================

# CUSTOMER LOGIN

# =========================================================



@app.route("/login", methods=["GET", "POST"])

def login():



    if request.method == "POST":



        email = request.form.get("email", "").strip()

        password = request.form.get("password", "")



        connection = None

        cursor = None



        try:



            connection = get_connection()

            cursor = connection.cursor(dictionary=True)



            cursor.execute(

                """

                SELECT user_id, name, email

                FROM users

                WHERE email = %s

                AND password = %s

                """,

                (email, password)

            )



            user = cursor.fetchone()



            if not user:



                return render_template(

                    "login.html",

                    error="Invalid email or password."

                )



            session.clear()



            session["user_id"] = user["user_id"]

            session["name"] = user["name"]

            session["user_name"] = user["name"]

            session["email"] = user["email"]



            return redirect(url_for("dashboard"))



        except Exception as error:



            print("Login error:", error)



            return render_template(

                "login.html",

                error="Unable to connect to the database."

            )



        finally:



            if cursor:

                cursor.close()



            if connection:

                connection.close()



    return render_template("login.html")





# =========================================================

# ADMIN LOGIN

# =========================================================



@app.route("/admin-login", methods=["GET", "POST"])

def admin_login():



    if request.method == "POST":



        username = request.form.get("username", "").strip()

        password = request.form.get("password", "")



        connection = None

        cursor = None



        try:



            connection = get_connection()

            cursor = connection.cursor(dictionary=True)



            cursor.execute(

                """

                SELECT admin_id, name, username

                FROM admins

                WHERE username = %s

                AND password = %s

                """,

                (username, password)

            )



            admin = cursor.fetchone()



            if not admin:



                return render_template(

                    "admin_login.html",

                    error="Invalid admin username or password."

                )



            session.clear()



            session["admin_id"] = admin["admin_id"]

            session["admin_name"] = admin["name"]

            session["admin_username"] = admin["username"]

            session["is_admin"] = True



            return redirect(url_for("admin_dashboard"))



        except Exception as error:



            print("Admin login error:", error)



            return render_template(

                "admin_login.html",

                error="Unable to connect to the database."

            )



        finally:



            if cursor:

                cursor.close()



            if connection:

                connection.close()



    return render_template("admin_login.html")





@app.route("/admin/screens", methods=["GET", "POST"])

def admin_screens():
    if not admin_required():
        return redirect(url_for("admin_login"))


    if request.method == "POST":

        theatre_id = request.form.get("theatre_id", type=int)

        screen_name = request.form.get("screen_name", "").strip()

        screen_type = request.form.get("screen_type", "").strip() or None

        total_seats = request.form.get("total_seats", type=int)



        if not theatre_id or not screen_name or not total_seats or total_seats < 1:

            flash("Enter a theatre, screen name and valid seat capacity.", "error")

            return redirect(url_for("admin_screens"))



        connection = None

        cursor = None



        try:

            connection = get_connection()

            cursor = connection.cursor()



            cursor.execute(

                "SELECT theatre_id FROM theatres WHERE theatre_id = %s",

                (theatre_id,)

            )

            if cursor.fetchone() is None:

                flash("Please select a valid theatre.", "error")

                return redirect(url_for("admin_screens"))



            cursor.execute(

                """

                INSERT INTO screens

                    (theatre_id, screen_name, screen_type, total_seats)

                VALUES (%s, %s, %s, %s)

                """,

                (theatre_id, screen_name, screen_type, total_seats)

            )

            connection.commit()

            flash("Screen added successfully.", "success")



        except Exception as exc:

            if connection:

                connection.rollback()

            print("Add screen error:", exc)

            flash("Could not add screen. Check the Flask terminal.", "error")



        finally:

            if cursor:

                cursor.close()

            if connection:

                connection.close()



        return redirect(url_for("admin_screens"))



    screens = []

    theatres = []

    connection = None

    cursor = None



    try:

        connection = get_connection()

        cursor = connection.cursor(dictionary=True)



        cursor.execute(

            """

            SELECT s.screen_id, s.theatre_id, s.screen_name,

                   s.screen_type, s.total_seats,

                   t.name AS theatre_name, t.city AS theatre_city

            FROM screens s

            LEFT JOIN theatres t ON t.theatre_id = s.theatre_id

            ORDER BY s.screen_id DESC

            """

        )

        screens = cursor.fetchall()



        cursor.execute(

            "SELECT theatre_id, name, city FROM theatres ORDER BY name"

        )

        theatres = cursor.fetchall()



    except Exception as exc:

        print("Load screens error:", exc)

        flash("Could not load screens. Check your theatre table columns.", "error")



    finally:

        if cursor:

            cursor.close()

        if connection:

            connection.close()



    return render_template(

        "admin_screens.html",

        screens=screens,

        theatres=theatres,

        admin_name=session.get("admin_name", "Admin")

    )





@app.route("/admin/screens/<int:screen_id>/edit", methods=["GET", "POST"])

def edit_screen(screen_id):

    connection = None

    cursor = None



    try:

        connection = get_connection()

        cursor = connection.cursor(dictionary=True)



        if request.method == "POST":

            theatre_id = request.form.get("theatre_id", type=int)

            screen_name = request.form.get("screen_name", "").strip()

            screen_type = request.form.get("screen_type", "").strip() or None

            total_seats = request.form.get("total_seats", type=int)



            if not theatre_id or not screen_name or not total_seats or total_seats < 1:

                flash("Enter valid screen details.", "error")

                return redirect(url_for("edit_screen", screen_id=screen_id))



            cursor.execute(

                "SELECT theatre_id FROM theatres WHERE theatre_id = %s",

                (theatre_id,)

            )

            if cursor.fetchone() is None:

                flash("Please select a valid theatre.", "error")

                return redirect(url_for("edit_screen", screen_id=screen_id))



            cursor.execute(

                """

                UPDATE screens

                SET theatre_id = %s, screen_name = %s,

                    screen_type = %s, total_seats = %s

                WHERE screen_id = %s

                """,

                (theatre_id, screen_name, screen_type, total_seats, screen_id)

            )

            connection.commit()

            flash("Screen updated successfully.", "success")

            return redirect(url_for("admin_screens"))



        cursor.execute(

            """

            SELECT screen_id, theatre_id, screen_name, screen_type, total_seats

            FROM screens WHERE screen_id = %s

            """,

            (screen_id,)

        )

        screen = cursor.fetchone()



        if not screen:

            flash("Screen not found.", "error")

            return redirect(url_for("admin_screens"))



        cursor.execute(

            "SELECT theatre_id, name, city FROM theatres ORDER BY name"

        )

        theatres = cursor.fetchall()



        return render_template(

            "admin_edit_screen.html",

            screen=screen,

            theatres=theatres,

            admin_name=session.get("admin_name", "Admin")

        )



    except Exception as exc:

        if connection:

            connection.rollback()

        print("Edit screen error:", exc)

        flash("Could not edit screen. Check the Flask terminal.", "error")

        return redirect(url_for("admin_screens"))



    finally:

        if cursor:

            cursor.close()

        if connection:

            connection.close()





@app.route("/admin/screens/<int:screen_id>/delete", methods=["POST"])

def delete_screen_with_checks(screen_id):

    connection = None

    cursor = None



    try:

        connection = get_connection()

        cursor = connection.cursor()



        # Prevent deletion when related seats or shows exist.

        cursor.execute(

            "SELECT COUNT(*) FROM shows WHERE screen_id = %s",

            (screen_id,)

        )

        show_count = cursor.fetchone()[0]



        cursor.execute(

            "SELECT COUNT(*) FROM seats WHERE screen_id = %s",

            (screen_id,)

        )

        seat_count = cursor.fetchone()[0]



        if show_count or seat_count:

            flash(

                "Cannot delete this screen because it has associated seats or shows.",

                "error"

            )

        else:

            cursor.execute(

                "DELETE FROM screens WHERE screen_id = %s",

                (screen_id,)

            )

            connection.commit()

            flash("Screen deleted successfully.", "success")



    except Exception as exc:

        if connection:

            connection.rollback()

        print("Delete screen error:", exc)

        flash("Could not delete screen. Check related database records.", "error")



    finally:

        if cursor:

            cursor.close()

        if connection:

            connection.close()



    return redirect(url_for("admin_screens"))



# =========================================================

# ACCESS CHECKS

# =========================================================



def admin_required():



    return bool(

        session.get("admin_id")

        and session.get("is_admin") is True

    )





def customer_required():



    return bool(

        session.get("user_id")

        and not session.get("is_admin")

    )





# =========================================================

# ADMIN DASHBOARD

# =========================================================



@app.route("/admin-dashboard")

def admin_dashboard():



    if not admin_required():



        return redirect(url_for("admin_login"))



    connection = None

    cursor = None



    try:



        connection = get_connection()

        cursor = connection.cursor(dictionary=True)



        # Movies

        cursor.execute(

            """

            SELECT COUNT(*) AS total_movies

            FROM movies

            """

        )



        total_movies = cursor.fetchone()["total_movies"]



        # Theatres

        cursor.execute(

            """

            SELECT COUNT(*) AS total_theatres

            FROM theatres

            """

        )



        total_theatres = cursor.fetchone()["total_theatres"]



        # Users

        cursor.execute(

            """

            SELECT COUNT(*) AS total_users

            FROM users

            """

        )



        total_users = cursor.fetchone()["total_users"]



        # Bookings

        cursor.execute(

            """

            SELECT COUNT(*) AS total_bookings

            FROM bookings

            """

        )



        total_bookings = cursor.fetchone()["total_bookings"]



        # Revenue

        cursor.execute(

            """

            SELECT COALESCE(SUM(amount), 0) AS total_revenue

            FROM payments

            WHERE payment_status = 'Paid'

            """

        )



        total_revenue = cursor.fetchone()["total_revenue"]



        return render_template(

            "admin_dashboard.html",

            admin_name=session.get(

                "admin_name",

                "Administrator"

            ),

            total_movies=total_movies,

            total_theatres=total_theatres,

            total_users=total_users,

            total_bookings=total_bookings,

            total_revenue=total_revenue

        )



    except Exception as error:



        print("ADMIN DASHBOARD ERROR:", error)



        return (

            "Unable to load admin dashboard. "

            "Check the Flask terminal for the database error."

        )



    finally:



        if cursor:

            cursor.close()



        if connection:

            connection.close()





# =========================================================

# ADMIN LOGOUT

# =========================================================



@app.route("/admin-logout")

def admin_logout():



    session.clear()



    return redirect(url_for("index"))



# =========================================================

# CUSTOMER DASHBOARD

# =========================================================



@app.route("/dashboard")

def dashboard():



    # Admin should not enter customer dashboard

    if session.get("is_admin"):

        return redirect(url_for("admin_dashboard"))



    # Customer must be logged in

    if not customer_required():

        return redirect(url_for("login"))



    connection = None

    cursor = None



    try:



        connection = get_connection()

        cursor = connection.cursor(dictionary=True)



        # =================================================

        # MOVIES

        # =================================================



        cursor.execute(

            """

            SELECT

                movie_id,

                title,

                genre,

                duration,

                language,

                release_date,

                description,

                poster_url

            FROM movies

            ORDER BY movie_id DESC

            """

        )



        movies = cursor.fetchall()





        # =================================================

        # CUSTOMER BOOKINGS

        #

        # bookings -> shows -> movies

        #

        # IMPORTANT:

        # bookings has show_id, NOT movie_id

        # =================================================



        cursor.execute(

            """

            SELECT

                b.booking_id,

                b.booking_date,

                b.total_amount,

                b.status,



                m.title AS movie_title,



                s.show_date,

                s.show_time,

                s.ticket_price



            FROM bookings b



            JOIN shows s

                ON b.show_id = s.show_id



            JOIN movies m

                ON s.movie_id = m.movie_id



            WHERE b.user_id = %s



            ORDER BY b.booking_date DESC

            """,

            (session["user_id"],)

        )



        bookings = cursor.fetchall()





        # =================================================

        # TOTAL MOVIES

        # =================================================



        cursor.execute(

            """

            SELECT COUNT(*) AS total_movies

            FROM movies

            """

        )



        total_movies = cursor.fetchone()["total_movies"]





        # =================================================

        # TOTAL THEATRES

        # =================================================



        cursor.execute(

            """

            SELECT COUNT(*) AS total_theatres

            FROM theatres

            """

        )



        total_theatres = cursor.fetchone()["total_theatres"]





        # =================================================

        # CUSTOMER BOOKING COUNT

        # =================================================



        cursor.execute(

            """

            SELECT COUNT(*) AS total_bookings

            FROM bookings

            WHERE user_id = %s

            """,

            (session["user_id"],)

        )



        total_bookings = cursor.fetchone()["total_bookings"]





        # =================================================

        # SEND DATA TO DASHBOARD

        # =================================================



        return render_template(

            "dashboard.html",



            name=session.get("name"),



            email=session.get("email"),



            movies=movies,



            bookings=bookings,



            total_movies=total_movies,



            total_theatres=total_theatres,



            total_bookings=total_bookings

        )





    except Exception as error:



        print(

            "CUSTOMER DASHBOARD ERROR:",

            error

        )



        return (

            "Unable to load dashboard. "

            "Check the Flask terminal for the database error."

        )





    finally:



        if cursor:

            cursor.close()



        if connection:

            connection.close()





# =========================================================

# CUSTOMER LOGOUT

# =========================================================



@app.route("/logout")

def logout():



    session.clear()



    return redirect(url_for("index"))





# =========================================================

# ADMIN - VIEW USERS

# =========================================================



@app.route("/users")

def users():



    if not admin_required():



        return redirect(url_for("admin_login"))



    connection = None

    cursor = None



    try:



        connection = get_connection()

        cursor = connection.cursor(dictionary=True)



        cursor.execute(

            """

            SELECT

                user_id,

                name,

                email,

                created_at

            FROM users

            ORDER BY user_id DESC

            """

        )



        users_list = cursor.fetchall()



        return render_template(

            "users.html",

            users=users_list

        )



    except Exception as error:



        print("Users error:", error)



        return "Unable to load users."



    finally:



        if cursor:

            cursor.close()



        if connection:

            connection.close()





# =========================================================

# ADMIN - UPDATE USER

# =========================================================



@app.route(

    "/update-user/<int:user_id>",

    methods=["GET", "POST"]

)

def update_user(user_id):



    if not admin_required():



        return redirect(url_for("admin_login"))



    connection = None

    cursor = None



    try:



        connection = get_connection()

        cursor = connection.cursor(dictionary=True)



        if request.method == "GET":



            cursor.execute(

                """

                SELECT

                    user_id,

                    name,

                    email

                FROM users

                WHERE user_id = %s

                """,

                (user_id,)

            )



            user = cursor.fetchone()



            if not user:



                return "User not found", 404



            return render_template(

                "update_user.html",

                user=user

            )



        name = request.form.get(

            "name",

            ""

        ).strip()



        email = request.form.get(

            "email",

            ""

        ).strip()



        cursor.execute(

            """

            UPDATE users

            SET name = %s,

                email = %s

            WHERE user_id = %s

            """,

            (name, email, user_id)

        )



        connection.commit()



        return redirect(url_for("users"))



    except Exception as error:



        print("Update user error:", error)



        if connection:

            connection.rollback()



        return "Unable to update user."



    finally:



        if cursor:

            cursor.close()



        if connection:

            connection.close()





# =========================================================

# ADMIN - DELETE USER

# =========================================================



@app.route(

    "/delete-user/<int:user_id>",

    methods=["POST"]

)

def delete_user(user_id):



    if not admin_required():



        return redirect(url_for("admin_login"))



    connection = None

    cursor = None



    try:



        connection = get_connection()

        cursor = connection.cursor()



        cursor.execute(

            """

            DELETE FROM users

            WHERE user_id = %s

            """,

            (user_id,)

        )



        connection.commit()



        return redirect(url_for("users"))



    except Exception as error:



        print("Delete user error:", error)



        if connection:

            connection.rollback()



        return (

            "Unable to delete user. "

            "The user may have existing bookings."

        )



    finally:



        if cursor:

            cursor.close()



        if connection:

            connection.close()





# =========================================================

# ADMIN - VIEW MOVIES

# =========================================================



@app.route("/admin-movies")

def admin_movies():



    if not admin_required():



        return redirect(url_for("admin_login"))



    connection = None

    cursor = None



    try:



        connection = get_connection()

        cursor = connection.cursor(dictionary=True)



        cursor.execute(

            """

            SELECT

                movie_id,

                title,

                genre,

                duration,

                language,

                release_date,

                description,

                poster_url

            FROM movies

            ORDER BY movie_id DESC

            """

        )



        movies = cursor.fetchall()



        return render_template(

            "admin_movies.html",

            movies=movies,

            admin_name=session.get(

                "admin_name",

                "Administrator"

            )

        )



    except Exception as error:



        print("Admin movies error:", error)



        return "Unable to load movies."



    finally:



        if cursor:

            cursor.close()



        if connection:

            connection.close()





# =========================================================

# ADMIN - ADD MOVIE

# =========================================================



@app.route(

    "/admin-movies/add",

    methods=["GET", "POST"]

)

def add_movie():



    if not admin_required():



        return redirect(url_for("admin_login"))



    if request.method == "POST":



        title = request.form.get(

            "title",

            ""

        ).strip()



        genre = request.form.get(

            "genre",

            ""

        ).strip()



        duration = request.form.get(

            "duration",

            ""

        ).strip()



        language = request.form.get(

            "language",

            ""

        ).strip()



        release_date = (

            request.form.get("release_date")

            or None

        )



        description = (

            request.form.get(

                "description",

                ""

            ).strip()

            or None

        )



        poster_url = (

            request.form.get(

                "poster_url",

                ""

            ).strip()

            or None

        )



        connection = None

        cursor = None



        try:



            connection = get_connection()

            cursor = connection.cursor()



            cursor.execute(

                """

                INSERT INTO movies

                (

                    title,

                    genre,

                    duration,

                    language,

                    release_date,

                    description,

                    poster_url

                )

                VALUES

                (

                    %s,

                    %s,

                    %s,

                    %s,

                    %s,

                    %s,

                    %s

                )

                """,

                (

                    title,

                    genre,

                    duration,

                    language,

                    release_date,

                    description,

                    poster_url

                )

            )



            connection.commit()



            return redirect(

                url_for("admin_movies")

            )



        except Exception as error:



            print("Add movie error:", error)



            if connection:

                connection.rollback()



            return render_template(

                "admin_add_movie.html",

                error="Unable to add movie."

            )



        finally:



            if cursor:

                cursor.close()



            if connection:

                connection.close()



    return render_template(

        "admin_add_movie.html"

    )





# =========================================================

# ADMIN - DELETE MOVIE

# =========================================================



@app.route(

    "/admin-movies/delete/<int:movie_id>",

    methods=["POST"]

)

def delete_movie(movie_id):



    if not admin_required():



        return redirect(url_for("admin_login"))



    connection = None

    cursor = None



    try:



        connection = get_connection()

        cursor = connection.cursor()



        cursor.execute(

            """

            DELETE FROM movies

            WHERE movie_id = %s

            """,

            (movie_id,)

        )



        connection.commit()



        return redirect(

            url_for("admin_movies")

        )



    except Exception as error:



        print("Delete movie error:", error)



        if connection:

            connection.rollback()



        return (

            "<h2>Unable to delete movie</h2>"

            "<p>"

            "This movie may already be connected "

            "to shows or bookings."

            "</p>"

            '<a href="/admin-movies">'

            "Back to Movies"

            "</a>"

        )



    finally:



        if cursor:

            cursor.close()



        if connection:

            connection.close()

# =========================================================

# ADMIN - ADD THEATRE

# =========================================================



@app.route(

    "/admin-theatres/add",

    methods=["GET", "POST"]

)

def add_theatre():



    if not admin_required():



        return redirect(url_for("admin_login"))



    if request.method == "POST":



        name = request.form.get(

            "name",

            ""

        ).strip()



        location = request.form.get(

            "location",

            ""

        ).strip()



        city = request.form.get(

            "city",

            ""

        ).strip()



        connection = None

        cursor = None



        try:



            connection = get_connection()

            cursor = connection.cursor()



            cursor.execute(

                """

                INSERT INTO theatres

                (

                    name,

                    location,

                    city

                )

                VALUES

                (

                    %s,

                    %s,

                    %s

                )

                """,

                (

                    name,

                    location,

                    city

                )

            )



            connection.commit()



            return redirect(

                url_for("admin_theatres")

            )



        except Exception as error:



            print("Add theatre error:", error)



            if connection:

                connection.rollback()



            return render_template(

                "admin_add_theatre.html",

                error="Unable to add theatre."

            )



        finally:



            if cursor:

                cursor.close()



            if connection:

                connection.close()



    return render_template(

        "admin_add_theatre.html"

    )







# =========================================================

# ADMIN - DELETE THEATRE

# =========================================================



@app.route(

    "/admin-theatres/delete/<int:theatre_id>",

    methods=["POST"]

)

def delete_theatre(theatre_id):



    if not admin_required():



        return redirect(url_for("admin_login"))



    connection = None

    cursor = None



    try:



        connection = get_connection()

        cursor = connection.cursor()



        cursor.execute(

            """

            DELETE FROM theatres

            WHERE theatre_id = %s

            """,

            (theatre_id,)

        )



        connection.commit()



        return redirect(

            url_for("admin_theatres")

        )



    except Exception as error:



        print("Delete theatre error:", error)



        if connection:

            connection.rollback()



        return (

            "<h2>Unable to delete theatre</h2>"

            "<p>"

            "This theatre may have screens connected to it."

            "</p>"

            '<a href="/admin-theatres">'

            "Back to Theatres"

            "</a>"

        )



    finally:



        if cursor:

            cursor.close()



        if connection:

            connection.close()





# =========================================================

# ADMIN - VIEW SCREENS

# =========================================================



# Duplicate admin_screens route removed; the earlier /admin/screens handler supports listing and adding screens.


@app.route(

    "/admin-screens/add",

    methods=["GET", "POST"]

)

def add_screen():



    if not admin_required():



        return redirect(url_for("admin_login"))



    connection = None

    cursor = None



    try:



        connection = get_connection()

        cursor = connection.cursor(dictionary=True)



        if request.method == "POST":



            theatre_id = request.form.get(

                "theatre_id"

            )



            screen_name = request.form.get(

                "screen_name",

                ""

            ).strip()



            screen_type = (

                request.form.get(

                    "screen_type",

                    ""

                ).strip()

                or None

            )



            total_seats = request.form.get(

                "total_seats"

            )



            cursor.execute(

                """

                INSERT INTO screens

                (

                    theatre_id,

                    screen_name,

                    screen_type,

                    total_seats

                )

                VALUES

                (

                    %s,

                    %s,

                    %s,

                    %s

                )

                """,

                (

                    theatre_id,

                    screen_name,

                    screen_type,

                    total_seats

                )

            )



            connection.commit()



            return redirect(

                url_for("admin_screens")

            )



        cursor.execute(

            """

            SELECT

                theatre_id,

                name

            FROM theatres

            ORDER BY name

            """

        )



        theatres = cursor.fetchall()



        return render_template(

            "admin_add_screen.html",

            theatres=theatres

        )



    except Exception as error:



        print("Add screen error:", error)



        if connection:

            connection.rollback()



        return "Unable to add screen."



    finally:



        if cursor:

            cursor.close()



        if connection:

            connection.close()





# =========================================================

# ADMIN - DELETE SCREEN

# =========================================================



@app.route(

    "/admin-screens/delete/<int:screen_id>",

    methods=["POST"]

)

def delete_screen(screen_id):



    if not admin_required():



        return redirect(url_for("admin_login"))



    connection = None

    cursor = None



    try:



        connection = get_connection()

        cursor = connection.cursor()



        cursor.execute(

            """

            DELETE FROM screens

            WHERE screen_id = %s

            """,

            (screen_id,)

        )



        connection.commit()



        return redirect(

            url_for("admin_screens")

        )



    except Exception as error:



        print("Delete screen error:", error)



        if connection:

            connection.rollback()



        return (

            "<h2>Unable to delete screen</h2>"

            "<p>"

            "This screen may have seats or shows connected to it."

            "</p>"

            '<a href="/admin-screens">'

            "Back to Screens"

            "</a>"

        )



    finally:



        if cursor:

            cursor.close()



        if connection:

            connection.close()





# =========================================================

# ADMIN - VIEW SEATS

# =========================================================



@app.route("/admin-seats")

def admin_seats():



    if not admin_required():



        return redirect(url_for("admin_login"))



    connection = None

    cursor = None



    try:



        connection = get_connection()

        cursor = connection.cursor(dictionary=True)



        cursor.execute(

            """

            SELECT

                se.seat_id,

                se.screen_id,

                se.seat_number,

                se.row_label,

                se.seat_type,

                sc.screen_name,

                t.name AS theatre_name

            FROM seats se

            JOIN screens sc

                ON se.screen_id = sc.screen_id

            JOIN theatres t

                ON sc.theatre_id = t.theatre_id

            ORDER BY se.seat_id DESC

            """

        )



        seats = cursor.fetchall()



        return render_template(

            "admin_seats.html",

            seats=seats

        )



    except Exception as error:



        print("Seats error:", error)



        return "Unable to load seats."



    finally:



        if cursor:

            cursor.close()



        if connection:

            connection.close()





# =========================================================

# ADMIN - ADD SEAT

# =========================================================



@app.route(

    "/admin-seats/add",

    methods=["GET", "POST"]

)

def add_seat():



    if not admin_required():



        return redirect(url_for("admin_login"))



    connection = None

    cursor = None



    try:



        connection = get_connection()

        cursor = connection.cursor(dictionary=True)



        if request.method == "POST":



            screen_id = request.form.get(

                "screen_id"

            )



            seat_number = request.form.get(

                "seat_number",

                ""

            ).strip()



            row_label = request.form.get(

                "row_label",

                ""

            ).strip()



            seat_type = request.form.get(

                "seat_type",

                ""

            ).strip()



            cursor.execute(

                """

                INSERT INTO seats

                (

                    screen_id,

                    seat_number,

                    row_label,

                    seat_type

                )

                VALUES

                (

                    %s,

                    %s,

                    %s,

                    %s

                )

                """,

                (

                    screen_id,

                    seat_number,

                    row_label,

                    seat_type

                )

            )



            connection.commit()



            return redirect(

                url_for("admin_seats")

            )



        cursor.execute(

            """

            SELECT

                screen_id,

                screen_name

            FROM screens

            ORDER BY screen_name

            """

        )



        screens = cursor.fetchall()



        return render_template(

            "admin_add_seat.html",

            screens=screens

        )



    except Exception as error:



        print("Add seat error:", error)



        if connection:

            connection.rollback()



        return "Unable to add seat."



    finally:



        if cursor:

            cursor.close()



        if connection:

            connection.close()





# =========================================================

# ADMIN - DELETE SEAT

# =========================================================



@app.route(

    "/admin-seats/delete/<int:seat_id>",

    methods=["POST"]

)

def delete_seat(seat_id):



    if not admin_required():



        return redirect(url_for("admin_login"))



    connection = None

    cursor = None



    try:



        connection = get_connection()

        cursor = connection.cursor()



        cursor.execute(

            """

            DELETE FROM seats

            WHERE seat_id = %s

            """,

            (seat_id,)

        )



        connection.commit()



        return redirect(

            url_for("admin_seats")

        )



    except Exception as error:



        print("Delete seat error:", error)



        if connection:

            connection.rollback()



        return "Unable to delete seat."



    finally:



        if cursor:

            cursor.close()



        if connection:

            connection.close()





# =========================================================

# ADMIN - VIEW SHOWS

# =========================================================



@app.route("/admin-shows")

def admin_shows():



    if not admin_required():



        return redirect(url_for("admin_login"))



    connection = None

    cursor = None



    try:



        connection = get_connection()

        cursor = connection.cursor(dictionary=True)



        cursor.execute(

            """

            SELECT

                s.show_id,

                s.movie_id,

                s.screen_id,

                s.show_date,

                s.show_time,

                s.ticket_price,

                s.status,

                m.title AS movie_title,

                sc.screen_name,

                t.name AS theatre_name

            FROM shows s

            JOIN movies m

                ON s.movie_id = m.movie_id

            JOIN screens sc

                ON s.screen_id = sc.screen_id

            JOIN theatres t

                ON sc.theatre_id = t.theatre_id

            ORDER BY s.show_date DESC, s.show_time DESC

            """

        )



        shows = cursor.fetchall()



        return render_template(

            "admin_shows.html",

            shows=shows

        )



    except Exception as error:



        print("Shows error:", error)



        return "Unable to load shows."



    finally:



        if cursor:

            cursor.close()



        if connection:

            connection.close()





# =========================================================

# ADMIN - ADD SHOW

# =========================================================



@app.route(

    "/admin-shows/add",

    methods=["GET", "POST"]

)

def add_show():



    if not admin_required():



        return redirect(url_for("admin_login"))



    connection = None

    cursor = None



    try:



        connection = get_connection()

        cursor = connection.cursor(dictionary=True)



        if request.method == "POST":



            movie_id = request.form.get(

                "movie_id"

            )



            screen_id = request.form.get(

                "screen_id"

            )



            show_date = request.form.get(

                "show_date"

            )



            show_time = request.form.get(

                "show_time"

            )



            ticket_price = request.form.get(

                "ticket_price"

            )



            status = (

                request.form.get(

                    "status",

                    "Active"

                ).strip()

                or "Active"

            )



            cursor.execute(

                """

                INSERT INTO shows

                (

                    movie_id,

                    screen_id,

                    show_date,

                    show_time,

                    ticket_price,

                    status

                )

                VALUES

                (

                    %s,

                    %s,

                    %s,

                    %s,

                    %s,

                    %s

                )

                """,

                (

                    movie_id,

                    screen_id,

                    show_date,

                    show_time,

                    ticket_price,

                    status

                )

            )



            connection.commit()



            return redirect(

                url_for("admin_shows")

            )



        cursor.execute(

            """

            SELECT

                movie_id,

                title

            FROM movies

            ORDER BY title

            """

        )



        movies = cursor.fetchall()



        cursor.execute(

            """

            SELECT

                screen_id,

                screen_name

            FROM screens

            ORDER BY screen_name

            """

        )



        screens = cursor.fetchall()



        return render_template(

            "admin_add_show.html",

            movies=movies,

            screens=screens

        )



    except Exception as error:



        print("Add show error:", error)



        if connection:

            connection.rollback()



        return "Unable to add show."



    finally:



        if cursor:

            cursor.close()



        if connection:

            connection.close()





# =========================================================

# ADMIN - DELETE SHOW

# =========================================================



@app.route(

    "/admin-shows/delete/<int:show_id>",

    methods=["POST"]

)

def delete_show(show_id):



    if not admin_required():



        return redirect(url_for("admin_login"))



    connection = None

    cursor = None



    try:



        connection = get_connection()

        cursor = connection.cursor()



        cursor.execute(

            """

            DELETE FROM shows

            WHERE show_id = %s

            """,

            (show_id,)

        )



        connection.commit()



        return redirect(

            url_for("admin_shows")

        )



    except Exception as error:



        print("Delete show error:", error)



        if connection:

            connection.rollback()



        return "Unable to delete show."



    finally:



        if cursor:

            cursor.close()



        if connection:

            connection.close()





# =========================================================

# ADMIN - VIEW BOOKINGS

# =========================================================



@app.route("/admin-bookings")

def admin_bookings():



    if not admin_required():



        return redirect(url_for("admin_login"))



    connection = None

    cursor = None



    try:



        connection = get_connection()

        cursor = connection.cursor(dictionary=True)



        cursor.execute(

            """

            SELECT
        b.booking_id,
        b.user_id,
        u.name AS customer_name,
        u.email AS customer_email,
        s.show_id,
        m.title AS movie_title,
        t.name AS theatre_name,
        sc.screen_name,
        s.show_date,
        s.show_time,
        b.booking_date,
        b.total_amount,
        b.status
    FROM bookings b
    LEFT JOIN users u
        ON b.user_id = u.user_id
    LEFT JOIN shows s
        ON b.show_id = s.show_id
    LEFT JOIN movies m
        ON s.movie_id = m.movie_id
    LEFT JOIN screens sc
        ON s.screen_id = sc.screen_id
    LEFT JOIN theatres t
        ON sc.theatre_id = t.theatre_id
    ORDER BY b.booking_id DESC

            """

        )



        bookings = cursor.fetchall()



        return render_template(

            "admin_bookings.html",

            bookings=bookings

        )



    except Exception as error:



        print("Bookings error:", error)



        return "Unable to load bookings."



    finally:



        if cursor:

            cursor.close()



        if connection:

            connection.close()





# =========================================================

# ADMIN - UPDATE BOOKING STATUS

# =========================================================



@app.route(

    "/admin-bookings/update/<int:booking_id>",

    methods=["POST"]

)

def update_booking_status(booking_id):



    if not admin_required():



        return redirect(url_for("admin_login"))



    status = request.form.get(

        "status",

        "Confirmed"

    ).strip()



    connection = None

    cursor = None



    try:



        connection = get_connection()

        cursor = connection.cursor()



        cursor.execute(

            """

            UPDATE bookings

            SET status = %s

            WHERE booking_id = %s

            """,

            (

                status,

                booking_id

            )

        )



        connection.commit()



        return redirect(

            url_for("admin_bookings")

        )



    except Exception as error:



        print("Update booking error:", error)



        if connection:

            connection.rollback()



        return "Unable to update booking."



    finally:



        if cursor:

            cursor.close()



        if connection:

            connection.close()





# =========================================================

# ADMIN - VIEW PAYMENTS

# =========================================================



@app.route("/admin-payments")

def admin_payments():



    if not admin_required():



        return redirect(url_for("admin_login"))



    connection = None

    cursor = None



    try:



        connection = get_connection()

        cursor = connection.cursor(dictionary=True)



        cursor.execute(

            """

            SELECT

                p.payment_id,

                p.booking_id,

                p.amount,

                p.payment_method,

                p.payment_status,

                p.payment_date

            FROM payments p

            ORDER BY p.payment_date DESC

            """

        )



        payments = cursor.fetchall()



        return render_template(

            "admin_payments.html",

            payments=payments

        )



    except Exception as error:



        print("Payments error:", error)



        return "Unable to load payments."



    finally:



        if cursor:

            cursor.close()



        if connection:

            connection.close()





# =========================================================

# ADMIN - UPDATE PAYMENT STATUS

# =========================================================



@app.route(

    "/admin-payments/update/<int:payment_id>",

    methods=["POST"]

)

def update_payment_status(payment_id):



    if not admin_required():



        return redirect(url_for("admin_login"))



    payment_status = request.form.get(

        "payment_status",

        "Pending"

    ).strip()



    connection = None

    cursor = None



    try:



        connection = get_connection()

        cursor = connection.cursor()



        cursor.execute(

            """

            UPDATE payments

            SET payment_status = %s

            WHERE payment_id = %s

            """,

            (

                payment_status,

                payment_id

            )

        )



        connection.commit()



        return redirect(

            url_for("admin_payments")

        )



    except Exception as error:



        print("Update payment error:", error)



        if connection:

            connection.rollback()



        return "Unable to update payment."



    finally:



        if cursor:

            cursor.close()



        if connection:

            connection.close()



# =========================================================

# ADMIN - VIEW THEATRES

# =========================================================



@app.route("/admin-theatres")

def admin_theatres():



    if not admin_required():

        return redirect(url_for("admin_login"))



    connection = None

    cursor = None



    try:

        connection = get_connection()

        cursor = connection.cursor(dictionary=True)



        cursor.execute("""

            SELECT

                theatre_id,

                name,

                location,

                city

            FROM theatres

            ORDER BY theatre_id DESC

        """)



        theatres = cursor.fetchall()



        return render_template(

            "admin_theatres.html",

            theatres=theatres,

            admin_name=session.get("admin_name", "Administrator")

        )



    except Exception as error:



        print("Admin theatres error:", error)



        return "Unable to load theatres."



    finally:



        if cursor:

            cursor.close()



        if connection:

            connection.close()







# =========================================================

# ADMIN - UPDATE THEATRE

# =========================================================



@app.route("/admin-theatres/update/<int:theatre_id>", methods=["GET", "POST"])

def update_theatre(theatre_id):



    if not admin_required():

        return redirect(url_for("admin_login"))



    connection = None

    cursor = None



    try:



        connection = get_connection()

        cursor = connection.cursor(dictionary=True)



        # -------------------------------------------------

        # GET THEATRE

        # -------------------------------------------------



        if request.method == "GET":



            cursor.execute("""

                SELECT

                    theatre_id,

                    name,

                    location,

                    city

                FROM theatres

                WHERE theatre_id = %s

            """, (theatre_id,))



            theatre = cursor.fetchone()



            if not theatre:

                return "Theatre not found", 404



            return render_template(

                "admin_update_theatre.html",

                theatre=theatre

            )



        # -------------------------------------------------

        # UPDATE THEATRE

        # -------------------------------------------------



        name = request.form.get("name", "").strip()

        location = request.form.get("location", "").strip()

        city = request.form.get("city", "").strip()



        cursor.execute("""

            UPDATE theatres

            SET

                name = %s,

                location = %s,

                city = %s

            WHERE theatre_id = %s

        """, (

            name,

            location,

            city,

            theatre_id

        ))



        connection.commit()



        return redirect(url_for("admin_theatres"))



    except Exception as error:



        print("Update theatre error:", error)



        return "Unable to update theatre."



    finally:



        if cursor:

            cursor.close()



        if connection:

            connection.close()



# =========================================================

# PHASE 3 - DATA QUERYING AND ANALYTICS

# =========================================================



@app.route("/admin-analytics")

def admin_analytics():



    if not admin_required():

        return redirect(url_for("admin_login"))



    connection = None

    cursor = None



    try:

        connection = get_connection()

        cursor = connection.cursor(dictionary=True)



        # -------------------------------------------------

        # 1. JOIN: Booking information from a database view

        # -------------------------------------------------

        cursor.execute("""

            SELECT *

            FROM vw_booking_details

            ORDER BY booking_date DESC

        """)

        bookings = cursor.fetchall()



        # -------------------------------------------------

        # 2. JOIN + AGGREGATION: Movie booking statistics

        # -------------------------------------------------

        cursor.execute("""

            SELECT

                m.movie_id,

                m.title,

                COUNT(b.booking_id) AS total_bookings,

                COALESCE(SUM(b.total_amount), 0) AS booking_value

            FROM movies m

            LEFT JOIN shows s

                ON m.movie_id = s.movie_id

            LEFT JOIN bookings b

                ON s.show_id = b.show_id

            GROUP BY m.movie_id, m.title

            ORDER BY total_bookings DESC, m.title

        """)

        movie_stats = cursor.fetchall()



        # -------------------------------------------------

        # 3. SUBQUERY: Movies with above-average bookings

        # -------------------------------------------------

        cursor.execute("""

            SELECT

                m.movie_id,

                m.title,

                COUNT(b.booking_id) AS total_bookings

            FROM movies m

            JOIN shows s

                ON m.movie_id = s.movie_id

            JOIN bookings b

                ON s.show_id = b.show_id

            GROUP BY m.movie_id, m.title

            HAVING COUNT(b.booking_id) > (

                SELECT AVG(movie_booking_count)

                FROM (

                    SELECT COUNT(b2.booking_id) AS movie_booking_count

                    FROM movies m2

                    LEFT JOIN shows s2

                        ON m2.movie_id = s2.movie_id

                    LEFT JOIN bookings b2

                        ON s2.show_id = b2.show_id

                    GROUP BY m2.movie_id

                ) AS booking_averages

            )

            ORDER BY total_bookings DESC

        """)

        popular_movies = cursor.fetchall()



        # -------------------------------------------------

        # 4. NESTED QUERY: Movies that have no bookings

        # -------------------------------------------------

        cursor.execute("""

            SELECT m.movie_id, m.title

            FROM movies m

            WHERE NOT EXISTS (

                SELECT 1

                FROM shows s

                JOIN bookings b

                    ON s.show_id = b.show_id

                WHERE s.movie_id = m.movie_id

            )

            ORDER BY m.title

        """)

        unbooked_movies = cursor.fetchall()



        # -------------------------------------------------

        # 5. VIEW: Payment records

        # -------------------------------------------------

        cursor.execute("""

            SELECT *

            FROM vw_payment_summary

            ORDER BY payment_date DESC

        """)

        payments = cursor.fetchall()



        # -------------------------------------------------

        # 6. STORED PROCEDURE: Payment summary

        # -------------------------------------------------

        cursor.callproc("sp_payment_summary")



        payment_stats = []



        for result in cursor.stored_results():

            payment_stats = result.fetchall()



        # -------------------------------------------------

        # 7. STORED FUNCTION: Seat price subtotal

        # -------------------------------------------------

        cursor.execute("""

            SELECT

                b.booking_id,

                u.name AS customer_name,

                fn_booking_seat_total(b.booking_id) AS seat_total

            FROM bookings b

            JOIN users u

                ON b.user_id = u.user_id

            ORDER BY b.booking_date DESC

        """)

        seat_totals = cursor.fetchall()



        # -------------------------------------------------

        # SEND DATA TO THE PHASE 3 PAGE

        # -------------------------------------------------

        return render_template(

            "admin_analytics.html",

            admin_name=session.get(

                "admin_name", "Administrator"

            ),

            bookings=bookings,

            movie_stats=movie_stats,

            popular_movies=popular_movies,

            unbooked_movies=unbooked_movies,

            payments=payments,

            payment_stats=payment_stats,

            seat_totals=seat_totals

        )



    except Exception as error:

        print("PHASE 3 ANALYTICS ERROR:", error)

        return (

            "Unable to load analytics. "

            "Check the Flask terminal for the database error."

        )



    finally:

        if cursor:

            cursor.close()



        if connection:

            connection.close()

# ================= PHASE 4: MOVIES =================

@app.route("/movies")
def browse_movies():
    if not customer_required():
        return redirect(url_for("login"))

    connection = cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
           
SELECT
    s.show_id,
    s.show_date,
    s.show_time,
    s.ticket_price,
    s.status,
    m.movie_id,
    m.title,
    m.genre,
    m.duration,
    m.language,
    m.description,
    m.poster_url,
    sc.screen_name,
    t.name AS theatre_name
FROM movies m

LEFT JOIN shows s
    ON s.movie_id = m.movie_id
    AND s.show_date >= CURDATE()
    AND LOWER(COALESCE(s.status, 'active'))
        NOT IN ('cancelled', 'inactive')

LEFT JOIN screens sc
    ON sc.screen_id = s.screen_id

LEFT JOIN theatres t
    ON t.theatre_id = sc.theatre_id

ORDER BY m.title, s.show_date, s.show_time

        """)

        shows = cursor.fetchall()

        return render_template("movies.html", shows=shows)

    except Exception:
        app.logger.exception("Could not load movies")
        flash("Could not load movies. Check your movie and show database columns.", "error")
        return redirect(url_for("dashboard"))

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# ================= PHASE 4: SEAT SELECTION =================

@app.route("/shows/<int:show_id>/seats")
def select_seats(show_id):
    if not customer_required():
        return redirect(url_for("login"))

    connection = cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                s.show_id, s.show_date, s.show_time, s.ticket_price,
                m.title, sc.screen_id, sc.screen_name,
                t.name AS theatre_name
            FROM shows s
            JOIN movies m ON m.movie_id = s.movie_id
            JOIN screens sc ON sc.screen_id = s.screen_id
            JOIN theatres t ON t.theatre_id = sc.theatre_id
            WHERE s.show_id = %s
        """, (show_id,))

        show = cursor.fetchone()

        if not show:
            flash("Show not found.", "error")
            return redirect(url_for("browse_movies"))

        cursor.execute("""
            SELECT seat_id, seat_number, row_label, seat_type
            FROM seats
            WHERE screen_id = %s
            ORDER BY row_label, seat_number
        """, (show["screen_id"],))

        seats = cursor.fetchall()

        cursor.execute("""
            SELECT bd.seat_id
            FROM booking_details bd
            JOIN bookings b ON b.booking_id = bd.booking_id
            LEFT JOIN payments p ON p.booking_id = b.booking_id
            WHERE b.show_id = %s
              AND LOWER(COALESCE(b.status, 'confirmed'))
                  NOT IN ('cancelled', 'rejected')
              AND LOWER(COALESCE(p.payment_status, 'pending'))
                  NOT IN ('failed', 'cancelled', 'rejected')
        """, (show_id,))

        booked_seat_ids = {
            row["seat_id"] for row in cursor.fetchall()
        }

        return render_template(
            "seats.html",
            show=show,
            seats=seats,
            booked_seat_ids=booked_seat_ids
        )

    except Exception:
        app.logger.exception("Seat selection failed")
        flash("Unable to load seats. Check your database migration.", "error")
        return redirect(url_for("browse_movies"))

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# ================= PHASE 4: CHECKOUT =================

@app.route("/shows/<int:show_id>/checkout", methods=["POST"])
def checkout(show_id):
    if not customer_required():
        return redirect(url_for("login"))

    try:
        seat_ids = sorted(set(
            int(value) for value in request.form.getlist("seat_ids")
        ))
    except (TypeError, ValueError):
        flash("Invalid seat selection.", "error")
        return redirect(url_for("select_seats", show_id=show_id))

    if not seat_ids:
        flash("Please select at least one seat.", "error")
        return redirect(url_for("select_seats", show_id=show_id))

    connection = cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT s.show_id, s.show_date, s.show_time, s.ticket_price,
                   m.title, sc.screen_id, sc.screen_name,
                   t.name AS theatre_name
            FROM shows s
            JOIN movies m ON m.movie_id = s.movie_id
            JOIN screens sc ON sc.screen_id = s.screen_id
            JOIN theatres t ON t.theatre_id = sc.theatre_id
            WHERE s.show_id = %s
        """, (show_id,))

        show = cursor.fetchone()

        if not show:
            flash("Show not found.", "error")
            return redirect(url_for("browse_movies"))

        placeholders = ",".join(["%s"] * len(seat_ids))

        cursor.execute(
            f"""
            SELECT seat_id, seat_number, row_label, seat_type
            FROM seats
            WHERE screen_id = %s
              AND seat_id IN ({placeholders})
            """,
            tuple([show["screen_id"]] + seat_ids)
        )

        seats = cursor.fetchall()

        if len(seats) != len(seat_ids):
            flash("Some seats do not belong to this screen.", "error")
            return redirect(url_for("select_seats", show_id=show_id))

        cursor.execute(
            f"""
            SELECT bd.seat_id
            FROM booking_details bd
            JOIN bookings b ON b.booking_id = bd.booking_id
            LEFT JOIN payments p ON p.booking_id = b.booking_id
            WHERE b.show_id = %s
              AND bd.seat_id IN ({placeholders})
              AND LOWER(COALESCE(b.status, 'confirmed'))
                  NOT IN ('cancelled', 'rejected')
              AND LOWER(COALESCE(p.payment_status, 'pending'))
                  NOT IN ('failed', 'cancelled', 'rejected')
            """,
            tuple([show_id] + seat_ids)
        )

        if cursor.fetchall():
            flash("One or more seats are already booked.", "error")
            return redirect(url_for("select_seats", show_id=show_id))

        total = Decimal(str(show["ticket_price"])) * len(seats)

        return render_template(
            "checkout.html",
            show=show,
            seats=seats,
            total=total,
            seat_ids=seat_ids
        )

    except Exception:
        app.logger.exception("Checkout failed")
        flash("Unable to prepare checkout.", "error")
        return redirect(url_for("select_seats", show_id=show_id))

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# ================= PHASE 4: PAYMENT =================

@app.route("/shows/<int:show_id>/pay", methods=["POST"])
def process_simulated_payment(show_id):
    if not customer_required():
        return redirect(url_for("login"))

    try:
        seat_ids = sorted(set(
            int(value) for value in request.form.getlist("seat_ids")
        ))
    except (TypeError, ValueError):
        flash("Invalid seat selection.", "error")
        return redirect(url_for("select_seats", show_id=show_id))

    if not seat_ids:
        flash("Please select at least one seat.", "error")
        return redirect(url_for("select_seats", show_id=show_id))

    method = request.form.get("payment_method", "").strip()
    result = request.form.get("simulated_result", "success")

    allowed_methods = {
        "UPI (Demo)",
        "Card (Demo)",
        "Pay at Counter"
    }

    if method not in allowed_methods:
        flash("Invalid payment method.", "error")
        return redirect(url_for("select_seats", show_id=show_id))

    connection = cursor = None

    try:
        connection = get_connection()
        connection.start_transaction(isolation_level="READ COMMITTED")
        cursor = connection.cursor(dictionary=True)

        # Lock the show record while processing the booking.
        cursor.execute("""
            SELECT s.show_id, s.show_date, s.show_time, s.ticket_price,
                   m.title, sc.screen_id
            FROM shows s
            JOIN movies m ON m.movie_id = s.movie_id
            JOIN screens sc ON sc.screen_id = s.screen_id
            WHERE s.show_id = %s
            FOR UPDATE
        """, (show_id,))

        show = cursor.fetchone()

        if not show:
            connection.rollback()
            flash("Show not found.", "error")
            return redirect(url_for("browse_movies"))

        placeholders = ",".join(["%s"] * len(seat_ids))

        # Lock selected seats and ensure they belong to this show's screen.
        cursor.execute(
            f"""
            SELECT seat_id, seat_number, row_label, seat_type
            FROM seats
            WHERE screen_id = %s
              AND seat_id IN ({placeholders})
            ORDER BY seat_id
            FOR UPDATE
            """,
            tuple([show["screen_id"]] + seat_ids)
        )

        seats = cursor.fetchall()

        if len(seats) != len(seat_ids):
            connection.rollback()
            flash("A selected seat is invalid for this show.", "error")
            return redirect(url_for("select_seats", show_id=show_id))

        # Recheck availability inside the transaction.
        cursor.execute(
            f"""
            SELECT bd.seat_id
            FROM booking_details bd
            JOIN bookings b ON b.booking_id = bd.booking_id
            LEFT JOIN payments p ON p.booking_id = b.booking_id
            WHERE bd.show_id = %s
              AND bd.seat_id IN ({placeholders})
              AND LOWER(COALESCE(b.status, 'confirmed'))
                  NOT IN ('cancelled', 'rejected')
              AND LOWER(COALESCE(p.payment_status, 'pending'))
                  NOT IN ('failed', 'cancelled', 'rejected')
            """,
            tuple([show_id] + seat_ids)
        )

        if cursor.fetchall():
            connection.rollback()
            flash("A seat was booked by another customer. Select seats again.", "error")
            return redirect(url_for("select_seats", show_id=show_id))

        # Failure simulation tests rollback. Nothing is inserted.
        if result == "fail":
            connection.rollback()
            flash("Demo payment failed. No booking was created.", "error")
            return redirect(url_for("select_seats", show_id=show_id))

        price = Decimal(str(show["ticket_price"]))
        total = price * len(seats)

        write_cursor = connection.cursor()

        try:
            # 1. Create booking.
            write_cursor.execute("""
                INSERT INTO bookings
                    (user_id, show_id, total_amount, status)
                VALUES (%s, %s, %s, %s)
            """, (
                session["user_id"],
                show_id,
                total,
                "Confirmed"
            ))

            booking_id = write_cursor.lastrowid

            # 2. Add each selected seat.
            for seat in seats:
                write_cursor.execute("""
                    INSERT INTO booking_details
                        (booking_id, show_id, seat_id, price)
                    VALUES (%s, %s, %s, %s)
                """, (
                    booking_id,
                    show_id,
                    seat["seat_id"],
                    price
                ))

            # 3. Record the simulated payment.
            payment_status = (
                "Pending" if method == "Pay at Counter" else "Paid"
            )

            write_cursor.execute("""
                INSERT INTO payments
                    (booking_id, amount, payment_method, payment_status)
                VALUES (%s, %s, %s, %s)
            """, (
                booking_id,
                total,
                method,
                payment_status
            ))

            # Commit only after all inserts succeed.
            connection.commit()

        finally:
            write_cursor.close()

        return redirect(
            url_for("booking_confirmation", booking_id=booking_id)
        )

    except Exception:
        if connection:
            connection.rollback()

        app.logger.exception("Booking transaction failed")
        flash(
            "Booking failed and the transaction was rolled back. "
            "Check the application terminal for the database error.",
            "error"
        )
        return redirect(url_for("select_seats", show_id=show_id))

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# ================= PHASE 4: CONFIRMATION =================

@app.route("/bookings/<int:booking_id>/confirmation")
def booking_confirmation(booking_id):
    if not customer_required():
        return redirect(url_for("login"))

    connection = cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Customers can view only their own bookings.
        cursor.execute("""
            SELECT
                b.booking_id, b.user_id, b.booking_date,
                b.total_amount, b.status,
                m.title, s.show_date, s.show_time,
                sc.screen_name, t.name AS theatre_name,
                p.payment_method, p.payment_status
            FROM bookings b
            JOIN shows s ON s.show_id = b.show_id
            JOIN movies m ON m.movie_id = s.movie_id
            JOIN screens sc ON sc.screen_id = s.screen_id
            JOIN theatres t ON t.theatre_id = sc.theatre_id
            LEFT JOIN payments p ON p.booking_id = b.booking_id
            WHERE b.booking_id = %s
              AND b.user_id = %s
        """, (booking_id, session["user_id"]))

        booking = cursor.fetchone()

        if not booking:
            flash("Booking not found.", "error")
            return redirect(url_for("my_bookings"))

        cursor.execute("""
            SELECT
                bd.seat_id, bd.price,
                st.seat_number, st.row_label, st.seat_type
            FROM booking_details bd
            JOIN seats st ON st.seat_id = bd.seat_id
            WHERE bd.booking_id = %s
            ORDER BY st.row_label, st.seat_number
        """, (booking_id,))

        seats = cursor.fetchall()

        return render_template(
            "confirmation.html",
            booking=booking,
            seats=seats
        )

    except Exception:
        app.logger.exception("Confirmation page failed")
        flash("Could not load the confirmation.", "error")
        return redirect(url_for("my_bookings"))

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# ================= PHASE 4: MY BOOKINGS =================

@app.route("/my-bookings")
def my_bookings():
    if not customer_required():
        return redirect(url_for("login"))

    connection = cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                b.booking_id, b.booking_date,
                b.total_amount, b.status,
                m.title AS movie_title,
                s.show_date, s.show_time,
                p.payment_status
            FROM bookings b
            JOIN shows s ON s.show_id = b.show_id
            JOIN movies m ON m.movie_id = s.movie_id
            LEFT JOIN payments p ON p.booking_id = b.booking_id
            WHERE b.user_id = %s
            ORDER BY b.booking_date DESC
        """, (session["user_id"],))

        bookings = cursor.fetchall()

        return render_template(
            "my_bookings.html",
            bookings=bookings
        )

    except Exception:
        app.logger.exception("My bookings page failed")
        flash("Could not load your bookings.", "error")
        return redirect(url_for("dashboard"))

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# =========================================================

# RUN APPLICATION

# =========================================================

# ================= PHASE 4: ADMIN VALIDATION =================

@app.route("/admin-integrity")
def admin_integrity():
    if not admin_required():
        return redirect(url_for("admin_login"))

    connection = cursor = None
    checks = []

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # 1. Duplicate seat allocations for the same show.
        cursor.execute("""
            SELECT COUNT(*) AS issue_count
            FROM (
                SELECT show_id, seat_id
                FROM booking_details
                GROUP BY show_id, seat_id
                HAVING COUNT(*) > 1
            ) AS duplicates
        """)

        checks.append({
            "name": "Duplicate seat allocations",
            "count": cursor.fetchone()["issue_count"],
            "description": "A seat should be allocated at most once per show."
        })

        # 2. Booking amount versus sum of seat details.
        cursor.execute("""
            SELECT COUNT(*) AS issue_count
            FROM bookings b
            LEFT JOIN (
                SELECT booking_id, SUM(price) AS seat_total,
                       COUNT(*) AS seat_count
                FROM booking_details
                GROUP BY booking_id
            ) d ON d.booking_id = b.booking_id
            WHERE COALESCE(d.seat_count, 0) = 0
               OR ABS(COALESCE(d.seat_total, 0) - b.total_amount) > 0.01
        """)

        checks.append({
            "name": "Booking and seat total mismatch",
            "count": cursor.fetchone()["issue_count"],
            "description": "Each booking should have seats whose prices add up to the booking total."
        })

        # 3. Payment amount versus booking total.
        cursor.execute("""
            SELECT COUNT(*) AS issue_count
            FROM bookings b
            JOIN payments p ON p.booking_id = b.booking_id
            WHERE ABS(p.amount - b.total_amount) > 0.01
        """)

        checks.append({
            "name": "Payment amount mismatch",
            "count": cursor.fetchone()["issue_count"],
            "description": "The recorded payment amount should equal the booking total."
        })

        # 4. Seat belongs to the screen used by the booking's show.
        cursor.execute("""
            SELECT COUNT(*) AS issue_count
            FROM booking_details bd
            JOIN bookings b ON b.booking_id = bd.booking_id
            JOIN shows sh ON sh.show_id = b.show_id
            JOIN seats st ON st.seat_id = bd.seat_id
            WHERE bd.show_id <> b.show_id
               OR st.screen_id <> sh.screen_id
        """)

        checks.append({
            "name": "Seat and screen mismatch",
            "count": cursor.fetchone()["issue_count"],
            "description": "A booked seat must belong to the screen scheduled for that show."
        })

        return render_template(
            "admin_integrity.html",
            checks=checks
        )

    except Exception:
        app.logger.exception("Integrity validation failed")
        flash("Could not run validation. Check the database schema and migration.", "error")
        return redirect(url_for("admin_dashboard"))

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

print("\n--- ADMIN ROUTE CHECK ---")

for rule in app.url_map.iter_rules():
    if "integrity" in rule.rule or "integrity" in rule.endpoint:
        print(f"URL: {rule.rule} | Endpoint: {rule.endpoint}")

print(
    "Registered endpoint:",
    "admin_integrity" in app.view_functions
)

print("-------------------------\n")

if __name__ == "__main__":



    app.run(

        debug=True

    )
