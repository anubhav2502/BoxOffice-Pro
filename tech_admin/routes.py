from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from tech_admin.services import (
    fetch_movies,
    fetch_theaters_by_owner,
    insert_schedule,
    remove_schedule,
    get_schedule,
    validate_schedule_dates,
)

tech_admin_bp = Blueprint("tech_admin", __name__)


@tech_admin_bp.route("/home")
def tech_admin_home():
    if session.get("user_role") != "tech_admin":
        return redirect(url_for("auth.login"))
    return render_template("tech_admin/home.html")



@tech_admin_bp.route("/schedule_movie", methods=["GET", "POST"])
def schedule_movie():
    if session.get("user_role") != "tech_admin":
        return redirect(url_for("auth.login"))

    current_user_email = session.get("user_email")

    if request.method == "POST":
        m_name = request.form.get("movie_name")
        t_name = request.form.get("theater_name")
        s_date_str = request.form.get("start_date")
        e_date_str = request.form.get("end_date")

        try:
            success, msg = validate_schedule_dates(s_date_str, e_date_str, m_name, t_name)
            if success:
                insert_schedule(t_name, m_name, s_date_str, e_date_str)
                flash(msg, "success")
            else:
                flash(msg, "danger")
                return redirect(url_for("tech_admin.schedule_movie"))
        except ValueError as ve:
            flash(str(ve), "danger")
            return redirect(url_for("tech_admin.schedule_movie"))

        except Exception as e:
            flash(f"Error Scheduling Movie: {str(e)}", "danger")
            return redirect(url_for("tech_admin.schedule_movie"))

    movie_names = fetch_movies()
    theater_names = fetch_theaters_by_owner(current_user_email)

    return render_template(
        "tech_admin/schedule_movie.html",
        movie_names=movie_names,
        theater_names=theater_names,
    )

 

@tech_admin_bp.route("/delete_schedule", methods=["GET", "POST"])
def delete_schedule():
    if session.get("user_role") != "tech_admin":
        return redirect(url_for("auth.login"))

    current_user_email = session.get("user_email")

    if request.method == "POST":
        m_name = request.form.get("movie_name")
        t_name = request.form.get("theater_name")
        s_date_str = request.form.get("start_date")

        try:
            rows_deleted = remove_schedule(t_name, m_name, s_date_str)
            if rows_deleted > 0:
                flash("Schedule deleted Successfully.", "success")
            else:
                flash("No Data Available.", "warning")

        except Exception as e:
            flash(f"Error deleting Schedule: {str(e)}", "danger")
            return redirect(url_for("tech_admin.delete_schedule"))

    movie_names = fetch_movies()
    theater_names = fetch_theaters_by_owner(current_user_email)

    return render_template(
        "tech_admin/delete_schedule.html",
        movie_names=movie_names,
        theater_names=theater_names,
    )



 

@tech_admin_bp.route("/view_schedule", methods=["GET", "POST"])
def view_schedule():
    if session.get("user_role") != "tech_admin":
        return redirect(url_for("auth.login"))

    current_user_email = session.get("user_email")

    movie_names = fetch_movies()
    theater_names = fetch_theaters_by_owner(current_user_email)

    filters = {}
    if request.method == "POST":
        fm_name = request.form.get("movie_name")
        ft_name = request.form.get("theater_name")
        f_date = request.form.get("start_date")

        if fm_name:
            filters["movie_name"] = fm_name

        if ft_name:
            filters["theater_name"] = ft_name

        if f_date:
            filters["start_date"] = f_date

    schedule_list = get_schedule(filters)

    return render_template(
        "tech_admin/view_schedule.html",
        movie_names=movie_names,
        theater_names=theater_names,
        schedule_list=schedule_list,
    )
    
