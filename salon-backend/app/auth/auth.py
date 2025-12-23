from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from app.database import get_cursor
from jose import jwt, JWTError
from datetime import datetime, timedelta

router = APIRouter()

# 🔐 PASSWORD HASHING (SAFE)
pwd_context = CryptContext(
    schemes=["bcrypt_sha256"],
    deprecated="auto"
)

# 🔑 JWT CONFIG
SECRET_KEY = "CHANGE_THIS_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

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

# ---------------- TOKEN UTILS ----------------
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

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
        SELECT id, password, role
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

    access_token = create_access_token({
        "user_id": user["id"],
        "role": user["role"]
    })

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
