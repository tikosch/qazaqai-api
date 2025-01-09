from sqlalchemy import Column, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.db.base import Base

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", String, ForeignKey("users.id"), primary_key=True),
    Column("role_name", String, ForeignKey("roles.name"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)

    roles = relationship("Role", secondary=user_roles, back_populates="users")
    tests = relationship("Test", back_populates="teacher")
    test_results = relationship("TestResult", back_populates="student")
    evaluations = relationship("Evaluation", back_populates="user")
    model_test_results = relationship("ModelTestResult", back_populates="student")


class Role(Base):
    __tablename__ = "roles"
    name = Column(String, primary_key=True)
    users = relationship("User", secondary=user_roles, back_populates="roles")
