import os

import holidays


class InconsistentLoanStartAndEndDateError(Exception):
    pass


class LoanStartOrAndDateFallsOnBankHolidayError(Exception):
    pass


LOANS_PERIOD_START = int(os.environ["LOANS_PERIOD_START"])
LOANS_PERIOD_END = int(os.environ["LOANS_PERIOD_END"])
BANK_HOLIDAYS_UK = [
    d for d in holidays.UnitedKingdom(years=[y for y in range(LOANS_PERIOD_START, LOANS_PERIOD_END+1)])
]
