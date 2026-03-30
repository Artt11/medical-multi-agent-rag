import re
import smtplib
from typing import Optional, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.database.models import PatientModel
from src.core.config import (
    EMAIL_HOST,
    EMAIL_PORT,
    EMAIL_USER,
    EMAIL_PASSWORD,
    EMAIL_USE_TLS,
    EMAIL_USE_SSL,
)

EMAIL_REGEX = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def extract_email(text: str) -> Optional[str]:
    if not text:
        return None
    match = EMAIL_REGEX.search(text)
    return match.group(0) if match else None


def find_patient_email(
    db: Session,
    patient_id: Optional[str] = None,
    patient_name: Optional[str] = None,
) -> Tuple[Optional[str], Optional[str]]:

    if patient_id:
        patient = db.query(PatientModel).filter(
            (PatientModel.patient_id == str(patient_id)) |
            (PatientModel.social_card == str(patient_id))
        ).first()
        if patient and patient.email:
            return patient.email, None

    if patient_name:
        name_value = patient_name.strip()
        if name_value:
            matches = db.query(PatientModel).filter(
                func.lower(PatientModel.name).like(f"%{name_value.lower()}%")
            ).all()
            if len(matches) > 1:
                return None, "MULTIPLE_MATCHES"
            if len(matches) == 1:
                return matches[0].email, None

    return None, None


def send_smtp_email(to_email: str, subject: str, body: str) -> str:
    if not EMAIL_USER or not EMAIL_PASSWORD:
        return "Չհաջողվեց ուղարկել: SMTP տվյալները բացակայում են:"

    if not to_email or "@" not in to_email:
        return "Չուղարկվեց (էլ. հասցեն սխալ է կամ բացակայում է)"

    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        port = int(EMAIL_PORT)

        use_ssl = EMAIL_USE_SSL or (port == 465)
        use_tls = EMAIL_USE_TLS or (port == 587)

        if use_ssl:
            server = smtplib.SMTP_SSL(EMAIL_HOST, port)
        else:
            server = smtplib.SMTP(EMAIL_HOST, port)

        with server:
            server.ehlo()
            if use_tls and not use_ssl:
                server.starttls()
                server.ehlo()

            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, to_email, msg.as_string())

        return "Հաջողությամբ ուղարկվեց"
    except Exception as e:
        return f"SMTP Սխալ: {str(e)}"
