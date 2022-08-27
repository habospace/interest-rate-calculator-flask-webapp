from typing import (
    Dict,
    List
)
from decimal import Decimal
from flask import current_app
from flask.views import MethodView
from flask_smorest import Blueprint
from werkzeug.exceptions import HTTPException

from calculator.loan import (
    calculate_loan,
    BaseInterestRateNotFound
)
from web_api.errors import (
    InconsistentLoanStartAndEndDateError,
    LoanStartOrAndDateFallsOnBankHolidayError,
    IncorrectLoanAmountError,
    IncorrectMarginError,
    OutOfBoundsStartDateError,
    OutOfBoundsEndDateError,
    BANK_HOLIDAYS_UK,
    validate_loan_inputs
)
from web_api.schemas.request import (
    UpdateLoanSchema as UpdateLoanRequestSchema,
    CreateLoanSchema as CreateLoanRequestSchema
)
from web_api.schemas.response import (
    LoanSchema as LoanResponseSchema,
    ListLoansSchema as ListLoansResponseSchema
)
from db.unit_of_work import UnitOfWork
from db.data_repositories.base_interest_rate_repository import (
    BaseInterestRateRepository,
    BaseInterestRatesNotFoundError
)
from db.data_repositories.loan_repository import (
    CreateDailyLoanCalculationResultSchema,
    LoanNotFoundError,
    LoanRepository,
    CreateLoanSchema,
    UpdateLoanSchema,
    LoanSchema
)

api_blp = Blueprint("api", "loan", url_prefix="/api/")


@api_blp.route("/loans")
class Loans(MethodView):

    @api_blp.arguments(CreateLoanRequestSchema)
    @api_blp.response(200, schema=LoanResponseSchema)
    def post(self, create_loan_params: Dict) -> Dict:
        with UnitOfWork(current_app.db_connection) as unit_of_work:
            loan_repository = LoanRepository(session=unit_of_work.session)
            base_interest_rates_repository = BaseInterestRateRepository(session=unit_of_work.session)

            start_date, end_date = create_loan_params["start_date"], create_loan_params["end_date"]
            loan_amount = Decimal(create_loan_params["amount"])
            annual_margin_in_percent = Decimal(create_loan_params["annual_margin_in_percent"])
            currency = create_loan_params["currency"]
            validate_loan_inputs(
                start_date=start_date, end_date=end_date, loan_amount=loan_amount,
                annual_margin_in_percent=annual_margin_in_percent, currency=currency
            )

            annual_margin = annual_margin_in_percent / Decimal(100.0)

            base_interest_rates = base_interest_rates_repository.get(
                start_date=start_date, end_date=end_date, currency=currency
            )
            loan_calculation_results = calculate_loan(
                base_interest_rates={(bi.currency, bi.date): bi.interest_rate for bi in base_interest_rates},
                start_date=start_date, end_date=end_date,
                loan_amount=loan_amount, currency=currency,
                annual_margin=annual_margin
            )

            new_loan = loan_repository.add(
                CreateLoanSchema(
                    start_date=start_date, end_date=end_date,
                    amount=loan_amount, currency=currency,
                    annual_margin=annual_margin,
                    total_interest=sum([r.interest_accrual_amount for r in loan_calculation_results]),
                    calculation_results=[
                        CreateDailyLoanCalculationResultSchema(
                            date=result.date,
                            interest_accrual_amount=result.interest_accrual_amount,
                            interest_accrual_amount_without_margin=result.interest_accrual_amount_without_margin,
                            days_elapsed_since_loan_start_date=result.days_elapsed_since_loan_start_date
                        ) for result in loan_calculation_results
                    ]
                )
            )
            unit_of_work.commit()
            return {"id": new_loan.id}

    @api_blp.response(200, schema=ListLoansResponseSchema)
    def get(self) -> Dict[str, List]:
        with UnitOfWork(current_app.db_connection) as unit_of_work:
            loan_repository = LoanRepository(session=unit_of_work.session)
            loans = [
                {
                    "id": loan.id,
                    "amount": loan.amount,
                    "currency": loan.currency,
                    "annual_margin_in_percent": loan.annual_margin * Decimal(100.0),
                    "start_date": loan.start_date,
                    "end_date": loan.end_date,
                    "total_interest": loan.total_interest,
                } for loan in loan_repository.list()
            ]
            return {"loans": loans, "count": len(loans)}


