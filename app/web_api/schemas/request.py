from marshmallow import (
    fields,
    Schema
)


class CreateLoanSchema(Schema):
    amount = fields.Float(required=True)
    currency = fields.String(required=True)
    base_interest_rate = fields.Float(required=True)
    margin = fields.Float(required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)


UpdateLoanSchema = CreateLoanSchema
