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
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

engine = create_engine(os.environ["DB_CONNECTION_STRING"])
Base = declarative_base()


class BaseInterestRate(Base):
    __tablename__ = "base_interest_rate"
    id = Column(Integer, primary_key=True)
    currency = Column(String(3), nullable=False)
    date = Column(Date(), nullable=False)
    interest_rate = Column(DECIMAL(precision=25, scale=10), nullable=False)

    __table_args__ = (
        UniqueConstraint('currency', 'date', name='currency_date'),
        Index('currency_date_index', "currency", "date")
    )


class Loan(Base):
    __tablename__ = 'loan'
    id = Column(Integer, primary_key=True)

    amount = Column(DECIMAL(precision=25, scale=10), nullable=False)
    currency = Column(String(3), nullable=False)
    base_interest_rate = Column(DECIMAL(precision=25, scale=10), nullable=False)
    margin = Column(DECIMAL(precision=25, scale=10), nullable=False)
    start_date = Column(Date(), default=datetime.now, nullable=False)
    end_date = Column(Date(), default=datetime.now, nullable=False)

    total_interest = Column(DECIMAL(precision=25, scale=10), nullable=False)

    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)


class LoanCalculationResult(Base):
    __tablename__ = "loan_calculation_result"
    id = Column(Integer, primary_key=True)
    loan_id = Column(Integer, ForeignKey("loan.id"), nullable=False, index=True)

    date = Column(Date(), nullable=False)
    interest_accrual_amount = Column(DECIMAL(precision=25, scale=10), nullable=False)
    interest_accrual_amount_without_margin = Column(DECIMAL(precision=25, scale=10), nullable=False)
    days_elapsed_since_loan_start_date = Column(Integer, nullable=False)


Base.metadata.create_all(engine)
