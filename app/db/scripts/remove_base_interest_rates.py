import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_CONNECTION_STRING = os.environ["DB_CONNECTION_STRING"]
BASE_INTEREST_RATE_TABLE_NAME = os.environ["BASE_INTEREST_RATE_TABLE_NAME"]

if __name__ == "__main__":
    db_engine = create_engine(DB_CONNECTION_STRING)
    session_maker = sessionmaker(bind=db_engine)
    with session_maker(autocommit=False) as session:
        session.execute(f"DELETE FROM public.{BASE_INTEREST_RATE_TABLE_NAME};")
        session.commit()
