from app.database import engine 
from app.models import Base

def init():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init()
