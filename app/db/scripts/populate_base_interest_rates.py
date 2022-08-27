import os
import sys
from decimal import Decimal
from datetime import (
    date,
    timedelta
)
from random import (
    uniform
)
from typing import (
    List,
    Optional
)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


ALLOWED_CURRENCIES = os.environ["LOAN_CURRENCIES"].split(",")
LOANS_PERIOD_START = int(os.environ["LOANS_PERIOD_START"])
LOANS_PERIOD_END = int(os.environ["LOANS_PERIOD_END"])
DB_CONNECTION_STRING = os.environ["DB_CONNECTION_STRING"]
BASE_INTEREST_RATE_TABLE_NAME = os.environ["BASE_INTEREST_RATE_TABLE_NAME"]


def populate_base_interest_rates(
        engine, table_name: str,
        currencies: List[str] = ALLOWED_CURRENCIES,
        start_year: int = LOANS_PERIOD_START,
        end_year: int = LOANS_PERIOD_END,
        static_interest_rate: Optional[Decimal] = None
):
    # getting all dates
    all_dates = []
    start_date = date(start_year, 1, 1)
    end_date = date(end_year, 12, 31)
    current_date = start_date
    while current_date <= end_date:
        all_dates.append(current_date)
        current_date += timedelta(days=1)

    min_daily_bi, max_daily_bi = 0.01 / 365.0, 0.1 / 365.0
    values_to_insert = [
        (
            f"('{currency}', '{interest_date}', "
            f"{round(uniform(min_daily_bi, max_daily_bi), 7) if not static_interest_rate else static_interest_rate})"
        ) for currency in currencies for interest_date in all_dates
    ]

    statement = f"INSERT INTO public.{table_name} (currency, date, interest_rate) values {', '.join(values_to_insert)};"
    session_maker = sessionmaker(bind=engine)
    with session_maker(autocommit=False) as session:
        session.execute(statement)
        session.commit()


if __name__ == "__main__":
    db_engine = create_engine(DB_CONNECTION_STRING)
    interest_rate_table_empty = db_engine.execute(
        f"SELECT COUNT(*) FROM public.{BASE_INTEREST_RATE_TABLE_NAME};"
    ).fetchall()[0][0] == 0

    if interest_rate_table_empty:
        try:
            interest_rate = Decimal(sys.argv[1])
        except IndexError:
            interest_rate = None
        populate_base_interest_rates(
            engine=db_engine,
            table_name=BASE_INTEREST_RATE_TABLE_NAME,
            static_interest_rate=interest_rate
        )
