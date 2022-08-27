import os
from datetime import date

import holidays


LOANS_PERIOD_START = date(int(os.environ["LOANS_PERIOD_START"]), 1, 1)
LOANS_PERIOD_END = date(int(os.environ["LOANS_PERIOD_END"]), 12, 31)
MAXIMUM_LOAN_AMOUNT = float(os.environ["MAXIMUM_LOAN_AMOUNT"])


class InconsistentLoanStartAndEndDateError(Exception):
    pass


class LoanStartOrAndDateFallsOnBankHolidayError(Exception):
    pass


class IncorrectLoanAmountError(Exception):
    pass


class IncorrectMarginError(Exception):
    pass


class OutOfBoundsStartDateError(Exception):
    pass


class OutOfBoundsEndDateError(Exception):
    pass


class CurrencyNotAllowedError(Exception):
    pass


ALLOWED_CURRENCIES = os.environ["LOAN_CURRENCIES"].split(",")
LOANS_PERIOD_START = int(os.environ["LOANS_PERIOD_START"])
LOANS_PERIOD_END = int(os.environ["LOANS_PERIOD_END"])
BANK_HOLIDAYS_UK = [
    d for d in holidays.UnitedKingdom(years=[y for y in range(LOANS_PERIOD_START, LOANS_PERIOD_END+1)])
]


def validate_loan_inputs(
        start_date: date, end_date: date,
        loan_amount: float, currency: str,
        annual_margin_in_percent: float
):
    if currency not in ALLOWED_CURRENCIES:
        raise CurrencyNotAllowedError(f"Currency has to be one of: {ALLOWED_CURRENCIES}.")
    if not(0 < loan_amount <= MAXIMUM_LOAN_AMOUNT):
        raise IncorrectLoanAmountError(f"Loan amount has to be between 0 and {MAXIMUM_LOAN_AMOUNT}.")
    if 0 > annual_margin_in_percent:
        raise IncorrectMarginError(f"Annual margin has to be greater than or equal to 0.")
    if not(LOANS_PERIOD_START <= start_date.year <= LOANS_PERIOD_END):
        raise OutOfBoundsStartDateError(
            f"Loan period start has to be between {LOANS_PERIOD_START} and {LOANS_PERIOD_END}."
        )
    if not(LOANS_PERIOD_START <= end_date.year <= LOANS_PERIOD_END):
        raise OutOfBoundsEndDateError(
            f"Loan period end has to be between {LOANS_PERIOD_START} and {LOANS_PERIOD_END}."
        )
    if start_date >= end_date:
        raise InconsistentLoanStartAndEndDateError("Loan start_date must be before end_date.")
    if start_date in BANK_HOLIDAYS_UK or end_date in BANK_HOLIDAYS_UK:
        raise LoanStartOrAndDateFallsOnBankHolidayError(
            f"Loan start_date and end_date cannot fall on a bank holiday: {[str(d) for d in BANK_HOLIDAYS_UK]}"
        )
