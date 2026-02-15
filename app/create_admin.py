from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Usuario
from app.security import hash_password

def create_admin():
    db = SessionLocal()

    admin = db.query(Usuario).filter(Usuario.username == "admin").first()

    if not admin:
        admin_user = Usuario(
            nombre= "Admin",
            username="admin",
            mail="admin@mail.com",
            password=hash_password("admin123"),
            edad=30,
            es_admin=True
        )
        db.add(admin_user)
        db.commit()
        print("Admin creado")
    else:
        print("Admin ya existe")

    db.close()

if __name__ == "__main__":
    create_admin()