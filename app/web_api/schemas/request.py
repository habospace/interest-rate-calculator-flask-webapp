import os

from marshmallow import (
    fields,
    Schema
)


class CreateLoanSchema(Schema):
    # Marshmallow is not producing useful error messages so doing validation + producing errors in api instead
    amount = fields.Float(required=True)     # , validate=lambda x: 0 < x < MAXIMUM_LOAN_AMOUNT)
    currency = fields.String(required=True)  # , validate=validate.OneOf(ALLOWED_CURRENCIES))
    annual_margin_in_percent = fields.Float(required=True)  # , validate=lambda x: x > 0)
    start_date = fields.Date(required=True)  # , validate=lambda x: LOANS_PERIOD_START <= x <= LOANS_PERIOD_END)
    end_date = fields.Date(required=True)    # , validate=lambda x: LOANS_PERIOD_START <= x <= LOANS_PERIOD_END)


UpdateLoanSchema = CreateLoanSchema
