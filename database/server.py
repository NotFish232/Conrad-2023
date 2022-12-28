import sys
import sqlite3
from pathlib import Path
from datetime import datetime
from flask import Flask, request, Response
from typing import Callable
from functools import wraps

app = Flask(__name__)
db_filename = Path(__file__).with_name("sqlite.db").absolute()
con = sqlite3.connect(db_filename, check_same_thread=False)


def authorization_required() -> Callable:

    def _authorization_required(func: Callable) -> Callable:

        @wraps(func)
        def __authorization_required(*args, **kwargs) -> tuple[dict, int]:

            username = request.args.get("username")
            password = request.args.get("password")

            if not username or not password:
                return {"error": "unauthorized request, please provide credentials"}, 401

            curser = con.execute("""
            SELECT * FROM Users WHERE username = ? AND password = ?
            """, (username, password))

            if curser.fetchone() is None:
                return {"error": "unathorized request, invalid credentials"}, 401

            return func(*args, **kwargs)

        return __authorization_required

    return _authorization_required


@app.after_request
def add_headers(response: Response) -> Response:
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route("/get_users", methods=["get"])
@authorization_required()
def get_users() -> tuple[dict, int]:

    cursor = con.execute("""
    SELECT username, email, id FROM Users;
    """)

    users = cursor.fetchall()

    json = {
        "users": [{"username": u[0], "email": u[1], "id": u[2]} for u in users],
        "count": len(users),
    }

    return json, 200


@app.route("/get_user/<int:id>", methods=["get"])
@authorization_required()
def get_user(id: int) -> tuple[dict, int]:

    curser = con.execute("""
    SELECT username, email FROM User where id = ?;
    """, (id, ))

    user = curser.fetchone()

    if user is None:
        return {"error", f"no user found with id \"{id}\""}, 400

    return {"username": user[0], "email": user[1]}, 200


@app.route("/delete_user/<int:id>", methods=["delete"])
@authorization_required()
def delete_user(id: int) -> tuple[dict, int]:

    curser = con.execute("""
    SELECT * FROM Users where id = ?;
    """, (id, ))

    if curser.fetchone() is None:
        return {"error": f"no user found with id \"{id}\""}, 400

    con.execute("""
    DELETE FROM Users WHERE id = ?
    """, (id, ))
    con.commit()

    return {"message": f"successfully deleted user with id \"{id}\""}, 200


@app.route("/add_user", methods=["post"])
def add_user() -> tuple[dict, int]:

    username = request.args.get("username")
    password = request.args.get("password")
    email = request.args.get("email")

    if not username or not password or not email:
        return {"error": "missing username, password, or email"}, 400

    curser = con.execute("""
    SELECT * FROM Users WHERE username = ? or email = ?;
    """, (username, email))

    user = curser.fetchone()

    if user is not None:
        return {"error": "supplied username or email is already in use"}

    con.execute("""
    INSERT INTO Users(username, password, email) VALUES (?, ?, ?);
    """, (username, password, email))
    con.commit()

    return {"message": "successfully added user to database"}, 201


@app.route("/get_locations", methods=["get"])
@authorization_required()
def get_locations() -> tuple[dict, int]:

    curser = con.execute("""
    SELECT address, latitude, longitude, id from Locations;
    """)

    locations = curser.fetchall()

    json = {
        "locations": [{"address": l[0], "latitude": l[1], "longitude": l[2], "id": l[3]} for l in locations],
        "count": len(locations)
    }
    return json, 200


@app.route("/get_location/<int:id>", methods=["get"])
@authorization_required()
def get_location(id: int) -> tuple[dict, int]:

    curser = con.execute("""
    SELECT address, latitude, longitude FROM Locations where id = ?;
    """, (id, ))

    location = curser.fetchone()

    if location is None:
        return {"error": f"no location found with id \"{id}\""}, 400

    return {"address": location[0], "latitude": location[1], "longitude": location[2]}, 200


@app.route("/delete_location/<int:id>", methods=["delete"])
@authorization_required()
def delete_location(id: int) -> tuple[dict, int]:

    curser = con.execute("""
    SELECT * FROM Locations where id = ?
    """, (id, ))

    if curser.fetchone() is None:
        return {"error": f"no location found with id \"{id}\""}, 400

    con.execute("""
    DELETE FROM Locations WHERE id = ?
    """, (id, ))
    con.commit()

    return {"message": f"successfully deleted location with id \"{id}\""}, 200


