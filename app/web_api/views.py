from typing import (
    Dict,
    List
)
from decimal import Decimal
from flask import current_app
from flask.views import MethodView
from flask_smorest import Blueprint

from calculator.loan import calculate_loan
from web_api.schemas.request import (
    UpdateLoanSchema as UpdateLoanRequestSchema,
    CreateLoanSchema as CreateLoanRequestSchema
)
from web_api.schemas.response import (
    LoanSchema as LoanResponseSchema,
    ListLoansSchema as ListLoansResponseSchema
)
from db.unit_of_work import UnitOfWork
from db.data_repositories.base_interest_rate_repository import BaseInterestRateRepository
from db.data_repositories.loan_repository import (
    CreateDailyLoanCalculationResultSchema,
    LoanRepository,
    CreateLoanSchema,
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
            base_interest_rates = base_interest_rates_repository.get(
                start_date=create_loan_params["start_date"],
                end_date=create_loan_params["end_date"],
                currency=create_loan_params["currency"]
            )
            loan_calculation_results = calculate_loan(
                start_date=create_loan_params["start_date"],
                end_date=create_loan_params["end_date"],
                loan_amount=Decimal(create_loan_params["amount"]),
                currency=create_loan_params["currency"],
                annual_margin=Decimal(create_loan_params["margin"]),
            )

            new_loan = loan_repository.add(
                CreateLoanSchema(
                    amount=create_loan_params["amount"],
                    currency=create_loan_params["currency"],
                    base_interest_rate=create_loan_params["base_interest_rate"],
                    margin=create_loan_params["margin"],
                    start_date=create_loan_params["start_date"],
                    end_date=create_loan_params["end_date"],
                    calculation_results=[
                        CreateDailyLoanCalculationResultSchema(
                            date=result[3],
                            interest_accrual_amount=result[0],
                            interest_accrual_amount_without_margin=result[2],
                            days_elapsed_since_loan_start_date=result[1]
                        ) for result in loan_calculation_results
                    ]
                )
            )
            unit_of_work.commit()
            return {
               "id": new_loan.id,
               "amount": new_loan.amount,
               "currency": new_loan.currency,
               "base_interest_rate": new_loan.base_interest_rate,
               "margin": new_loan.margin,
               "start_date": new_loan.start_date,
               "end_date": new_loan.end_date,
               "total_interest": new_loan.total_interest
            }

    @api_blp.response(200, schema=ListLoansResponseSchema)
    def get(self) -> Dict[str, List]:
        with UnitOfWork(current_app.db_connection) as unit_of_work:
            loan_repository = LoanRepository(session=unit_of_work.session)
            loans = loan_repository.list()
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
               "base_interest_rate": loan.base_interest_rate,
               "margin": loan.margin,
               "start_date": loan.start_date,
               "end_date": loan.end_date,
               "total_interest": loan.total_interest
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
            loan_repository.update(id=id, update_loan_parameters=update_loan_parameters)
            unit_of_work.commit()
            loan = loan_repository.get(id)
            return {
               "id": loan.id,
               "amount": loan.amount,
               "currency": loan.currency,
               "base_interest_rate": loan.base_interest_rate,
               "margin": loan.margin,
               "start_date": loan.start_date,
               "end_date": loan.end_date,
               "total_interest": loan.total_interest
            }
