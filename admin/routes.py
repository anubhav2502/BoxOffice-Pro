from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_db
import mysql.connector
import re
from datetime import datetime,  timedelta
from admin.service import add_movie_db, delete_movie_db, get_movie, fetch_filterd_movies, add_theater_db, fetch_filterd_theater
#creating blueprint
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/home')
def admin_home():
    if 'user_role' not in session or session['user_role'] != 'admin':
        flash('Unauthorized Access!', "danger")
        return redirect(url_for('auth.login'))
    return render_template('admin/home.html')

@admin_bp.route('/add_movie', methods=['GET','POST'])
def add_movie():
    # Security check if user in session
    if 'user_role' not in session or session['user_role'] != 'admin':
        flash('Unauthorized Access!', "danger")
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        #Fetching  data
        name = request.form.get('movie_name')
        language = request.form.get('language')
        category = request.form.get('category')
        r_date_str = request.form.get('release_date')

        success, msg = add_movie_db(name, language, category, r_date_str)
        if not success:
            flash(msg, 'danger')
        else:
            flash(msg, 'success')
    # for 5 days rule check from today
    today = datetime.now().date().isoformat()
    min_date = datetime.now().date() + timedelta(days=5)
    min_date_str = min_date.isoformat()
    return render_template('admin/add_movie.html',min_date = min_date_str)

@admin_bp.route('/delete_movie', methods=['GET','POST'])
def delete_movie():
    #security check
    if 'user_role' not in session or session['user_role'] != 'admin':
        flash('Unauthorized Access!', "danger")
        return redirect(url_for('auth.login'))
    
    # Handle Deletion 
    if request.method=='POST':
        # get data from form
        movie_name = request.form.get('selected_movie')
        success, msg = delete_movie_db(movie_name)
        if not success:
            flash(msg, 'danger')
        else:
            flash(msg, 'success')
        return redirect(url_for('admin.delete_movie'))
    #Handle viewing (GET)
    #fetch data to view in tables(movies list)
    movie_list = get_movie()
    return render_template('admin/delete_movie.html', movies = movie_list)

@admin_bp.route('/view_movie', methods=['GET','POST'])
def view_movie():
    if 'user_role' not in session or session['user_role'] != 'admin':
        flash('Unauthorized Access!', "danger")
        return redirect(url_for('auth.login'))
    
    #handeling filters
    filters={}
    if request.method == 'POST':
        filters ={
            'movie_name': request.form.get('movie_name'),
            'language': request.form.get('language'),
            'category': request.form.get('category'),
            'release_date': request.form.get('release_date')
        }
        
    # getting data from service layer
    movie_list, all_movie_names = fetch_filterd_movies(filters)           
    return render_template('admin/view_movie.html', movies = movie_list, movie_name = all_movie_names )

@admin_bp.route('/add_theater', methods=['GET','POST'])
def add_theater():
    if 'user_role' not in session or session['user_role'] != 'admin':
        flash('Unauthorized Access!', "danger")
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        data = {
            'theater_name': request.form.get('theater_name'),
            'owner_email': request.form.get('owner_email'),
            'show_time': request.form.get('show_time'),
            'seat_capacity': request.form.get('seat_capacity'),
            'price':  request.form.get('price')
        }

        # fetch data from form
        success, msg = add_theater_db(data)
        if success:
            flash(msg, "success")
            return redirect(url_for('admin.add_theater'))
        else:
            flash(msg, "danger")
            return render_template('admin/add_theater.html')
    #Get Request
    return render_template('admin/add_theater.html')

@admin_bp.route('/view_theater', methods=['GET','POST'])
def view_theater():
    if 'user_role' not in session or session['user_role'] != 'admin':
        flash('Unauthorized Access!', "danger")
        return redirect(url_for('auth.login'))
    
    #handeling filters
    filters = {}
    if request.method == 'POST':
        #fetching filters
        filters={
            'theater_name': request.form.get('theater_name'),
            'owner_email': request.form.get('owner_email')   
        }
        
    # Get Request handelling and fetching filterd data for post request   
    theater_list, all_theater_names = fetch_filterd_theater(filters)
        
    return render_template('admin/view_theater.html', theaters = theater_list, theater_names = all_theater_names )
