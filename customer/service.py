from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_db
import re
from datetime import datetime,  timedelta

def fetch_shows_on_filter(filters):
    db, cursor = get_db()
    
    # JOin on movie and schedule
    join_query = """SELECT M.movie_name, M.language, M.category, T.theater_name, T.seat_capacity, T.price_per_ticket
                FROM schedule S JOIN movie M ON S.movie_name = M.movie_name
                JOIN Theater T ON S.theater_name = T.theater_name ORDER BY M.movie_name, T.theater_name;    
    """
    cursor.execute(join_query)
    shows_list = cursor.fetchall()

    movie_with_seats = {}
    movie_with_seats = shows_list.copy()
    for sl_r, ms_r in zip(shows_list,movie_with_seats) :
        ms_r['update_seat_capacity'] = sl_r['seat_capacity']
    
    if not filters.get('selected_show'):
        return movie_with_seats

    b_date_str = filters.get('booking_date')
    b_time = filters.get('booking_time')
    if filters.get('selected_show'):
        movie_name, theater_name, seat_cpacity_str, price_str = filters.get('selected_show').split('|')
        seat_capacity = int(seat_cpacity_str)
        price = float(price_str)

    if b_date_str and b_time and movie_name and theater_name:
        
        for rows in movie_with_seats:
            if rows['movie_name'] == movie_name and rows['theater_name'] == theater_name:
                # count already booked seats 
                query_booked = """ SELECT SUM(no_of_tickets_required) as booked FROM booking 
                                WHERE theater_name = %s and movie_name = %s and date_of_booking = %s and time_of_booking = %s
                                and status = 'Booked'  """
                cursor.execute(query_booked, (theater_name, movie_name, b_date_str, b_time))
                result = cursor.fetchone()
                print(result)
                # is result['booked] is none no bookings yet so 0
                booked_seats = result['booked'] if result and result['booked'] else 0
                total_cpacity = int(rows['seat_capacity'])
                available_seats = total_cpacity - booked_seats
                print(available_seats)
                rows['update_seat_capacity'] = available_seats
    return movie_with_seats

def book_ticket_db(booking_data, user_email):
    db, cursor = get_db()
    selection = booking_data.get('selected_show')
    b_date_str = booking_data.get('booking_date')
    b_time = booking_data.get('booking_time')
    tickets = booking_data.get('no_of_tickets')
    try:
        movie_name, theater_name, seat_cpacity_str, price_str = selection.split('|')
        seat_capacity = int(seat_cpacity_str)
        price = float(price_str)
    except ValueError:
        
        return False, "Invalid selection data."
    if b_date_str == '' or not booking_data.get('booking_date'):
        return False, "Please select a booking date."
    # Validation
    try:
        b_date = datetime.strptime(b_date_str, '%Y-%m-%d').date()
        today = datetime.now().date()
        min_date = today + timedelta(days = 3) 

        if b_date > min_date: # checking for only 3 days in future
            
            return False, "Booking allowed only for the next 3 days" 

        # checking if show is available on booking date
        cursor.execute("Select start_date, end_date from schedule where movie_name = %s and theater_name = %s",(movie_name, theater_name))
        show_available = cursor.fetchone()
        e_date = show_available['end_date']
        s_date = show_available['start_date']
        print(type(s_date))
        #s_date = datetime.strptime(show_date_str, '%Y-%m-%d').date()
        if b_date < s_date or b_date > e_date:
            return False, f"Can't book movie ticket. Movie is scheduled from {s_date.strftime("%b %d, %Y")} to {e_date.strftime("%b %d, %Y")}" 
    except ValueError:
        return False, "Invlaid date format."

    # validation Check seat availability
    cursor.execute("SELECT * FROM theater WHERE theater_name = %s ", (theater_name,))
    theater_data = cursor.fetchall()
    if not theater_data:
        return False, 'Theater not found.'
    total_cpacity = seat_capacity # taken from form itself (that taken form join query)
    
    # count already booked seats 
    query_booked = """ SELECT SUM(no_of_tickets_required) as booked FROM booking 
                    WHERE theater_name = %s and movie_name = %s and date_of_booking = %s and time_of_booking = %s
                        and status = 'Booked'
    
    """
    cursor.execute(query_booked, (theater_name, movie_name, b_date_str, b_time))
    result = cursor.fetchone()
    # is result['booked] is none no bookings yet so 0
    booked_seats = result['booked'] if result and result['booked'] else 0
    available_seats = total_cpacity - booked_seats

    # final check 
    if int(tickets) > int(available_seats):
        return False, f"Not enough seats! Onle {available_seats} reaming."
    #success calculate total amount and insert total_amount
    total_amount = int(tickets) * price
    try: 
        insert_query = """INSERT INTO booking 
        (email_address, movie_name, theater_name, date_of_booking, time_of_booking, no_of_tickets_required, total_amount)
            VALUES (%s,%s,%s,%s,%s,%s,%s)"""
        cursor.execute(insert_query, (user_email, movie_name, theater_name, b_date_str, b_time, tickets, total_amount))
        db.commit()
        return True, f"Booking Successfull! Total Amount: Rs.{total_amount}" 
    except Exception as e:
        db.rollback()
        return False, f"Booking Failed: {str(e)} "

def cancel_bookings(booking_id,user_email):
    db,cur=get_db()
    query="""
    update booking set status="Cancelled" where booking_id=%s and email_address=%s
    """
    cur.execute(query,(booking_id,user_email))
    db.commit()
    return cur.rowcount

def get_active_bookings(user_email):
    db,cur=get_db()
    query="""
    select b.*,t.price_per_ticket,m.language,m.category from booking b
    join theater t on b.theater_name=t.theater_name
    join movie m on b.movie_name=m.movie_name
    where b.status='Booked' and b.email_address=%s
    """
    cur.execute(query,(user_email,))
    res=cur.fetchall()
    return res


def get_booking_history(user_email):

    if 'user_role' not in session or session['user_role']!='user':
        flash("Unauthorized access!","danger")
        return redirect(url_for('auth.login'))
    user_email=session.get('user_email')
    history_data=get_booking_history(user_email)
    return render_template('customer/history.html',history_data=history_data)

    # db,cur=get_db()
    # query="""
    # select b.*,t.price_per_ticket,m.language,m.category from booking b
    # join theater t on b.theater_name=t.theater_name
    # join movie m on b.movie_name=m.movie_name
    # where b.email_address=%s
    # order by b.status,b.booking_id
    # """
    # cur.execute(query,(user_email,))
    # res=cur.fetchall()
    # return res