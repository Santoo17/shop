from app.core.database import SessionLocal, engine
from app.models.base import Base
from app.models import User, UserRole
from app.auth.hashing import hash_password


def seed_db():
    
    Base.metadata.create_all(bind=engine) 
    db = SessionLocal()
    try:

        if db.query(User).filter(User.ruolo == UserRole.ADMIN).first():

            return

        # 3. Inserimento Utente Admin
        admin = User(
            nome="Santo",
            cognome="Foti",
            email="admin@example.com",
            password_digest=hash_password("password123"),
            ruolo=UserRole.ADMIN
        )
        db.add(admin)


        db.commit()
        print("✅ Seeding completato con successo!")

    except Exception as e:
        print(f"🔴 Errore durante il seeding: {e}")
        db.rollback()
    finally:
        db.close()



if __name__ == "__main__":
    seed_db()

