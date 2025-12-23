from fastapi import APIRouter, HTTPException
from app.database import get_cursor

router = APIRouter()

# ---------------- ROLE CHECK ----------------
def check_admin_permission(user_id: int, cur):
    cur.execute(
        "SELECT role FROM users WHERE id = %s",
        (user_id,)
    )
    user = cur.fetchone()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user["role"] != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Only admin can perform this action"
        )

# ---------------- CREATE ----------------
@router.post("/")
def create_staff(
    user_id: int,    # 👈 who is creating staff
    name: str,
    role: str
):
    conn, cur = get_cursor()

    # 🔐 admin check
    check_admin_permission(user_id, cur)

    cur.execute(
        "INSERT INTO staff (name, role) VALUES (%s, %s)",
        (name, role)
    )
    conn.commit()
    conn.close()
    return {"message": "Staff created successfully"}

# ---------------- READ ----------------
@router.get("/")
def get_all_staff():
    conn, cur = get_cursor()
    cur.execute(
        "SELECT * FROM staff WHERE is_active = TRUE"
    )
    data = cur.fetchall()
    conn.close()
    return data

@router.get("/{staff_id}")
def get_staff_by_id(staff_id: int):
    conn, cur = get_cursor()
    cur.execute(
        "SELECT * FROM staff WHERE id = %s",
        (staff_id,)
    )
    staff = cur.fetchone()
    conn.close()

    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    return staff

# ---------------- UPDATE (PUT) ----------------
@router.put("/{staff_id}")
def update_staff(
    user_id: int,    # 👈 admin only
    staff_id: int,
    name: str,
    role: str
):
    conn, cur = get_cursor()

    # 🔐 admin check
    check_admin_permission(user_id, cur)

    cur.execute(
        """
        UPDATE staff
        SET name = %s, role = %s
        WHERE id = %s
        """,
        (name, role, staff_id)
    )

    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Staff not found")

    conn.commit()
    conn.close()
    return {"message": "Staff updated successfully"}

# ---------------- PARTIAL UPDATE (PATCH) ----------------
@router.patch("/{staff_id}")
def patch_staff(
    user_id: int,    # 👈 admin only
    staff_id: int,
    name: str = None,
    role: str = None
):
    if name is None and role is None:
        raise HTTPException(
            status_code=400,
            detail="At least one field (name or role) must be provided"
        )

    conn, cur = get_cursor()

    # 🔐 admin check
    check_admin_permission(user_id, cur)

    fields = []
    values = []

    if name is not None:
        fields.append("name = %s")
        values.append(name)

    if role is not None:
        fields.append("role = %s")
        values.append(role)

    values.append(staff_id)

    query = f"""
        UPDATE staff
        SET {', '.join(fields)}
        WHERE id = %s
    """

    cur.execute(query, tuple(values))

    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Staff not found")

    conn.commit()
    conn.close()
    return {"message": "Staff updated successfully"}

# ---------------- DELETE (SOFT DELETE) ----------------
@router.delete("/{staff_id}")
def delete_staff(
    user_id: int,    # 👈 admin only
    staff_id: int
):
    conn, cur = get_cursor()

    # 🔐 admin check
    check_admin_permission(user_id, cur)

    cur.execute(
        """
        UPDATE staff
        SET is_active = FALSE
        WHERE id = %s
        """,
        (staff_id,)
    )

    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Staff not found")

    conn.commit()
    conn.close()
    return {"message": "Staff deleted successfully"}
