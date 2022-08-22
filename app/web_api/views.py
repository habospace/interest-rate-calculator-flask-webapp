from typing import Dict, List
from flask import current_app
from flask.views import MethodView
from flask_smorest import Api, Blueprint, abort

from web_api.schemas.request import (
    UpdateLoanSchema as UpdateLoanRequestSchema,
    CreateLoanSchema as CreateLoanRequestSchema
)
from web_api.schemas.response import (
    LoanSchema as LoanResponseSchema,
    ListLoansSchema as ListLoansResponseSchema
)
from db.unit_of_work import UnitOfWork
from db.loan_repository import (
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
            new_loan = loan_repository.add(
                CreateLoanSchema(
                    amount=create_loan_params["amount"],
                    currency=create_loan_params["currency"],
                    base_interest_rate=create_loan_params["base_interest_rate"],
                    margin=create_loan_params["margin"],
                    start_date=create_loan_params["start_date"],
                    end_date=create_loan_params["end_date"],
                    calculation_result={}
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
               "calculation_result": new_loan.calculation_result
            }

    @api_blp.response(200, schema=ListLoansResponseSchema)
    def get(self) -> Dict[str, List]:
        # TODO: implement listing method
        return {'loans': []}


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
               "calculation_result": loan.calculation_result
            }

    @api_blp.response(200, schema=LoanResponseSchema)
    def delete(self, id: int) -> Dict[str, int]:
        # TODO: implement delete method
        return {"id": id}

    @api_blp.arguments(UpdateLoanRequestSchema)
    @api_blp.response(200, schema=LoanResponseSchema)
    def put(self, update_loan_params: Dict, id: int) -> Dict:
        # TODO: implement put method
        return {}
