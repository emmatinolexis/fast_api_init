from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus


user = 'mvistaging'
password = 'mv15t%40g3db45Ag3'
host = '15.236.33.216'
port = '5432'
database = 'mvi_staging_db'

POSTGRES_DATABASE_URL = f'postgresql://{user}:{password}@{host}:{port}/{database}'

engine = create_engine(POSTGRES_DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

try:
    with engine.connect() as connection_str:
        print('Successfully connected to the PostgreSQL database')
except Exception as ex:
    print(f'Sorry failed to connect: {ex}')


Base = declarative_base()


def init_db():
    Base.metadata.create_all(engine)
