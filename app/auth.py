from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def register(self, db: Session, username: str, password: str) -> User:
        hashed_password = pwd_context.hash(password)
        user = User(username=username, password=hashed_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def login(self, db: Session, username: str, password: str):
        user = db.query(User).filter(User.username == username).first()
        if user and pwd_context.verify(password, user.password):
            return user
        return None
