from app.database import get_db, engine, Base
from app.models import User, Attendance
from app.utils.auth import get_password_hash
from app.schemas import UserCreate

# Create tables
Base.metadata.create_all(bind=engine)

print("Testing manual registration...")
db = next(get_db())
try:
    user_data = UserCreate(
        username="ahmed", password="test1234", salary_type="monthly", salary_amount=5000
    )
    hashed = get_password_hash(user_data.password)
    u = User(
        username=user_data.username,
        password_hash=hashed,
        salary_type=user_data.salary_type,
        salary_amount=user_data.salary_amount,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    print("Created user:", u.id, u.username)
except Exception as e:
    db.rollback()
    print("ERROR:", type(e).__name__, str(e))
    import traceback

    traceback.print_exc()
finally:
    db.close()
