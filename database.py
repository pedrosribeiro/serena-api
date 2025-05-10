from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = "sqlite:///./serena.db"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    # Importa todos os models explicitamente para garantir a criação correta das tabelas e FKs
    from models import medication, prescription, report, senior, symptom, user

    SQLModel.metadata.create_all(engine)
