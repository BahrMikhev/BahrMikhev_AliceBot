import os
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec

SqlAlchemyBase = dec.declarative_base()

__factory = None


def global_init():
    global __factory

    if __factory:
        return

    if 'DATABASE_URL' in os.environ:  # возьмём адрес базы из переменной окружения
        # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL?sslmode=require').replace('postgres://', 'postgresql://')
        conn_str = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://')  # сработает на Heroku
    else:
        from config import LOCAL_DB  # сработает локально
        conn_str = LOCAL_DB

    engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    from . import users

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()
