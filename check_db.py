from app import app, db
from sqlalchemy import inspect

def check_tables():
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print("Tables in the database:", tables)

if __name__ == "__main__":
    check_tables()