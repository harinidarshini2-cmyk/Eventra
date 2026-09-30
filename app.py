from flask import Flask, render_template, request
from database import create_tables, get_connection
from cache import get_cache, set_cache
app = Flask(__name__)

# Create database tables when the application starts
create_tables()


# =========================================================
# HOME PAGE
# =========================================================
@app.route("/")
def home():

    print("HOME ROUTE CALLED")

    events = get_cache("events")

    if events is None:

        print("LOADING EVENTS FROM DATABASE")

        connection = get_connection()

        events = connection.execute("""
            SELECT *
            FROM events
            ORDER BY date
        """).fetchall()

        connection.close()

        set_cache("events", events)

    return render_template(
        "index.html",
        events=events
    )
# =========================================================
# EVENT DETAILS PAGE
# =========================================================

@app.route("/event/<int:event_id>")
def event_details(event_id):

    connection = get_connection()

    event = connection.execute("""
        SELECT *
        FROM events
        WHERE id = ?
    """, (event_id,)).fetchone()

    connection.close()

    if event is None:
        return "Event not found", 404

    return render_template(
        "event_details.html",
        event=event
    )


# =========================================================
# REGISTER FOR EVENT
# =========================================================

@app.route("/register/<int:event_id>", methods=["GET", "POST"])
def register(event_id):

    connection = get_connection()

    # Find event
    event = connection.execute("""
        SELECT *
        FROM events
        WHERE id = ?
    """, (event_id,)).fetchone()

    # Event not found
    if event is None:

        connection.close()

        return "Event not found", 404


    # =====================================================
    # FORM SUBMITTED
    # =====================================================

    if request.method == "POST":

        # Get form data
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()


        # -------------------------------------------------
        # CHECK EMPTY FIELDS
        # -------------------------------------------------

        if not name or not email or not phone:

            connection.close()

            return render_template(
                "register.html",
                event=event,
                error="Please fill in all the fields."
            )


        # -------------------------------------------------
        # CHECK DUPLICATE REGISTRATION
        # -------------------------------------------------

        existing_registration = connection.execute("""
            SELECT id
            FROM registrations
            WHERE event_id = ?
            AND email = ?
        """, (event_id, email)).fetchone()


        if existing_registration:

            connection.close()

            return render_template(
                "register.html",
                event=event,
                error="You have already registered for this event."
            )


        # -------------------------------------------------
        # CHECK AVAILABLE SEATS
        # -------------------------------------------------

        if event["available_seats"] <= 0:

            connection.close()

            return render_template(
                "register.html",
                event=event,
                error="Sorry, this event is fully booked."
            )


        # -------------------------------------------------
        # INSERT REGISTRATION
        # -------------------------------------------------

        cursor = connection.execute("""
            INSERT INTO registrations
            (
                event_id,
                name,
                email,
                phone,
                registered_at
            )
            VALUES (?, ?, ?, ?, datetime('now'))
        """, (
            event_id,
            name,
            email,
            phone
        ))


        # Get generated registration ID
        registration_id = cursor.lastrowid


        # -------------------------------------------------
        # REDUCE AVAILABLE SEATS
        # -------------------------------------------------

        connection.execute("""
            UPDATE events
            SET available_seats = available_seats - 1
            WHERE id = ?
        """, (event_id,))


        # Save database changes
        connection.commit()

        connection.close()


        # -------------------------------------------------
        # SHOW SUCCESS PAGE
        # -------------------------------------------------

        return render_template(
            "registration_success.html",
            registration_id=registration_id,
            name=name,
            event=event
        )


    # =====================================================
    # FIRST OPENING OF REGISTRATION PAGE
    # =====================================================

    connection.close()

    return render_template(
        "register.html",
        event=event
    )


# =========================================================
# API - GET ALL EVENTS
# =========================================================

@app.route("/api/events", methods=["GET"])
def api_events():

    connection = get_connection()

    events = connection.execute("""
        SELECT *
        FROM events
        ORDER BY date
    """).fetchall()

    connection.close()


    event_list = []

    for event in events:

        event_list.append({
            "id": event["id"],
            "name": event["name"],
            "category": event["category"],
            "description": event["description"],
            "date": event["date"],
            "time": event["time"],
            "venue": event["venue"],
            "capacity": event["capacity"],
            "available_seats": event["available_seats"]
        })


    return {
        "success": True,
        "events": event_list
    }


# =========================================================
# API - GET SINGLE EVENT
# =========================================================

@app.route("/api/events/<int:event_id>", methods=["GET"])
def api_event(event_id):

    connection = get_connection()

    event = connection.execute("""
        SELECT *
        FROM events
        WHERE id = ?
    """, (event_id,)).fetchone()

    connection.close()


    if event is None:

        return {
            "success": False,
            "message": "Event not found"
        }, 404


    return {
        "success": True,
        "event": {
            "id": event["id"],
            "name": event["name"],
            "category": event["category"],
            "description": event["description"],
            "date": event["date"],
            "time": event["time"],
            "venue": event["venue"],
            "capacity": event["capacity"],
            "available_seats": event["available_seats"]
        }
    }


# =========================================================
# API - REGISTER USER
# =========================================================

@app.route("/api/register", methods=["POST"])
def api_register():

    data = request.get_json()


    # Check request body
    if not data:

        return {
            "success": False,
            "message": "Request body is required"
        }, 400


    event_id = data.get("event_id")
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    phone = data.get("phone", "").strip()


    # -----------------------------------------------------
    # VALIDATE INPUT
    # -----------------------------------------------------

    if not event_id or not name or not email or not phone:

        return {
            "success": False,
            "message": "event_id, name, email and phone are required"
        }, 400


    connection = get_connection()


    # -----------------------------------------------------
    # FIND EVENT
    # -----------------------------------------------------

    event = connection.execute("""
        SELECT *
        FROM events
        WHERE id = ?
    """, (event_id,)).fetchone()


    if event is None:

        connection.close()

        return {
            "success": False,
            "message": "Event not found"
        }, 404


    # -----------------------------------------------------
    # CHECK DUPLICATE
    # -----------------------------------------------------

    existing = connection.execute("""
        SELECT id
        FROM registrations
        WHERE event_id = ?
        AND email = ?
    """, (event_id, email)).fetchone()


    if existing:

        connection.close()

        return {
            "success": False,
            "message": "You have already registered for this event."
        }, 409


    # -----------------------------------------------------
    # CHECK SEATS
    # -----------------------------------------------------

    if event["available_seats"] <= 0:

        connection.close()

        return {
            "success": False,
            "message": "Event is fully booked."
        }, 409


    # -----------------------------------------------------
    # INSERT REGISTRATION
    # -----------------------------------------------------

    cursor = connection.execute("""
        INSERT INTO registrations
        (
            event_id,
            name,
            email,
            phone,
            registered_at
        )
        VALUES (?, ?, ?, ?, datetime('now'))
    """, (
        event_id,
        name,
        email,
        phone
    ))


    registration_id = cursor.lastrowid


    # -----------------------------------------------------
    # REDUCE SEATS
    # -----------------------------------------------------

    connection.execute("""
        UPDATE events
        SET available_seats = available_seats - 1
        WHERE id = ?
    """, (event_id,))


    connection.commit()

    connection.close()


    # -----------------------------------------------------
    # API RESPONSE
    # -----------------------------------------------------

    return {
        "success": True,
        "message": "Registration successful",
        "registration_id": f"EVT-{registration_id:05d}",
        "event": event["name"],
        "name": name
    }, 201


# =========================================================
# START FLASK SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
                host="0.0.0.0",
        port=5000,
        debug=True
    )