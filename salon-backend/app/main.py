from fastapi import FastAPI
from app.database import get_cursor
from app.staff.staff import router as staff_router
from app.services.services import router as services_router
from app.appointments.appointments import router as appointments_router
from app.reports.reports import router as reports_router
from app.auth.auth import router as auth_router
app = FastAPI(title="Salon Management System")

@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "Salon Management System API is running"
    }



app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(staff_router, prefix="/staff", tags=["Staff"])
app.include_router(services_router, prefix="/services", tags=["Services"])
app.include_router(
    appointments_router,
    prefix="/appointments",
    tags=["Appointments"]
)
app.include_router(
    reports_router,
    prefix="/reports",
    tags=["Reports"]
)

@app.get("/db-health")
def db_health_check():
    try:
        conn, cur = get_cursor()
        cur.execute("SELECT 1;")
        conn.close()
        return {"database": "connected"}
    except Exception as e:
        return {"database": "error", "detail": str(e)}
