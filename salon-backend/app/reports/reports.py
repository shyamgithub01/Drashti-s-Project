from fastapi import APIRouter
from app.database import get_cursor

router = APIRouter()

# ---------------- DAILY APPOINTMENTS ----------------
@router.get("/daily-appointments")
def daily_appointments(date: str):
    conn, cur = get_cursor()
    cur.execute(
        """
        SELECT COUNT(*) AS total_appointments
        FROM appointments
        WHERE appointment_date = %s
        """,
        (date,)
    )
    result = cur.fetchone()
    conn.close()
    return {
        "date": date,
        "total_appointments": result["total_appointments"]
    }

# ---------------- APPOINTMENTS BY STATUS ----------------
@router.get("/appointments-by-status")
def appointments_by_status():
    conn, cur = get_cursor()
    cur.execute(
        """
        SELECT status, COUNT(*) AS count
        FROM appointments
        GROUP BY status
        ORDER BY count DESC
        """
    )
    data = cur.fetchall()
    conn.close()
    return data

# ---------------- STAFF PERFORMANCE ----------------
@router.get("/staff-performance")
def staff_performance():
    conn, cur = get_cursor()
    cur.execute(
        """
        SELECT s.id,
               s.name,
               COUNT(a.id) AS total_appointments
        FROM staff s
        LEFT JOIN appointments a ON s.id = a.staff_id
        GROUP BY s.id, s.name
        ORDER BY total_appointments DESC
        """
    )
    data = cur.fetchall()
    conn.close()
    return data

# ---------------- SERVICE POPULARITY ----------------
@router.get("/service-popularity")
def service_popularity():
    conn, cur = get_cursor()
    cur.execute(
        """
        SELECT sv.id,
               sv.name,
               COUNT(a.id) AS total_bookings
        FROM services sv
        LEFT JOIN appointments a ON sv.id = a.service_id
        GROUP BY sv.id, sv.name
        ORDER BY total_bookings DESC
        """
    )
    data = cur.fetchall()
    conn.close()
    return data
