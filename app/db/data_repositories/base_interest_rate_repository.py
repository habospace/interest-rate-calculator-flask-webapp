from datetime import date
from decimal import Decimal
from typing import List

from pydantic import BaseModel

from db.schema import BaseInterestRate


class BaseInterestRatesNotFoundError(Exception):
    pass


class BaseInterestRateSchema(BaseModel):
    id: int
    currency: str
    date: date
    interest_rate: Decimal


class BaseInterestRateRepository:

    def __init__(self, session):
        self.session = session

    def get(self, start_date: date, end_date: date, currency: str) -> List[BaseInterestRateSchema]:
        interest_rates = self.session.query(
            BaseInterestRate
        ).filter(
            BaseInterestRate.currency == currency
        ).filter(
            BaseInterestRate.date >= start_date
        ).filter(
            BaseInterestRate.date <= end_date
        ).all()
        if not interest_rates:
            raise BaseInterestRatesNotFoundError(
                f"Couldn't find base interest rates for parameters: "
                f"'currency'={currency}, 'start_date'={start_date}, 'end_date'={end_date}"
            )
        return [
            BaseInterestRateSchema(
                id=rate.interest_rate,
                currency=rate.currency,
                date=rate.date,
                interest_rate=Decimal(rate.interest_rate),
            ) for rate in interest_rates
        ]

    def add(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def list(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError
