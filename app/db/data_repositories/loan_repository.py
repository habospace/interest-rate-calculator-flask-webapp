from decimal import Decimal
from typing import List
from datetime import (
    date,
    datetime
)

from sqlalchemy import delete
from pydantic import BaseModel

from db.schema import (
    Loan,
    DailyLoanCalculationResult
)


class LoanNotFoundError(Exception):
    pass


class CreateDailyLoanCalculationResultSchema(BaseModel):
    date: date
    interest_accrual_amount: Decimal
    interest_accrual_amount_without_margin: Decimal
    days_elapsed_since_loan_start_date: int


class DailyLoanCalculationResultSchema(CreateDailyLoanCalculationResultSchema):
    id: int


class LoanParametersSchema(BaseModel):
    amount: Decimal
    currency: str
    annual_margin: Decimal
    start_date: date
    end_date: date


class ListedLoanSchema(LoanParametersSchema):
    id: int
    total_interest: Decimal


class CreateLoanSchema(LoanParametersSchema):
    total_interest: Decimal
    calculation_results: List[CreateDailyLoanCalculationResultSchema]


class LoanSchema(CreateLoanSchema):
    id: int
    created_on: datetime
    updated_on: datetime
    calculation_results: List[DailyLoanCalculationResultSchema]


UpdateLoanSchema = CreateLoanSchema


class LoanRepository:

    def __init__(self, session):
        self.session = session

    def add(self, create_loan_parameters: CreateLoanSchema) -> Loan:
        ts_now = datetime.utcnow()
        loan = Loan(
            amount=create_loan_parameters.amount,
            currency=create_loan_parameters.currency,
            annual_margin=create_loan_parameters.annual_margin,
            start_date=create_loan_parameters.start_date,
            end_date=create_loan_parameters.end_date,
            total_interest=create_loan_parameters.total_interest,
            created_on=ts_now,
            updated_on=ts_now,
            daily_loan_calculation_results=[
                DailyLoanCalculationResult(
                    date=result.date,
                    interest_accrual_amount=result.interest_accrual_amount,
                    interest_accrual_amount_without_margin=result.interest_accrual_amount_without_margin,
                    days_elapsed_since_loan_start_date=result.days_elapsed_since_loan_start_date)
                for result in create_loan_parameters.calculation_results
            ]
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
            total_interest=loan_record.total_interest,
            annual_margin=loan_record.annual_margin,
            start_date=loan_record.start_date,
            end_date=loan_record.end_date,
            calculation_results=[
                DailyLoanCalculationResultSchema(
                    id=result.id,
                    date=result.date,
                    interest_accrual_amount=result.interest_accrual_amount,
                    interest_accrual_amount_without_margin=result.interest_accrual_amount_without_margin,
                    days_elapsed_since_loan_start_date=result.days_elapsed_since_loan_start_date

                ) for result in loan_record.daily_loan_calculation_results
            ],
            created_on=loan_record.created_on,
            updated_on=loan_record.updated_on
        )

    def list(self) -> List[ListedLoanSchema]:
        return [
            ListedLoanSchema(
                id=loan_record.id,
                amount=loan_record.amount,
                currency=loan_record.currency,
                total_interest=loan_record.total_interest,
                annual_margin=loan_record.annual_margin,
                start_date=loan_record.start_date,
                end_date=loan_record.end_date,
                created_on=loan_record.created_on,
                updated_on=loan_record.updated_on
            ) for loan_record in self.session.query(Loan).all()
        ]

    def delete(self, id: int):
        loan = self.session.query(Loan).filter(Loan.id == id).first()
        if not loan:
            raise LoanNotFoundError(f"Loan with id={id} is not found so can't be deleted.")
        delete_results_statement = delete(DailyLoanCalculationResult).where(DailyLoanCalculationResult.loan_id == id)
        self.session.execute(delete_results_statement)
        self.session.delete(loan)

    def update(self, id: int, update_loan_parameters: UpdateLoanSchema):
        loan = self.session.query(Loan).filter(Loan.id == id).first()
        if not loan:
            raise LoanNotFoundError(f"Loan with id={id} is not found so can't be updated.")
        delete_results_statement = delete(DailyLoanCalculationResult).where(DailyLoanCalculationResult.loan_id == id)
        self.session.execute(delete_results_statement)

        for result in update_loan_parameters.calculation_results:
            self.session.add(
                DailyLoanCalculationResult(
                    date=result.date,
                    loan_id=id,
                    interest_accrual_amount=result.interest_accrual_amount,
                    interest_accrual_amount_without_margin=result.interest_accrual_amount_without_margin,
                    days_elapsed_since_loan_start_date=result.days_elapsed_since_loan_start_date
                )
            )
        for field, value in update_loan_parameters.dict().items():
            if field == "calculation_results":
                continue
            setattr(loan, field, value)
        loan.updated_on = datetime.utcnow()
