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

sys.path.append("/app/calculator/")
sys.path.append("/app/")
sys.path.append("/app/db/")
sys.path.append("/app/db/data_repositories/")

from loan import calculate_daily_margin_from_annual

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
        annual_static_interest_rate_in_percent: Optional[Decimal] = None
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

    chunk_size = 365
    for i in range(0, len(all_dates), chunk_size):
        # insertion statement is so large that it causes memory issues so have to do it in smaller chunks
        dates_chunk = all_dates[i:min(i + chunk_size, len(all_dates))]
        inserts = [
            (
                "('{}', '{}', {})".format(
                    currency, interest_date,
                    round(uniform(min_daily_bi, max_daily_bi), 7) if not annual_static_interest_rate_in_percent else
                    calculate_daily_margin_from_annual(
                        year=interest_date.year, annual_margin=annual_static_interest_rate_in_percent / Decimal(100.0)
                    )
                )
            ) for currency in currencies for interest_date in dates_chunk
        ]

        statement = f"INSERT INTO public.{table_name} (currency, date, interest_rate) values {', '.join(inserts)};"
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
            annual_static_interest_rate_in_percent=interest_rate
        )
