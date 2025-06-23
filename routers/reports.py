from datetime import date, datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database import get_current_user, get_session
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
from schemas.report import ReportCreate, ReportRead
from utils.jwt import decode_access_token

router = APIRouter()


@router.get("/report/{senior_id}", dependencies=[Depends(get_current_user)])
def get_consolidated_report(senior_id: str, db: Session = Depends(get_session)):
    # Busca o idoso
    senior = db.query(Senior).filter(Senior.id == senior_id).first()
    if not senior:
        raise HTTPException(status_code=404, detail="Senior not found")

    # Nome, idade, identificador
    name = senior.name
    # Calcula idade
    try:
        birth_date = datetime.strptime(senior.birth_date, "%d/%m/%Y")
        today = date.today()
        age = (
            today.year
            - birth_date.year
            - ((today.month, today.day) < (birth_date.month, birth_date.day))
        )
    except Exception:
        age = None
    identifier = senior.id

    # Médicos vinculados
    user_seniors = db.query(UserSenior).filter(UserSenior.senior_id == senior_id).all()
    doctor_ids = [us.user_id for us in user_seniors]
    doctors = (
        db.query(User).filter(User.id.in_(doctor_ids), User.role == "doctor").all()
    )
    doctors_list = [
        {
            "name": d.name,
            "specialty": "Geriatria" if "geri" in d.name.lower() else "Médico",
        }
        for d in doctors
    ]

    # Prescrições
    prescriptions = (
        db.query(Prescription).filter(Prescription.senior_id == senior_id).all()
    )
    prescriptions_list = []
    for p in prescriptions:
        med = db.query(Medication).filter(Medication.id == p.medication_id).first()
        prescriptions_list.append(
            {
                "name": med.name if med else "",
                "dosage": p.dosage,
                "frequency": p.frequency,
            }
        )

    # Sintomas
    symptoms = (
        db.query(Symptom)
        .filter(Symptom.senior_id == senior_id)
        .order_by(Symptom.created_at.desc())
        .all()
    )

    def pain_level_to_pt(level):
        if level <= 2:
            return "Leve"
        elif level <= 5:
            return "Moderado"
        else:
            return "Forte"

    symptoms_list = [
        {
            "name": s.name,
            "date": s.created_at.strftime("%d/%m/%Y"),
            "time": s.created_at.strftime("%H:%M"),
            "severity": pain_level_to_pt(s.pain_level),
        }
        for s in symptoms
    ]

    # Histórico de medicação (simulado: doses previstas e tomadas)
    # Aqui, normalmente, buscaria uma tabela de doses tomadas. Como não há, simula com horários das prescrições.
    medication_history = []
    for p in prescriptions:
        med = db.query(Medication).filter(Medication.id == p.medication_id).first()
        # Para cada horário previsto, simula se foi tomada (alternando True/False)
        times = []
        if p.frequency:
            if ":" in p.frequency:
                times = [t.strip() for t in p.frequency.split(",")]
            else:
                times = [
                    f"{int(h):02d}:00"
                    for h in p.frequency.replace(",", " ").split()
                    if h.isdigit()
                ]
        for idx, t in enumerate(times):
            # Simula datas recentes
            dt = datetime.now().replace(
                hour=int(t[:2]), minute=int(t[3:]), second=0, microsecond=0
            )
            medication_history.append(
                {
                    "name": med.name if med else "",
                    "date": dt.strftime("%d/%m/%Y"),
                    "time": dt.strftime("%H:%M"),
                    "taken": idx % 2 == 0,  # alterna True/False
                }
            )

    return JSONResponse(
        {
            "name": name,
            "age": age,
            "identifier": identifier,
            "doctors": doctors_list,
            "prescriptions": prescriptions_list,
            "symptoms": symptoms_list,
            "medicationHistory": medication_history,
        }
    )