@app.route("/add_location", methods=["post"])
@authorization_required()
def add_location() -> tuple[dict, int]:
    address = request.args.get("address")
    latitude = request.args.get("latitude")
    longitude = request.args.get("longitude")

    if not address or not latitude or not longitude:
        return {"error": "missing address, latitude, or longitudes"}, 400

    curser = con.execute("""
    SELECT * FROM Locations WHERE address = ?;
    """, (address, ))

    location = curser.fetchone()

    if location is not None:
        return {"error": "supplied address is already in use"}

    con.execute("""
    INSERT INTO Locations(address, latitude, longitude) VALUES (?, ?, ?);
    """, (address, latitude, longitude))
    con.commit()

    return {"message": "successfully added location to database"}, 201


@app.route("/get_foods", methods=["get"])
@authorization_required()
def get_foods() -> tuple[dict, int]:

    curser = con.execute("""
    SELECT description, id, location_id, batch_id FROM Foods;
    """)

    foods = curser.fetchall()

    json = {
        "foods": [{
            "description": f[0],
            "id": f[1],
            "location": f[2],
            "batch": f[3]
        } for f in foods],
        "count": len(foods)
    }

    return json, 200


@app.route("/get_food/<int:id>", methods=["get"])
@authorization_required()
def get_food(id: int) -> tuple[dict, int]:

    curser = con.execute("""
    SELECT description, location_id, batch_id from Foods where id = ?;
    """, (id, ))

    food = curser.fetchone()

    if food is None:
        return {"error": f"no food found with id {id}"}, 400

    return {"description": food[0], "location": food[1], "batch": food[2]}, 200


@app.route("/get_foods_at_location/<int:id>", methods=["get"])
@authorization_required()
def get_foods_at_location(id: int) -> tuple[dict, int]:

    curser = con.execute("""
    SELECT * FROM Locations where id = ?;
    """, (id, ))

    if curser.fetchone() is None:
        return {"error", f"no location found with id \"{id}\""}, 400

    curser = con.execute("""
    SELECT description, id, batch_id FROM Foods WHERE location_id = ?;
    """, (id, ))

    foods = curser.fetchall()

    json = {
        "foods": [{
            "description": f[0],
            "id": f[1],
            "batch": f[2]
        } for f in foods],
        "count": len(foods)
    }

    return json, 200


@app.route("/get_foods_from_batch/<int:id>", methods=["get"])
@authorization_required()
def get_foods_from_batch(id: int) -> tuple[dict, int]:

    curser = con.execute("""
    SELECT description, id, location_id FROM Foods WHERE batch_id = ?;
    """, (id, ))

    foods = curser.fetchall()

    json = {
        "foods": [{
            "description": f[0],
            "id": f[1],
            "location": f[2]
        } for f in foods],
        "count": len(foods)
    }

    return json, 200


@app.route("/delete_food/<int:id>", methods=["delete"])
@authorization_required()
def delete_food(id: int) -> tuple[dict, int]:

    curser = con.execute("""
    SELECT * FROM Foods where id = ?;
    """, (id, ))

    if curser.fetchone() is None:
        return {"error": f"no food found with id \"{id}\""}, 400

    con.execute("""
    DELETE FROM Foods where id = ?;
    """, (id, ))
    con.commit()

    return {"message", f"successfully deleted food with id \"{id}\""}, 200


@app.route("/add_food", methods=["post"])
@authorization_required()
def add_food() -> tuple[dict, int]:

    description = request.args.get("description")
    location = request.args.get("location")
    batch = request.args.get("batch", None)

    if not description or not location:
        return {"error": "missing description"}, 400

    curser = con.execute("""
    SELECT * FROM Locations WHERE id = ?;
    """, (location, ))

    if curser.fetchone() is None:
        return {"error": f"no location with id \"{id}\""}, 400

    if batch is None:
        curser = con.execute("""
        SELECT IFNULL(MAX(batch_id), 0) + 1 FROM Foods;
        """)
        batch = curser.fetchone()[0]

 
    con.execute("""
    INSERT INTO Foods (description, location_id, batch_id) VALUES (?, ?, ?);
    """, (description, location, batch))
    con.commit()

    return {"message": "successfully added food to database"}, 201


