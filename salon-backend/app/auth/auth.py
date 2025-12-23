from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from app.database import get_cursor

router = APIRouter()

# 🔥 SAFE SCHEME
pwd_context = CryptContext(
    schemes=["bcrypt_sha256"],
    deprecated="auto"
)

# ---------------- PASSWORD UTILS ----------------
def validate_password(password: str):
    if len(password) < 8 or len(password) > 20:
        raise HTTPException(
            status_code=400,
            detail="Password must be between 8 and 20 characters"
        )

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)

# ---------------- REGISTER ----------------
@router.post("/register")
def register_user(
    name: str,
    email: str,
    password: str,
    role: str
):
    validate_password(password)

    conn, cur = get_cursor()

    cur.execute(
        "SELECT id FROM users WHERE email = %s",
        (email,)
    )
    if cur.fetchone():
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    cur.execute(
        """
        INSERT INTO users (name, email, password, role)
        VALUES (%s, %s, %s, %s)
        """,
        (name, email, hash_password(password), role)
    )

    conn.commit()
    conn.close()
    return {"message": "User registered successfully"}

# ---------------- LOGIN ----------------
@router.post("/login")
def login_user(email: str, password: str):
    conn, cur = get_cursor()

    cur.execute(
        """
        SELECT id, name, email, password, role
        FROM users
        WHERE email = %s
        """,
        (email,)
    )
    user = cur.fetchone()
    conn.close()

    if not user or not verify_password(password, user["password"]):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    return {
        "message": "Login successful",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }
    }
