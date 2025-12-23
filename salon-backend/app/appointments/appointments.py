from fastapi import APIRouter, HTTPException
from app.database import get_cursor
from datetime import date

router = APIRouter()

VALID_STATUSES = ["BOOKED", "CONFIRMED", "COMPLETED", "CANCELLED", "NO_SHOW"]

# ---------------- CREATE (BOOK APPOINTMENT) ----------------
@router.post("/")
def create_appointment(
    customer_name: str,
    staff_id: int,
    service_id: int,
    appointment_date: str,
    appointment_time: str
):
    conn, cur = get_cursor()

    # prevent past booking
    if appointment_date < str(date.today()):
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Appointment date cannot be in the past"
        )

    # check staff exists
    cur.execute(
        "SELECT id FROM staff WHERE id = %s AND is_active = TRUE",
        (staff_id,)
    )
    if not cur.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Staff not found")

    # check service exists
    cur.execute(
        "SELECT id FROM services WHERE id = %s AND is_active = TRUE",
        (service_id,)
    )
    if not cur.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Service not found")

    # insert appointment
    cur.execute(
        """
        INSERT INTO appointments
        (customer_name, staff_id, service_id, appointment_date, appointment_time)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (customer_name, staff_id, service_id, appointment_date, appointment_time)
    )

    conn.commit()
    conn.close()
    return {"message": "Appointment booked successfully"}

# ---------------- READ ----------------
@router.get("/")
def get_all_appointments():
    conn, cur = get_cursor()
    cur.execute(
        """
        SELECT a.*, s.name AS staff_name, sv.name AS service_name
        FROM appointments a
        JOIN staff s ON a.staff_id = s.id
        JOIN services sv ON a.service_id = sv.id
        ORDER BY a.appointment_date, a.appointment_time
        """
    )
    data = cur.fetchall()
    conn.close()
    return data

@router.get("/{appointment_id}")
def get_appointment_by_id(appointment_id: int):
    conn, cur = get_cursor()
    cur.execute(
        "SELECT * FROM appointments WHERE id = %s",
        (appointment_id,)
    )
    appt = cur.fetchone()
    conn.close()

    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    return appt

# ---------------- FILTER (NEW) ----------------
@router.get("/filter")
def filter_appointments(
    appointment_date: str = None,
    staff_id: int = None,
    status: str = None
):
    conn, cur = get_cursor()

    query = """
        SELECT a.*, s.name AS staff_name, sv.name AS service_name
        FROM appointments a
        JOIN staff s ON a.staff_id = s.id
        JOIN services sv ON a.service_id = sv.id
        WHERE 1=1
    """
    values = []

    if appointment_date:
        query += " AND a.appointment_date = %s"
        values.append(appointment_date)

    if staff_id:
        query += " AND a.staff_id = %s"
        values.append(staff_id)

    if status:
        if status not in VALID_STATUSES:
            conn.close()
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Use {VALID_STATUSES}"
            )
        query += " AND a.status = %s"
        values.append(status)

    query += " ORDER BY a.appointment_date, a.appointment_time"

    cur.execute(query, tuple(values))
    data = cur.fetchall()
    conn.close()
    return data

# ---------------- UPDATE (PUT) ----------------
@router.put("/{appointment_id}")
def update_appointment(
    appointment_id: int,
    appointment_date: str,
    appointment_time: str,
    status: str
):
    if status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Use {VALID_STATUSES}"
        )

    conn, cur = get_cursor()
    cur.execute(
        """
        UPDATE appointments
        SET appointment_date = %s,
            appointment_time = %s,
            status = %s
        WHERE id = %s
        """,
        (appointment_date, appointment_time, status, appointment_id)
    )

    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Appointment not found")

    conn.commit()
    conn.close()
    return {"message": "Appointment updated successfully"}

# ---------------- PARTIAL UPDATE (PATCH) ----------------
@router.patch("/{appointment_id}")
def patch_appointment(
    appointment_id: int,
    status: str
):
    if status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Use {VALID_STATUSES}"
        )

    conn, cur = get_cursor()
    cur.execute(
        """
        UPDATE appointments
        SET status = %s
        WHERE id = %s
        """,
        (status, appointment_id)
    )

    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Appointment not found")

    conn.commit()
    conn.close()
    return {"message": "Appointment status updated"}

# ---------------- DELETE ----------------
@router.delete("/{appointment_id}")
def delete_appointment(appointment_id: int):
    conn, cur = get_cursor()
    cur.execute(
        "DELETE FROM appointments WHERE id = %s",
        (appointment_id,)
    )

    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Appointment not found")

    conn.commit()
    conn.close()
    return {"message": "Appointment deleted successfully"}
