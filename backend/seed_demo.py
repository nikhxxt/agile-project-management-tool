"""Seed demo user: demo4@example.com / demo123"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, engine, Base
from app.models import User

Base.metadata.create_all(bind=engine)

# Pre-generated bcrypt hash for "demo123"
HASH = "$2b$12$21mr6Zxa3jFltxo.pyUKUe5T98uDN6WXenOeyQnFeFIPWSppq4qda"

db = SessionLocal()
try:
    existing = db.query(User).filter(User.email == "demo4@example.com").first()
    if existing:
        existing.password_hash = HASH
        db.commit()
        print("Updated password for demo4@example.com")
    else:
        user = User(name="Demo User", email="demo4@example.com", password_hash=HASH, role="admin")
        db.add(user)
        db.commit()
        print("Created demo4@example.com with password demo123")
finally:
    db.close()
