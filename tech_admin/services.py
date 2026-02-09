
from db import get_db
from datetime import datetime, timedelta


def fetch_movies():
    """Fetch all movies from DB"""
    db, cursor = get_db()
    cursor.execute("SELECT movie_name FROM movie")
    return cursor.fetchall()

def fetch_theaters_by_owner(owner_email):
    """Fetch theaters owned by a specific tech admin"""
    db, cursor = get_db()
    cursor.execute(
        "SELECT theater_name FROM theater WHERE owner_email = %s", (owner_email,)
    )
    return cursor.fetchall()



 


def insert_schedule(theater_name, movie_name, start_date, end_date):
    """Insert new schedule into DB"""
    db, cursor = get_db()
    query = """
        INSERT INTO schedule (theater_name, movie_name, start_date, end_date)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (theater_name, movie_name, start_date, end_date))
    db.commit()



 

def remove_schedule(theater_name, movie_name, start_date):
    """Delete a schedule from DB"""
    db, cursor = get_db()
    query = """
        DELETE FROM schedule
        WHERE theater_name = %s
        AND movie_name = %s
        AND start_date = %s
    """
    cursor.execute(query, (theater_name, movie_name, start_date))
    db.commit()
    return cursor.rowcount


def get_schedule(filters=None):
    """Fetch schedule from DB with optional filters"""
    db, cursor = get_db()
    base_query = "SELECT * FROM schedule WHERE 1=1"
    params = []

    if filters:
        if filters.get("movie_name"):
            base_query += " AND movie_name = %s"
            params.append(filters["movie_name"])

        if filters.get("theater_name"):
            base_query += " AND theater_name = %s"
            params.append(filters["theater_name"])

        if filters.get("start_date"):
            base_query += " AND start_date = %s"
            params.append(filters["start_date"])

    base_query += " ORDER BY start_date"
    cursor.execute(base_query, tuple(params))

    return cursor.fetchall()



def validate_schedule_dates(start_date_str, end_date_str, m_name, t_name):
    """Validate start and end dates"""
    s_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    e_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    today = datetime.now().date()
    if s_date <= today: 
        return False, "start date cannot be current date"
    # fetch release date fo movie
    db, cursor = get_db()
    query = "SELECT release_date FROM movie WHERE movie_name = %s"
    cursor.execute(query, (m_name,))
    r_date_str = cursor.fetchone()
    #r_date = datetime.strptime(r_date_str.get('release_date'), '%Y-%m-%d').date()
    r_date = r_date_str.get('release_date')
    # Check for release date < s_date
    if r_date >= s_date:
        return False, "start date cannot be on or before release date"
    if e_date <= today:
        return False, "End date cannot be current date"
    if e_date <= s_date :
        return False, "End date cannot be before start date"
    time_difference = e_date - s_date
    if time_difference.days < 10 or time_difference.days > 30:
        min_edate = s_date + timedelta(days = 10)
        max_edate = s_date + timedelta(days = 30)
        return False, f"Time Difference can not be {time_difference.days} Days.It should be min 10 Days and max 30 days. End date should be between {min_edate.strftime("%b %d, %Y")} and {max_edate.strftime("%b %d, %Y")}."
    query = "SELECT * FROM schedule WHERE movie_name = %s and theater_name = %s"
    cursor.execute(query, (m_name, t_name))
    p_schedule = cursor.fetchone()
    if p_schedule:
        p_sdate = p_schedule.get('start_date')
        p_edate = p_schedule.get('end_date')
        return False, f"Movie is already scheduled from {p_sdate.strftime("%b %d, %Y")} to {p_edate.strftime("%b %d, %Y")}."
        
        
        # if p_edate >= s_date: 
        #     return False, f"Movie is already scheduled from {p_sdate.strftime("%b %d, %Y")} to {p_edate.strftime("%b %d, %Y")}. Please Give the start date after {p_edate.strftime("%b %d, %Y")}."
    return True, "Movie Scheduled added Successfully."