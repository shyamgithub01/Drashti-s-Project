from fastapi import APIRouter, HTTPException, Depends
from app.database import get_cursor
from app.auth.utils import get_current_user

router = APIRouter()

# ---------------- ADMIN ROLE CHECK ----------------
def check_admin_permission(current_user: dict):
    if current_user["role"] != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Only admin can perform this action"
        )

# ---------------- CREATE ----------------
@router.post("/")
def create_staff(
    name: str,
    role: str,
    current_user: dict = Depends(get_current_user)
):
    # 🔐 admin check via token
    check_admin_permission(current_user)

    conn, cur = get_cursor()
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
    staff_id: int,
    name: str,
    role: str,
    current_user: dict = Depends(get_current_user)
):
    # 🔐 admin check via token
    check_admin_permission(current_user)

    conn, cur = get_cursor()
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
    staff_id: int,
    name: str = None,
    role: str = None,
    current_user: dict = Depends(get_current_user)
):
    if name is None and role is None:
        raise HTTPException(
            status_code=400,
            detail="At least one field (name or role) must be provided"
        )

    # 🔐 admin check via token
    check_admin_permission(current_user)

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

    conn, cur = get_cursor()
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
    staff_id: int,
    current_user: dict = Depends(get_current_user)
):
    # 🔐 admin check via token
    check_admin_permission(current_user)

    conn, cur = get_cursor()
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
