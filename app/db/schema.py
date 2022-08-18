import os
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Integer,
    String,
    Column,
    DateTime,
    ForeignKey,
    Numeric,
    Date,
    Float
)
from sqlalchemy.dialects.postgresql import (
    DOUBLE_PRECISION,
    JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_json import mutable_json_type
from datetime import datetime

engine = create_engine(os.environ["DB_CONNECTION_STRING"])
Base = declarative_base()


class Loan(Base):
    __tablename__ = 'loan'
    id = Column(Integer, primary_key=True)

    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)
    base_interest_rate = Column(DOUBLE_PRECISION, nullable=False)
    margin = Column(Float, nullable=False)

    start_date = Column(Date(), default=datetime.now, nullable=False)
    end_date = Column(Date(), default=datetime.now, nullable=False)

    calculation_result = Column(mutable_json_type(dbtype=JSON, nested=True))

    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)


Base.metadata.create_all(engine)