@app.route("/update_food_location/<int:id>", methods=["post"])
@authorization_required()
def update_food_location(id: int) -> tuple[dict, int]:

    location = request.args.get("location")

    if not location:
        return {"error": "missing location"}, 400

    curser = con.execute("""
    SELECT * FROM Foods where id = ?;
    """, (id, ))

    if curser.fetchone() is None:
        return {"error": f"food not found with id \"{id}\""}, 400

    curser = con.execute("""
    SELECT * FROM Locations where id = ?;
    """, (location, ))

    if curser.fetchone() is None:
        return {"error": f"location not found with id \"{id}\""}, 400

    curser = con.execute("""
    SELECT location_id from Foods where id = ?;
    """, (id, ))

    previous = curser.fetchone()[0]

    if previous == location:
        return {"error": "can not update location to same location"}, 400

    con.execute("""
    UPDATE Foods
    SET location_id = ?
    WHERE id = ?;
    """, (location, id))
    con.execute("""
    INSERT INTO History (food_id, source_id, destination_id, date) VALUES (?, ?, ?, ?);
    """, (id, previous, location, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    con.commit()

    return {"message": f"successfully updated food with id \"{id}\""}, 201


@app.route("/get_history", methods=["get"])
@authorization_required()
def get_history() -> tuple[dict, int]:

    curser = con.execute("""
    SELECT food_id, source_id, destination_id, id, date FROM History;
    """)

    history = curser.fetchall()

    json = {
        "history": [{
            "food": h[0],
            "source": h[1],
            "destination": h[2],
            "id": h[3],
            "date": h[4]
        } for h in history],
        "count": len(history)
    }

    return json, 200


@app.route("/get_history_of_food/<int:id>", methods=["get"])
@authorization_required()
def get_history_of_food(id: int) -> tuple[dict, int]:

    curser = con.execute("""
    SELECT * FROM Foods WHERE id = ?;
    """, (id, ))

    if curser.fetchone() is None:
        return {"error": f"food not found with id \"{id}\""}, 400

    curser = con.execute("""
    SELECT source_id, destination_id, id, date FROM History where food_id = ?;
    """,  (id, ))

    history = curser.fetchall()

    json = {
        "history": [{
            "source": h[0],
            "destination": h[1],
            "id": h[2],
            "date": h[3]
        } for h in history],
        "count": len(history)
    }

    return json, 200


@app.route("/get_history_of_location/<int:id>", methods=["get"])
@authorization_required()
def get_history_of_location(id: int) -> tuple[dict, int]:

    curser = con.execute("""
    SELECT * FROM Locations WHERE id = ?;
    """, (id, ))

    if curser.fetchone() is None:
        return {"error": f"location not found with id \"{id}\""}, 400

    curser = con.execute("""
    SELECT
        food_id,
        id,
        date,
        CASE WHEN source_id = ? THEN "departed" ELSE "arrived" END
    FROM History WHERE source_id = ? or destination_id = ?;
    """, (id, ))

    history = curser.fetchall()

    json = {
        "history": [{
            "food": h[0],
            "id": h[1],
            "date": h[2],
            "type": h[3]
        } for h in history],
        "count": len(history)
    }

    return json, 200

@app.route("/get_number_of_batches", methods=["get"])
@authorization_required()
def get_number_of_batches() -> tuple[dict, int]:

    curser = con.execute("""
    SELECT COUNT(DISTINCT batch_id) FROM Foods;
    """)

    count = curser.fetchone()[0]

    return {"count": count}, 200


def initialize_database() -> None:

    con.execute("""
    CREATE TABLE IF NOT EXISTS Users(
        id         INTEGER PRIMARY KEY NOT NULL,
        username  nvarchar(255) UNIQUE NOT NULL,
        password         nvarchar(255) NOT NULL,
        email     nvarchar(255) UNIQUE NOT NULL 
    );
    """)

    con.execute("""
    CREATE TABLE IF NOT EXISTS Locations(
        id       INTEGER PRIMARY KEY  NOT NULL,
        address  nvarchar(255) UNIQUE NOT NULL,
        latitude                 REAL NOT NULL,
        longitude                REAL NOT NULL
    );
    """)

    con.execute("""
    CREATE TABLE IF NOT EXISTS Foods(
        id     INTEGER PRIMARY KEY NOT NULL,
        batch_id           INTEGER NOT NULL,
        description   nvarchar(255) NOT NULL,
        location_id        INTEGER NOT NULL,
        FOREIGN KEY           (location_id)
        REFERENCES  Locations (location_id)
    );
    """)

    con.execute("""
    CREATE TABLE IF NOT EXISTS History(
        id        INTEGER PRIMARY KEY NOT NULL,
        date                 DATETIME NOT NULL,
        food_id               INTEGER NOT NULL,
        source_id             INTEGER NOT NULL,
        destination_id        INTEGER NOT NULL,
        FOREIGN KEY                  (food_id)
        REFERENCES             Foods (food_id),
        FOREIGN KEY                (source_id)
        REFERENCES       Locations (source_id),
        FOREIGN KEY           (destination_id)
        REFERENCES  Locations (destination_id)
    );
    """)


def main() -> None:
    initialize_database()
    host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
    app.run(host=host, port=port)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        con.close()
