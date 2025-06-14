from app.db.database import engine
from app.db.models import Base

def init_database():
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_database() 