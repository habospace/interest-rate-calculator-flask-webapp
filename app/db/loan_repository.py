from typing import Dict
from datetime import date, datetime

from pydantic import BaseModel

from db.schema import Loan


class LoanNotFoundError(Exception):
    pass


class CreateLoanSchema(BaseModel):
    amount: float
    currency: str
    base_interest_rate: str
    margin: float
    start_date: date
    end_date: date
    calculation_result: Dict


class LoanSchema(CreateLoanSchema):
    id: int
    created_on: datetime
    updated_on: datetime


UpdateLoanSchema = CreateLoanSchema


class LoanRepository:

    def __init__(self, session):
        self.session = session

    def add(self, create_loan_parameters: CreateLoanSchema) -> LoanSchema:
        ts_now = datetime.utcnow()
        loan = Loan(
            amount=create_loan_parameters.amount,
            currency=create_loan_parameters.currency,
            base_interest_rate=create_loan_parameters.base_interest_rate,
            margin=create_loan_parameters.margin,
            start_date=create_loan_parameters.start_date,
            end_date=create_loan_parameters.end_date,
            calculation_result=create_loan_parameters.calculation_result,
            created_on=ts_now,
            updated_on=ts_now,
        )
        self.session.add(loan)
        return loan

    def get(self, id: int) -> LoanSchema:
        loan_record = self.session.query(Loan).filter(Loan.id == id).first()
        if not loan_record:
            raise LoanNotFoundError(f"Loan with id={id} is not found.")
        return LoanSchema(
            id=loan_record.id,
            amount=loan_record.amount,
            currency=loan_record.currency,
            base_interest_rate=loan_record.base_interest_rate,
            margin=loan_record.margin,
            start_date=loan_record.start_date,
            end_date=loan_record.end_date,
            calculation_result=loan_record.calculation_result,
            created_on=loan_record.created_on,
            updated_on=loan_record.updated_on
        )

    def list(self):
        # TODO: implement this
        pass

    def update(self):
        # TODO: implement this
        pass