@api_blp.route("/loan/<id>")
class Loan(MethodView):

    @api_blp.response(200, schema=LoanResponseSchema)
    def get(self, id: int) -> Dict:
        with UnitOfWork(current_app.db_connection) as unit_of_work:
            loan_repository = LoanRepository(session=unit_of_work.session)
            loan = loan_repository.get(id)
            return {
                "id": loan.id,
                "amount": loan.amount,
                "currency": loan.currency,
                "annual_margin_in_percent": loan.annual_margin * Decimal(100.0),
                "start_date": loan.start_date,
                "end_date": loan.end_date,
                "total_interest": loan.total_interest,
                "calculation_results": [
                    {
                        "date": result.date,
                        "interest_accrual_amount": result.interest_accrual_amount,
                        "interest_accrual_amount_without_margin": result.interest_accrual_amount_without_margin,
                        "days_elapsed_since_loan_start_date": result.days_elapsed_since_loan_start_date,
                    } for result in loan.calculation_results
                ]
            }

    @api_blp.response(200, schema=LoanResponseSchema)
    def delete(self, id: int) -> Dict[str, int]:
        with UnitOfWork(current_app.db_connection) as unit_of_work:
            loan_repository = LoanRepository(session=unit_of_work.session)
            loan_repository.delete(id)
            unit_of_work.commit()
            return {"id": id}

    @api_blp.arguments(UpdateLoanRequestSchema)
    @api_blp.response(200, schema=LoanResponseSchema)
    def put(self, update_loan_parameters: Dict, id: int) -> Dict:
        with UnitOfWork(current_app.db_connection) as unit_of_work:

            loan_repository = LoanRepository(session=unit_of_work.session)
            base_interest_rates_repository = BaseInterestRateRepository(session=unit_of_work.session)

            start_date, end_date = update_loan_parameters["start_date"], update_loan_parameters["end_date"]
            loan_amount = Decimal(update_loan_parameters["amount"])
            annual_margin_in_percent = Decimal(update_loan_parameters["annual_margin_in_percent"])
            currency = update_loan_parameters["currency"]
            validate_loan_inputs(
                start_date=start_date, end_date=end_date, loan_amount=loan_amount,
                annual_margin_in_percent=annual_margin_in_percent, currency=currency
            )

            annual_margin = annual_margin_in_percent / Decimal(100.0)

            base_interest_rates = base_interest_rates_repository.get(
                start_date=start_date, end_date=end_date, currency=currency
            )
            loan_calculation_results = calculate_loan(
                base_interest_rates={(bi.currency, bi.date): bi.interest_rate for bi in base_interest_rates},
                start_date=start_date, end_date=end_date,
                loan_amount=loan_amount, currency=currency,
                annual_margin=annual_margin
            )

            loan_repository.update(
                id=id, update_loan_parameters=UpdateLoanSchema(
                    start_date=start_date, end_date=end_date,
                    amount=loan_amount, currency=currency,
                    annual_margin=annual_margin,
                    total_interest=sum([r.interest_accrual_amount for r in loan_calculation_results]),
                    calculation_results=[
                        CreateDailyLoanCalculationResultSchema(
                            date=result.date,
                            interest_accrual_amount=result.interest_accrual_amount,
                            interest_accrual_amount_without_margin=result.interest_accrual_amount_without_margin,
                            days_elapsed_since_loan_start_date=result.days_elapsed_since_loan_start_date
                        ) for result in loan_calculation_results
                    ]
                )
            )
            unit_of_work.commit()
            return {"id": id}


@api_blp.errorhandler(LoanNotFoundError)
def handle_loan_not_found_error(error):
    return {"error": str(error)}, 404


@api_blp.errorhandler(BaseInterestRatesNotFoundError)
def handle_base_interest_rates_not_found_error(error):
    return {"error": str(error)}, 404


@api_blp.errorhandler(BaseInterestRateNotFound)
def handle_base_interest_rate_not_found(error):
    return {"error": str(error)}, 404


@api_blp.errorhandler(InconsistentLoanStartAndEndDateError)
def handle_inconsistent_loan_start_and_end_date_error(error):
    return {"error": str(error)}, 400


@api_blp.errorhandler(LoanStartOrAndDateFallsOnBankHolidayError)
def handle_loan_start_or_end_date_falls_on_bank_holiday(error):
    return {"error": str(error)}, 400


@api_blp.errorhandler(OutOfBoundsEndDateError)
def handle_inconsistent_loan_start_and_end_date_error(error):
    return {"error": str(error)}, 400


@api_blp.errorhandler(OutOfBoundsStartDateError)
def handle_inconsistent_loan_start_and_end_date_error(error):
    return {"error": str(error)}, 400


@api_blp.errorhandler(IncorrectMarginError)
def handle_inconsistent_loan_start_and_end_date_error(error):
    return {"error": str(error)}, 400


@api_blp.errorhandler(IncorrectLoanAmountError)
def handle_inconsistent_loan_start_and_end_date_error(error):
    return {"error": str(error)}, 400


@api_blp.errorhandler(Exception)
def handle_general_exception(error):
    if isinstance(error, HTTPException):
        return {"error": str(error)}, error.code
    return {"error": str(error)}, 500
