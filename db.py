""" This file is resource manager.  
It helps in closing the open db connections automatically.
"""
import mysql.connector
from flask import current_app, g 
# g is global or request global using it store database connection for a specefic request

# the connection helper
def get_db():
    # check if open connection for the users current request
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host="localhost",  # current_app.config['DB_HOST']
            user="root",  # current_app.config['DB_USER']
            password="YOUR_PASSWORD_HERE",  # Don't put the real one!, #current_app.config['DB_PASSWORD']
            database="boxoffice",  # current_app.config['DB_NAME']
        )
        g.cursor = g.db.cursor(dictionary=True)
    return g.db, g.cursor

def close_db(e=None):
    #close the connection after request ends
    db = g.pop('db', None)
    cursor = g.pop('cursor', None)
    if cursor is not None:
        cursor.close()
    if db is not None:
        db.close()

def init_app(app):
    # Register the close_db function with the app
    app.teardown_appcontext(close_db)
