import os
from sqlalchemy import (
    ForeignKey,
    UniqueConstraint,
    Index,
    create_engine,
    Integer,
    DECIMAL,
    String,
    Column,
    DateTime,
    Date,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

engine = create_engine(os.environ["DB_CONNECTION_STRING"])
Base = declarative_base()


LOAN_TABLE_NAME = os.environ["LOAN_TABLE_NAME"]
LOAN_CALCULATION_RESULT_TABLE_NAME = os.environ["LOAN_CALCULATION_RESULT_TABLE_NAME"]
BASE_INTEREST_RATE_TABLE_NAME = os.environ["BASE_INTEREST_RATE_TABLE_NAME"]


class BaseInterestRate(Base):
    __tablename__ = BASE_INTEREST_RATE_TABLE_NAME
    id = Column(Integer, primary_key=True)
    currency = Column(String(3), nullable=False)
    date = Column(Date(), nullable=False)
    interest_rate = Column(DECIMAL(precision=25, scale=10), nullable=False)

    __table_args__ = (
        UniqueConstraint('currency', 'date', name='currency_date'),
        Index('currency_date_index', "currency", "date")
    )


class Loan(Base):
    __tablename__ = LOAN_TABLE_NAME
    id = Column(Integer, primary_key=True)
    daily_loan_calculation_results = relationship("DailyLoanCalculationResult")

    amount = Column(DECIMAL(precision=25, scale=10), nullable=False)
    currency = Column(String(3), nullable=False)
    base_interest_rate = Column(DECIMAL(precision=25, scale=10), nullable=False)
    margin = Column(DECIMAL(precision=25, scale=10), nullable=False)
    start_date = Column(Date(), default=datetime.now, nullable=False)
    end_date = Column(Date(), default=datetime.now, nullable=False)

    total_interest = Column(DECIMAL(precision=25, scale=10), nullable=False)

    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)


class DailyLoanCalculationResult(Base):
    __tablename__ = LOAN_CALCULATION_RESULT_TABLE_NAME
    id = Column(Integer, primary_key=True)
    loan_id = Column(Integer, ForeignKey(f"{LOAN_TABLE_NAME}.id"), nullable=False, index=True)

    date = Column(Date(), nullable=False)
    interest_accrual_amount = Column(DECIMAL(precision=25, scale=10), nullable=False)
    interest_accrual_amount_without_margin = Column(DECIMAL(precision=25, scale=10), nullable=False)
    days_elapsed_since_loan_start_date = Column(Integer, nullable=False)


Base.metadata.create_all(engine)
