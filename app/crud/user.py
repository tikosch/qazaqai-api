from sqlalchemy.orm import Session
from uuid import uuid4
from app.models.user import User, Role
from app.core.security import get_password_hash, verify_password

def create_user(db: Session, username: str, email: str, password: str) -> User:
    user_id = str(uuid4())
    user = User(
        id=user_id,
        username=username,
        email=email,
        hashed_password=get_password_hash(password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_email(db: Session, email: str) -> User:
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str) -> User:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def add_user_role(db: Session, user: User, role_name: str):
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        role = Role(name=role_name)
        db.add(role)
        db.commit()
        db.refresh(role)
    user.roles.append(role)
    db.commit()
    db.refresh(user)
    return user
