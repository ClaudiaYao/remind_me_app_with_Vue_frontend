from sqlalchemy import create_engine, Column, Integer, String, PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.services import config

# Database Engine & Session
# toggle betwewen postgresql and sqlite databases
# engine = create_engine(config.DATABASE_URL)
engine = create_engine(config.DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class UserRemindee(Base):
    __tablename__ = "user_remindee"
    remindee_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, nullable=False)
    image_object_key = Column(String, nullable=False)
    person_name = Column(String, nullable=False)
    summary = Column(String, nullable=True)
    relationship = Column(String, nullable=False)
    
    # # This relationship will handle cascade delete if configured in code
    # summaries = relationship("RemindeeSummary", back_populates="remindee", cascade="all, delete-orphan")


    
class UserSummary(Base):
    __tablename__ = "user_summary"
    user_id = Column(String, primary_key=True, index=True)
    nick_name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    phone_number = Column(String, nullable=True)
    avatar_object_key = Column(String, nullable=True)  # Add this field to store the avatar URL
    
class RemindeeSummary(Base):
    __tablename__ = "remindee_summary"
    user_id = Column(String, index=True)
    person_name = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    
    __table_args__ = (
        PrimaryKeyConstraint("user_id", "person_name"),  # Define composite primary key
        # ForeignKeyConstraint(
        #     ["user_id", "person_name"],
        #     ["user_remindee.user_id", "user_remindee.person_name"],
        #     ondelete="CASCADE"
        # ),
    )

    # remindee = relationship("UserRemindee", back_populates="summaries")
    
Base.metadata.create_all(bind=engine)

# Dependency for Database Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
