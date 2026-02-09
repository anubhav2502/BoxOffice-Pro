from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_db
import mysql.connector
import re
#creating blueprint
auth_bp = Blueprint('auth', __name__)

#login route
@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if 'user_role' in session:
        return redirect_based_on_role(session['user_role'])
    
    if request.method == 'POST':
        role = request.form.get('role')
        username = request.form.get('uname')
        password = request.form.get('password')
        #validation field empty?
        if not role or not username or not password:
            flash('Pleas Fill all field!', 'danger')
            return render_template("auth/login.html")

        # databse check 
        db, cursor = get_db()

        query = "SELECT * FROM user WHERE email_address = %s AND role = %s"
        cursor.execute(query, (username, role))
        user = cursor.fetchone()

        #verify credentials

        if user:
            #check password 
            if user['password'] == password:
                session['user_email'] = user['email_address']
                session['user_role'] = user['role']
                session['user_name'] = user['user_name']
                return redirect_based_on_role(role)
            else:
                flash("Please enter correct password", "danger")
        else:
            flash("You are not authorized to login or Invalid credentials!", "danger")
    return render_template('auth/login.html')

#helper redirect based on role

def redirect_based_on_role(role):
    if role == "admin":
        return redirect(url_for('admin.admin_home'))
    elif role == "user":
        return redirect(url_for('customer.customer_home'))
    elif role == "tech_admin" :
        return redirect(url_for('tech_admin.tech_admin_home'))
    return redirect(url_for('customer.customer_home'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/signup',methods=['GET','POST'])   
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        mobile = request.form['mobile']
        dob = request.form['dob']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # sequrity questions
        security_code = request.form['security_question']
        question_map = {
            'q1': 'Which is your favorite book?',
            'q2': 'What was the name of your favorite pet?', 
            'q3': 'What is your favorite food?',
            'q4': 'What city were you born in?',
            'q5': 'Where is your favorite place to vacation?'       
        }
        sec_question = question_map.get(security_code, 'What is your favorite book?')
        sec_answer = request.form['security_answer']
        print(email, username, mobile, dob, password, sec_question, sec_answer)
        error = None

        if not re.match(r'^[a-zA-Z]{1,20}$', username):
            error = 'Username must be Alphabet only (1-10 characters)'
        elif not re.match(r'^[a-zA-Z0-9]+@[a-z]+\.[a-z]+$',email):
            error = "Incorrect Email address"
        elif not re.match(r'^[0-9]{10}$',mobile):
            error = "Incorrect Mobile number (must be 10 digits)"

        elif not re.match(r'(?=.*[A-Z])(?=.*[\d])(?=.*[!@#$%^&*])[a-zA-Z0-9!@#$%^&*]{8,}', password):
            error = 'Min 8 chars, at least one Uppercase, one Digit and one Special Character (!@#$%^&*)'
        elif not re.match(password, confirm_password):
            error = 'Password do not match'
        elif not re.match(r'^[a-zA-Z]{1,20}$', sec_answer):
            error = "Incorrect security answer"
        
        if error:
            flash(error, "danger")
            return render_template('auth/signup.html')
        
        #database check 

        db, cursor = get_db()
        print(email, username, mobile, dob, password, sec_question, sec_answer)
        try:
            cursor.execute("SELECT * FROM user WHERE email_address = %s", (email,))
            if cursor.fetchone():
                flash("Email already exists", 'danger')
                return render_template('auth/signup.html')
            
            cursor.execute("SELECT * FROM user WHERE mobile_number = %s", (mobile,))
            if cursor.fetchone():
                flash("Mobile number already exists", 'danger')
                return render_template('auth/signup.html')
            print(email, username, mobile, dob, password, sec_question, sec_answer)
            insert_query = """
                INSERT INTO user (email_address, user_name, mobile_number, date_of_birth, password, security_question, security_answer, role)
                values (%s,%s,%s,%s,%s,%s,%s,%s)
            """

            cursor.execute(insert_query, ((email, username, mobile, dob, password, sec_question, sec_answer, 'user')))
            db.commit()

            flash("Resgistration is done successfully", "success")
            return render_template('auth/signup.html')
        except Exception as e:
            db.rollback()
            flash(f"An eror occured: {str(e)}" , "danger")

    return render_template('auth/signup.html')

@auth_bp.route('/change_password', methods=['GET','POST'])
def change_password():
    if request.method =="POST":
        email = request.form.get('email')
        old_pass = request.form.get('old_password')
        new_pass = request.form.get('new_password')
        conf_pass = request.form.get('confirm_password')
        print(email, old_pass, new_pass, conf_pass)
        #Fetch user from db
        db , cursor = get_db()
        cursor.execute("SELECT * FROM user WHERE email_address = %s", (email,))
        user = cursor.fetchone()
        #validations
        #check if user exists
        if not user:
            flash("User with this email does not exists.", 'danger')
            return render_template('auth/change_password.html')
        #check role must be user or tech admin
        if user['role'] not in ['user', 'tech_admin']:
            flash("Only customers and Tech Admins can change password here.", 'danger')
            return render_template('auth/change_password.html')
        #Check if old password maches current db
        if user['password'] != old_pass:
            flash('Incorrect Old Password.', "danger")
            return render_template('auth/change_password.html')
        #new password strength
        if not re.match(r'^(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*_])[\w\d!@#$%^&*_]{8,}$', new_pass):
            flash('New password must be 8+ characters, with 1 Uppercae, 1 Digit and 1 Special character!', "danger")
            return render_template('auth/change_password.html')
        
        if new_pass != conf_pass:
            flash('New Password Does not match', "danger")
            return render_template('auth/change_password.html')

        if new_pass == old_pass:
            flash('New password can not be same as old.', "danger")
            return render_template('auth/change_password.html')
        #update password in db
        try: 
            update_query = "UPDATE user SET password = %s WHERE email_address = %s"
            cursor.execute(update_query, (new_pass, email))
            db.commit()
            flash("password Saved Successfully.", 'success')
        except Exception as e:
            db.rollback()
            flash(f"Error: {str(e)}", "danger")
            return render_template('auth/change_password.html')


    return render_template('auth/change_password.html')

@auth_bp.route('/base')
def base():
    return render_template('base.html')