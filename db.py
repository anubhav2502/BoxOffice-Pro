import mysql.connector
import os
from flask import current_app, g


# The connection helper
def get_db():
    # Check if there's already an open connection for the current request
    if "db" not in g:
        # Check if we are in a cloud environment (Railway/Render)
        if os.environ.get("DB_HOST"):
            # Cloud Connection (Railway)
            g.db = mysql.connector.connect(
                host=os.environ.get("DB_HOST"),
                user=os.environ.get("DB_USER"),
                password=os.environ.get("DB_PASSWORD"),
                database=os.environ.get("DB_NAME"),
                port=int(os.environ.get("DB_PORT", 3306)),
            )
        else:
            # Local Connection (Your Laptop)
            g.db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Your Password",  # Update with your local pass
                database="boxoffice",
            )

        # We use dictionary=True so we can access columns by name (e.g., row['movie_name'])
        g.cursor = g.db.cursor(dictionary=True)

    return g.db, g.cursor


def close_db(e=None):
    # Close the connection after the request ends
    db = g.pop("db", None)
    cursor = g.pop("cursor", None)

    if cursor is not None:
        cursor.close()
    if db is not None:
        db.close()


def init_app(app):
    # Register the close_db function to run automatically after every request
    app.teardown_appcontext(close_db)
