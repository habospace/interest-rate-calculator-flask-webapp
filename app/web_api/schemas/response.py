from marshmallow import (
    fields,
    Schema
)

from web_api.schemas.request import CreateLoanSchema


class DailyLoanCalculationResultSchema(Schema):
    date = fields.Date(required=True)
    interest_accrual_amount = fields.Float(required=True)
    interest_accrual_amount_without_margin = fields.Float(required=True)
    days_elapsed_since_loan_start_date = fields.Integer(required=True)


class ListedLoanSchema(CreateLoanSchema):
    id = fields.Integer(required=True)
    total_interest = fields.Float(required=True)


class LoanSchema(ListedLoanSchema):
    calculation_results = fields.List(fields.Nested(DailyLoanCalculationResultSchema), required=True)


class ListLoansSchema(Schema):
    loans = fields.List(fields.Nested(ListedLoanSchema), required=True)
    count = fields.Integer(required=True)
