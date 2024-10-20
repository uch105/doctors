import smtplib

def send_automail(to_email,subject,body):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'prescribemate'
    smtp_password = 'onvemayrrmwkdzks'

    from_email = 'prescribemate@gmail.com'

    message = f'Subject: {subject}\n\n{body}'

    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(smtp_username, smtp_password)
        try:
            smtp.sendmail(from_email, to_email, message)
            return True
        except:
            return False