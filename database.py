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

        # Popula as demais tabelas se não houver dados
        import uuid
        from datetime import datetime, timedelta

        from passlib.context import CryptContext

        from models.compartment import Compartment
        from models.device import Device
        from models.dispenser import Dispenser
        from models.medication import Medication
        from models.prescription import Prescription
        from models.report import Report
        from models.senior import Senior
        from models.symptom import Symptom
        from models.user import User
        from models.usersenior import UserSenior

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        # Doctor
        doctor = session.query(User).filter(User.email == "doctor@serena.com").first()
        if not doctor:
            doctor = User(
                name="Dr. Serena",
                email="doctor@serena.com",
                password=pwd_context.hash("doctor123"),
                role="doctor",
            )
            session.add(doctor)
            session.commit()
            session.refresh(doctor)
        # Senior
        senior = session.query(Senior).filter(Senior.name == "Paciente Exemplo").first()
        if not senior:
            senior = Senior(
                name="Paciente Exemplo",
                birth_date="01/01/1950",
                created_at=datetime.utcnow().isoformat(),
            )
            session.add(senior)
            session.commit()
            session.refresh(senior)
        # UserSenior - Doctor
        if (
            not session.query(UserSenior)
            .filter(UserSenior.user_id == doctor.id, UserSenior.senior_id == senior.id)
            .first()
        ):
            usersenior_doctor = UserSenior(user_id=doctor.id, senior_id=senior.id)
            session.add(usersenior_doctor)
            session.commit()
        # Caregiver
        caregiver = session.query(User).filter(User.email == "admin@serena.com").first()
        # Device
        device = session.query(Device).filter(Device.senior_id == senior.id).first()
        if not device:
            device = Device(
                id="0",
                senior_id=senior.id,
                status="active",
                last_sync=datetime.utcnow(),
            )
            session.add(device)
            session.commit()
            session.refresh(device)
        # Dispenser
        dispenser = (
            session.query(Dispenser).filter(Dispenser.device_id == device.id).first()
        )
        if not dispenser:
            dispenser = Dispenser(device_id=device.id)
            session.add(dispenser)
            session.commit()
            session.refresh(dispenser)
        # Compartments
        if (
            not session.query(Compartment)
            .filter(Compartment.dispenser_id == dispenser.id)
            .first()
        ):
            meds = session.query(Medication).all()
            for i in range(14):
                # Deixe os 3 últimos compartimentos sem medicação
                if i >= 11:
                    med_id = ""
                    quantity = 0
                else:
                    med_id = meds[i % len(meds)].id if meds else None
                    quantity = 10 + i
                compartment = Compartment(
                    dispenser_id=dispenser.id,
                    medication_id=med_id,
                    quantity=quantity,
                )
                session.add(compartment)
            session.commit()
        # UserSenior
        if (
            not session.query(UserSenior)
            .filter(
                UserSenior.user_id == caregiver.id, UserSenior.senior_id == senior.id
            )
            .first()
        ):
            usersenior = UserSenior(user_id=caregiver.id, senior_id=senior.id)
            session.add(usersenior)
            session.commit()
        # Prescriptions
        if (
            not session.query(Prescription)
            .filter(Prescription.senior_id == senior.id)
            .first()
        ):
            meds = session.query(Medication).all()
            frequencies = [
                "8",
                "12",
            ]  # Frequências diferentes para os dois medicamentos
            for idx, med in enumerate(meds[:2]):
                prescription = Prescription(
                    senior_id=senior.id,
                    medication_id=med.id,
                    doctor_id=doctor.id,
                    description=f"Qualquer descrição para {med.name}",
                    dosage="1 comprimido",
                    frequency=frequencies[idx] if idx < len(frequencies) else "8",
                    start_date=datetime.utcnow(),
                    end_date=datetime.utcnow() + timedelta(days=30),
                )
                session.add(prescription)
            session.commit()
        # Symptoms
        if not session.query(Symptom).filter(Symptom.senior_id == senior.id).first():
            symptom1 = Symptom(
                senior_id=senior.id,
                name="Dor de cabeça",
                description="Paciente levantou rápido e sentiu dor",
                pain_level=5,
            )
            symptom2 = Symptom(
                senior_id=senior.id,
                name="Náusea",
                description="Acordou enjoado",
                pain_level=2,
            )
            session.add_all([symptom1, symptom2])
            session.commit()
        # Report
        from models.report import Report

        if not session.query(Report).filter(Report.user_id == caregiver.id).first():
            report = Report(
                user_id=caregiver.id,
                content="Relatório inicial do paciente.",
                created_at=datetime.utcnow().isoformat(),
            )
            session.add(report)
            session.commit()


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
