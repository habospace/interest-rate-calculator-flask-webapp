from typing import List, Dict, Tuple
from datetime import date, timedelta
from decimal import Decimal

from db.data_repositories.base_interest_rate_repository import BaseInterestRateSchema

loan_daily_data = Tuple[Decimal, int, Decimal, date]
loan_calculation_result = List[loan_daily_data]


class BaseInterestRateNotAvailableError(Exception):
    pass


def calculate_loan(
        start_date: date, end_date: date,
        loan_amount: Decimal, currency: str,
        daily_margin: Decimal, base_interest_rates: Dict[str, BaseInterestRateSchema]
) -> loan_calculation_result:

    daily_loan_data = []
    current_date = start_date
    days_elapsed = 0
    while current_date <= end_date:
        try:
            bi = base_interest_rates[f"{currency}_{current_date}"]
        except KeyError:
            raise BaseInterestRateNotAvailableError(
                f"Base interest rate is not available for: currency={currency}, date={current_date}"
            )
        daily_interest_accrual_amount = calculate_interest_accrual_amount(
            p=loan_amount, bi=bi, m=daily_margin, n=Decimal(1)
        )
        daily_interest_accrual_amount_without_margin = calculate_interest_accrual_amount_without_margin(
            p=loan_amount, bi=bi, n=Decimal(1)
        )
        daily_loan_data.append(
            (daily_interest_accrual_amount, days_elapsed, daily_interest_accrual_amount_without_margin, current_date)
        )
        days_elapsed += 1
        current_date += timedelta(days=days_elapsed)
    return daily_loan_data


def calculate_interest_accrual_amount(p: Decimal, bi: Decimal, m: Decimal, n: Decimal):
    return p * (bi + m) * n


def calculate_interest_accrual_amount_without_margin(p: Decimal, bi: Decimal, n: Decimal):
    return p * bi * n
