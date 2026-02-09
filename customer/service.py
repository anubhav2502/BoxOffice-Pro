from db import get_db
from flask import session
from datetime import datetime, timedelta


def fetch_shows_on_filter(filters):
    db, cursor = get_db()

    # FIX: Changed 'Theater' to 'theater' (Lowercase)
    join_query = """SELECT M.movie_name, M.language, M.category, T.theater_name, T.seat_capacity, T.price_per_ticket
                FROM schedule S JOIN movie M ON S.movie_name = M.movie_name
                JOIN theater T ON S.theater_name = T.theater_name ORDER BY M.movie_name, T.theater_name;    
    """
    cursor.execute(join_query)
    shows_list = cursor.fetchall()

    movie_with_seats = []
    # Copying list properly to avoid reference issues
    import copy

    movie_with_seats = copy.deepcopy(shows_list)

    for ms_r in movie_with_seats:
        ms_r["update_seat_capacity"] = ms_r["seat_capacity"]

    if not filters.get("selected_show"):
        return movie_with_seats

    b_date_str = filters.get("booking_date")
    b_time = filters.get("booking_time")

    movie_name = None
    theater_name = None

    if filters.get("selected_show"):
        try:
            movie_name, theater_name, seat_cpacity_str, price_str = filters.get(
                "selected_show"
            ).split("|")
        except ValueError:
            pass  # Handle error if split fails

    if b_date_str and b_time and movie_name and theater_name:
        for rows in movie_with_seats:
            if (
                rows["movie_name"] == movie_name
                and rows["theater_name"] == theater_name
            ):
                # count already booked seats
                # FIX: Ensure tables are lowercase 'booking'
                query_booked = """ SELECT SUM(no_of_tickets_required) as booked FROM booking 
                                WHERE theater_name = %s and movie_name = %s and date_of_booking = %s and time_of_booking = %s
                                and status = 'Booked' """
                cursor.execute(
                    query_booked, (theater_name, movie_name, b_date_str, b_time)
                )
                result = cursor.fetchone()

                booked_seats = result["booked"] if result and result["booked"] else 0
                total_cpacity = int(rows["seat_capacity"])
                available_seats = total_cpacity - booked_seats

                rows["update_seat_capacity"] = available_seats

    return movie_with_seats


def book_ticket_db(booking_data, user_email):
    db, cursor = get_db()
    selection = booking_data.get("selected_show")
    b_date_str = booking_data.get("booking_date")
    b_time = booking_data.get("booking_time")
    tickets = booking_data.get("no_of_tickets")

    try:
        movie_name, theater_name, seat_cpacity_str, price_str = selection.split("|")
        seat_capacity = int(seat_cpacity_str)
        price = float(price_str)
    except (ValueError, AttributeError):
        return False, "Invalid selection data."

    if not b_date_str:
        return False, "Please select a booking date."

    # Validation
    try:
        b_date = datetime.strptime(b_date_str, "%Y-%m-%d").date()
        today = datetime.now().date()
        min_date = today + timedelta(days=3)

        if b_date > min_date:
            return False, "Booking allowed only for the next 3 days"

        # checking if show is available on booking date
        # FIX: Ensure 'schedule' is lowercase
        cursor.execute(
            "Select start_date, end_date from schedule where movie_name = %s and theater_name = %s",
            (movie_name, theater_name),
        )
        show_available = cursor.fetchone()

        if not show_available:
            return False, "Show not found in schedule."

        e_date = show_available["end_date"]
        s_date = show_available["start_date"]

        if b_date < s_date or b_date > e_date:
            return (
                False,
                f"Can't book. Movie is scheduled from {s_date.strftime('%b %d, %Y')} to {e_date.strftime('%b %d, %Y')}",
            )
    except ValueError:
        return False, "Invalid date format."

    # validation Check seat availability
    # FIX: Ensure 'theater' is lowercase
    cursor.execute("SELECT * FROM theater WHERE theater_name = %s ", (theater_name,))
    theater_data = cursor.fetchall()
    if not theater_data:
        return False, "Theater not found."

    total_cpacity = seat_capacity

    # count already booked seats
    query_booked = """ SELECT SUM(no_of_tickets_required) as booked FROM booking 
                    WHERE theater_name = %s and movie_name = %s and date_of_booking = %s and time_of_booking = %s
                        and status = 'Booked' """
    cursor.execute(query_booked, (theater_name, movie_name, b_date_str, b_time))
    result = cursor.fetchone()

    booked_seats = result["booked"] if result and result["booked"] else 0
    available_seats = total_cpacity - booked_seats

    # final check
    if int(tickets) > int(available_seats):
        return False, f"Not enough seats! Only {available_seats} remaining."

    # Insert Booking
    total_amount = int(tickets) * price
    try:
        # FIX: Ensure 'booking' is lowercase
        insert_query = """INSERT INTO booking 
        (email_address, movie_name, theater_name, date_of_booking, time_of_booking, no_of_tickets_required, total_amount, status)
            VALUES (%s,%s,%s,%s,%s,%s,%s, 'Booked')"""
        cursor.execute(
            insert_query,
            (
                user_email,
                movie_name,
                theater_name,
                b_date_str,
                b_time,
                tickets,
                total_amount,
            ),
        )
        db.commit()
        return True, f"Booking Successful! Total Amount: Rs.{total_amount}"
    except Exception as e:
        db.rollback()
        return False, f"Booking Failed: {str(e)} "


def cancel_bookings(booking_id, user_email):
    db, cur = get_db()
    # FIX: Ensure 'booking' is lowercase
    query = """
    update booking set status="Cancelled" where booking_id=%s and email_address=%s
    """
    cur.execute(query, (booking_id, user_email))
    db.commit()
    return cur.rowcount


def get_active_bookings(user_email):
    db, cur = get_db()
    # FIX: Ensure tables are lowercase
    query = """
    select b.*, t.price_per_ticket, m.language, m.category from booking b
    join theater t on b.theater_name=t.theater_name
    join movie m on b.movie_name=m.movie_name
    where b.status='Booked' and b.email_address=%s
    """
    cur.execute(query, (user_email,))
    res = cur.fetchall()
    return res


def get_booking_history(user_email):
    db, cur = get_db()
    # FIX: Ensure tables are lowercase
    query = """
    select b.*, t.price_per_ticket, m.language, m.category from booking b
    join theater t on b.theater_name=t.theater_name
    join movie m on b.movie_name=m.movie_name
    where b.email_address=%s
    order by b.status, b.booking_id
    """
    cur.execute(query, (user_email,))
    res = cur.fetchall()
    return res
