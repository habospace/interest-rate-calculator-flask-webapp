from collections import namedtuple
from typing import (
    List,
    Dict,
    Tuple
)
from datetime import (
    date,
    timedelta
)
from decimal import Decimal


LoanDailyCalculationResult = namedtuple("daily_loan_data", [
    "interest_accrual_amount",
    "days_elapsed_since_loan_start_date",
    "interest_accrual_amount_without_margin",
    "date"
])

Currency = str
BaseInterestRate = Decimal


class BaseInterestRateNotFound(Exception):
    pass


def calculate_daily_margin_from_annual(year: int, annual_margin: Decimal) -> Decimal:
    is_leapyear = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
    return annual_margin / Decimal(366.0) if is_leapyear else annual_margin / Decimal(365.0)


def calculate_loan(
        start_date: date, end_date: date,
        loan_amount: Decimal, currency: str,
        annual_margin: Decimal, base_interest_rates: Dict[Tuple[Currency, date], BaseInterestRate]
) -> List[LoanDailyCalculationResult]:

    daily_loan_data = []
    current_date = start_date
    days_elapsed = 0
    while current_date <= end_date:
        try:
            bi = base_interest_rates[(currency, current_date)]
        except KeyError:
            raise BaseInterestRateNotFound(
                f"Base interest rate is not available for: 'currency'={currency}, 'date'={current_date}."
            )
        daily_margin = calculate_daily_margin_from_annual(year=current_date.year, annual_margin=annual_margin)
        daily_interest_accrual_amount = calculate_interest_accrual_amount(
            p=loan_amount, bi=bi, m=daily_margin, n=Decimal(1)
        )
        daily_interest_accrual_amount_without_margin = calculate_interest_accrual_amount_without_margin(
            p=loan_amount, bi=bi, n=Decimal(1)
        )
        daily_loan_data.append(
            LoanDailyCalculationResult(
                daily_interest_accrual_amount, days_elapsed,
                daily_interest_accrual_amount_without_margin,
                current_date
            )
        )
        days_elapsed += 1
        current_date = start_date + timedelta(days=days_elapsed)
    return daily_loan_data


def calculate_interest_accrual_amount(p: Decimal, bi: Decimal, m: Decimal, n: Decimal):
    return p * (bi + m) * n


def calculate_interest_accrual_amount_without_margin(p: Decimal, bi: Decimal, n: Decimal):
    return p * bi * n
