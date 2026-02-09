
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_db
import re
from datetime import datetime,  timedelta

def get_movie():
    db, cursor = get_db()
    cursor.execute("SELECT * FROM movie")
    movie_list = cursor.fetchall()
    return movie_list

def add_movie_db(name, language, category, r_date_str):
    #  vlaidations
    # A. empty check
    if not name or not language or not category or not r_date_str:
        return False, "Please fill all the fields!"
    # B. Length and content
    if not (10<=len(name)<=50) or not re.match(r'^[a-zA-Z0-9]+$', name):
        return False, "Movie name must be 10 to 50 charecters (Alphabets/Digits only)"
    # C. Date Validation
    try:
        r_date = datetime.strptime(r_date_str, '%Y-%m-%d').date()
        min_date = datetime.now().date() + timedelta(days=5)
        if r_date <= min_date:
            return False, "Release date must be atleast 5 days in future."
    except ValueError:
        return False,  "Invalid date format."
    db, cursor = get_db()
    to_return = 0
    try:
        #check for duplicate
        cursor.execute("SELECT * FROM movie WHERE LOWER(movie_name) = LOWER(%s)", (name,))
        if cursor.fetchone():
            return False, "Movie details already present"

        #insert 
        query = "INSERT INTO movie (movie_name, language, category, release_date) VALUES (%s,%s,%s,%s)"
        cursor.execute(query, (name, language, category, r_date_str))
        db.commit()

        return True, "Movie details added successfully"
    except Exception as e:
        db.rollback()
        return False, f"Error:{str(e)}"

def delete_movie_db(movie_name):
    db, cursor = get_db()
    # validate movie name
    if not movie_name:
        return False, "Please select the movie to bo deleted"

    else:
        try:
            #delete query
            cursor.execute("DELETE FROM movie WHERE movie_name = %s", (movie_name,))
            db.commit()
            return True, "Movie deleted successfully"
            
        except Exception as e:
            db.rollback()
            return False, f"Error: Could not delete. This movie currently scheduled! "

def fetch_filterd_movies(filters=None):
    db, cursor = get_db()
    #Fetch movie names for dropdown
    cursor.execute("SELECT movie_name FROM movie")
    all_movie_names = cursor.fetchall()
    #base query 
    base_query = "SELECT * FROM movie WHERE 1=1"
    params = []

    if filters:
        if filters.get('movie_name'):
            base_query += " AND movie_name =%s "
            params.append(filters.get('movie_name'))
        if filters.get('language'):
            base_query += " AND language =%s "
            params.append(filters.get('language'))
        if filters.get('category'):
            base_query += " AND category =%s "
            params.append(filters.get('category'))
        if filters.get('release_date'):
            base_query += " AND release_date =%s "
            params.append(filters.get('release_date'))

    #Executing final query
    final_query = base_query + " ORDER BY release_date DESC "
    cursor.execute(base_query, tuple(params))
    movie_list = cursor.fetchall()

    return movie_list, all_movie_names

def add_theater_db(data):
    # extract data from data
    t_name = data.get('theater_name')
    owner = data.get('owner_email')
    show_time = data.get('show_time')
    capacity = data.get('seat_capacity')
    price = data.get('price')

    # Vlaidations
    try:
        capacity = int(capacity)
        price = float(price)
    except ValueError:
        
        return False, "Invalid number format for Capacity of Price."
    # Rule A capacity >= 100
    if capacity < 100:
        
        return False, "Capacity must be between 100 to 500."
    # Rule B Price >= 100
    if price < 100:
        
        return False, "Price must be between 100 to 500."
    # Databse checks
    db , cursor = get_db()
    try:
        #check 1 Owner exists
        cursor.execute("SELECT * FROM user WHERE email_address = %s and role = 'tech_admin'", (owner,))
        if not cursor.fetchone():
            cursor.execute("SELECT * FROM user WHERE email_address = %s ", (owner,))
            if cursor.fetchone():
                return False, f"ERROR: Entered Email {owner} is not a Tech Admin."
            
            return False, f"ERROR: User {owner} does not exist. Please register the owner first"

        #check 2 duplicate theater name
        cursor.execute("SELECT * FROM theater WHERE theater_name = %s ", (t_name,))
        if cursor.fetchone():
        
            return False, f"ERROR: Theater {t_name} already exists."
        # Insert theater
        query = """INSERT INTO theater (theater_name, owner_email,show_time, seat_capacity, price_per_ticket)
                    VALUES (%s,%s,%s,%s,%s)"""
        cursor.execute(query, (t_name, owner,show_time, capacity, price))
        db.commit()
        
        return True, "Theater added successfully"
        
    except Exception as e : 
        db.rollback()
        return False, f"Database error: {str(e)}"


def fetch_filterd_theater(filters=None):
    db, cursor = get_db()
    #Fetch Theater names for dropdown
    cursor.execute("SELECT theater_name FROM theater")
    all_theater_names = cursor.fetchall()
    #base query 
    base_query = "SELECT * FROM theater WHERE 1=1 "
    params = []
    if filters:
       #Addding conditions to select query if filters 
        if filters.get('theater_name'):
            base_query += " AND theater_name =%s "
            params.append(filters.get('theater_name'))
        if filters.get('owner_email'):
            base_query += " AND owner_email =%s "
            params.append(filters.get('owner_email')) 
    #Executing final query
    final_query = base_query + " ORDER BY theater_name "
    cursor.execute(base_query, tuple(params))
    theater_list = cursor.fetchall()
    return theater_list, all_theater_names