from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime, timedelta
from customer.service import *

# Creating blueprint
customer_bp = Blueprint("customer", __name__)


@customer_bp.route("/home")
def customer_home():
    if "user_role" not in session or session["user_role"] != "user":
        flash("Unauthorized Access!", "danger")
        return redirect(url_for("auth.login"))
    return render_template("customer/home.html")


@customer_bp.route("/book_ticket", methods=["GET", "POST"])
def book_ticket():
    if "user_role" not in session or session["user_role"] != "user":
        flash("Unauthorized Access!", "danger")
        return redirect(url_for("auth.login"))

    user_email = session.get("user_email")
    selection = request.form.get("selected_show")

    # Get: Show the table
    filters = {
        "booking_date": request.form.get("booking_date"),
        "booking_time": request.form.get("booking_time"),
        "selected_show": selection,
        "no_of_tickets": request.form.get("no_of_tickets"),
    }

    # This calls the service function where we fixed 'Theater' -> 'theater'
    movie_with_seats = fetch_shows_on_filter(filters)

    if request.method == "POST" and "book_btn" in request.form:
        if not selection:
            flash("Please select Movie and Theater.", "danger")
            return redirect(url_for("customer.book_ticket"))

        booking_data = filters.copy()
        success, msg = book_ticket_db(booking_data, user_email)

        if not success:
            flash(msg, "danger")
            return redirect(url_for("customer.book_ticket"))
        else:
            flash(msg, "success")
            return redirect(url_for("customer.history"))

    # Date check for frontend
    today = datetime.now().date()
    today_date_str = today.isoformat()
    max_date = today + timedelta(days=3)
    max_date_str = max_date.isoformat()

    return render_template(
        "customer/book_ticket.html",
        shows=movie_with_seats,
        min_date=today_date_str,
        max_date=max_date_str,
        selected_movie_details=filters,
    )


@customer_bp.route("/cancel", methods=["GET", "POST"])
def cancel_booking():
    if "user_role" not in session or session["user_role"] != "user":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("auth.login"))

    user_email = session.get("user_email")

    if request.method == "POST":
        booking_id = request.form.get("booking_id")
        if not booking_id:
            flash("Select a booking to cancel", "danger")
            return redirect(url_for("customer.cancel_booking"))

        rows = cancel_bookings(booking_id, user_email)

        if rows > 0:
            flash("Booking Cancelled Successfully", "success")
        else:
            flash("Cancellation Failed", "danger")
        return redirect(url_for("customer.cancel_booking"))

    bookings = get_active_bookings(user_email)
    return render_template("customer/cancel_booking.html", history_data=bookings)


@customer_bp.route("/history")
def history():
    if "user_role" not in session or session["user_role"] != "user":
        flash("Unauthorized Access!", "danger")
        return redirect(url_for("auth.login"))

    user_email = session.get("user_email")

    # Use the service function instead of raw SQL in route
    show_data = get_booking_history(user_email)

    return render_template("customer/history.html", history_data=show_data)
