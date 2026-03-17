import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.core.config import (
    EMAIL_HOST,
    EMAIL_PORT,
    EMAIL_USER,
    EMAIL_PASSWORD,
    EMAIL_USE_TLS,
    EMAIL_USE_SSL,
)


def send_smtp_email(to_email: str, subject: str, body: str) -> str:
    email_host = EMAIL_HOST
    email_port = EMAIL_PORT
    email_user = EMAIL_USER
    email_password = EMAIL_PASSWORD

    if not email_user or not email_password:
        return "Չհաջողվեց ուղարկել Էլ. փոստը:"

    if not to_email or "@" not in to_email:
        return "Չուղարկվեց (էլ. հասցեն սխալ է կամ բացակայում է)"

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        use_ssl = EMAIL_USE_SSL or (email_port == 465)
        use_tls = EMAIL_USE_TLS or (email_port == 587)

        if use_ssl:
            server = smtplib.SMTP_SSL(email_host, email_port)
        else:
            server = smtplib.SMTP(email_host, email_port)

        with server:
            server.ehlo()
            if use_tls and not use_ssl:
                server.starttls()
                server.ehlo()
            server.login(email_user, email_password)
            server.sendmail(email_user, to_email, msg.as_string())
        return "Հաջողությամբ ուղարկվեց"
    except Exception as e:
        return f"SMTP Սխալ: {str(e)}"


# EMAILI funkcianery sax stex berel
