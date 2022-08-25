from datetime import date
import os

from marshmallow import (
    fields,
    Schema,
    validate
)

ALLOWED_CURRENCIES = os.environ["LOAN_CURRENCIES"].split(",")
LOANS_PERIOD_START = date(int(os.environ["LOANS_PERIOD_START"]), 1, 1)
LOANS_PERIOD_END = date(int(os.environ["LOANS_PERIOD_END"]), 12, 31)
MAXIMUM_LOAN_AMOUNT = float(os.environ["MAXIMUM_LOAN_AMOUNT"])


class CreateLoanSchema(Schema):
    amount = fields.Float(required=True, validate=lambda x: 0 < x < MAXIMUM_LOAN_AMOUNT)
    currency = fields.String(required=True, validate=validate.OneOf(ALLOWED_CURRENCIES))
    annual_margin_in_percent = fields.Float(required=True, validate=lambda x: x > 0)
    start_date = fields.Date(required=True, validate=lambda x: LOANS_PERIOD_START <= x <= LOANS_PERIOD_END)
    end_date = fields.Date(required=True, validate=lambda x: LOANS_PERIOD_START <= x <= LOANS_PERIOD_END)


UpdateLoanSchema = CreateLoanSchema
