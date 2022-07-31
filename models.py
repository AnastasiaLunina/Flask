from sqlalchemy import (Column, DateTime, Integer, String, create_engine, func,)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


PG_DSN = 'postgresql://POSTGRES_USER:POSTGRES_PASSWORD@localhost:5432/POSTGRES_DB'
engine = create_engine(PG_DSN)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class AdModel(Base):
    __tablename__ = 'advertisements'

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    owner = Column(String(255), index=True, nullable=False)


Base.metadata.create_all(engine)
