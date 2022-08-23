from marshmallow import (
    fields,
    Schema
)

from web_api.schemas.request import CreateLoanSchema


class LoanSchema(CreateLoanSchema):
    id = fields.Integer(required=True)
    total_interest = fields.Float(required=True)


class ListLoansSchema(Schema):
    loans = fields.List(fields.Nested(LoanSchema), required=True)
    count = fields.Integer(required=True)
