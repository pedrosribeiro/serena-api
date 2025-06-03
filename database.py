from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, SQLModel, create_engine

from models.user import User
from utils.jwt import decode_access_token

DATABASE_URL = "sqlite:///./serena.db"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    from sqlalchemy.exc import IntegrityError

    from models import medication, prescription, report, senior, symptom, user
    from models.medication import Medication
    from models.user import User

    SQLModel.metadata.create_all(engine)

    # Popula a tabela de medicações se estiver vazia
    with Session(engine) as session:
        if not session.query(Medication).first():
            meds = [
                Medication(name="Paracetamol", description="Analgésico e antitérmico"),
                Medication(name="Dipirona", description="Analgésico e antitérmico"),
                Medication(name="Ibuprofeno", description="Anti-inflamatório"),
                Medication(name="Amoxicilina", description="Antibiótico"),
                Medication(name="Losartana", description="Anti-hipertensivo"),
                Medication(name="Metformina", description="Antidiabético oral"),
                Medication(name="Omeprazol", description="Inibidor de bomba de próton"),
                Medication(name="Sinvastatina", description="Redutor de colesterol"),
                Medication(name="AAS", description="Antiplaquetário"),
                Medication(name="Ranitidina", description="Antiácido"),
            ]
            session.add_all(meds)
            session.commit()
        # Cria usuário admin padrão se não existir
        if not session.query(User).filter(User.email == "admin@serena.com").first():
            from passlib.context import CryptContext

            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            admin = User(
                name="Admin",
                email="admin@serena.com",
                password=pwd_context.hash("admin123"),
                role="caregiver",
            )
            session.add(admin)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()


def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    user = db.query(User).filter(User.email == username).first()
    if user is None:
        raise credentials_exception
    return user
