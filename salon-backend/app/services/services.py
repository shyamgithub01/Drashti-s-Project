from fastapi import APIRouter, HTTPException
from app.database import get_cursor

router = APIRouter()

# ---------------- CREATE ----------------
@router.post("/")
def create_service(
    name: str,
    duration_minutes: int,
    category: str = None
):
    conn, cur = get_cursor()
    cur.execute(
        """
        INSERT INTO services (name, duration_minutes, category)
        VALUES (%s, %s, %s)
        """,
        (name, duration_minutes, category)
    )
    conn.commit()
    conn.close()
    return {"message": "Service created successfully"}

# ---------------- READ ----------------
@router.get("/")
def get_all_services():
    conn, cur = get_cursor()
    cur.execute(
        "SELECT * FROM services WHERE is_active = TRUE"
    )
    data = cur.fetchall()
    conn.close()
    return data

@router.get("/{service_id}")
def get_service_by_id(service_id: int):
    conn, cur = get_cursor()
    cur.execute(
        "SELECT * FROM services WHERE id = %s",
        (service_id,)
    )
    service = cur.fetchone()
    conn.close()

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    return service

# ---------------- UPDATE (PUT) ----------------
@router.put("/{service_id}")
def update_service(
    service_id: int,
    name: str,
    duration_minutes: int,
    category: str = None
):
    conn, cur = get_cursor()
    cur.execute(
        """
        UPDATE services
        SET name = %s,
            duration_minutes = %s,
            category = %s
        WHERE id = %s
        """,
        (name, duration_minutes, category, service_id)
    )

    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Service not found")

    conn.commit()
    conn.close()
    return {"message": "Service updated successfully"}

# ---------------- PARTIAL UPDATE (PATCH) ----------------
@router.patch("/{service_id}")
def patch_service(
    service_id: int,
    name: str = None,
    duration_minutes: int = None,
    category: str = None
):
    if name is None and duration_minutes is None and category is None:
        raise HTTPException(
            status_code=400,
            detail="At least one field must be provided"
        )

    fields = []
    values = []

    if name is not None:
        fields.append("name = %s")
        values.append(name)

    if duration_minutes is not None:
        fields.append("duration_minutes = %s")
        values.append(duration_minutes)

    if category is not None:
        fields.append("category = %s")
        values.append(category)

    values.append(service_id)

    query = f"""
        UPDATE services
        SET {', '.join(fields)}
        WHERE id = %s
    """

    conn, cur = get_cursor()
    cur.execute(query, tuple(values))

    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Service not found")

    conn.commit()
    conn.close()
    return {"message": "Service updated successfully"}

# ---------------- DELETE (SOFT DELETE) ----------------
@router.delete("/{service_id}")
def delete_service(service_id: int):
    conn, cur = get_cursor()
    cur.execute(
        """
        UPDATE services
        SET is_active = FALSE
        WHERE id = %s
        """,
        (service_id,)
    )

    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Service not found")

    conn.commit()
    conn.close()
    return {"message": "Service deleted successfully"}
