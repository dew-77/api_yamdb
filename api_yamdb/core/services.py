import random
import string
from django.core.mail import send_mail
from django.template.loader import render_to_string


def generate_confirmation_code(length=6):
    """Генерирует случайный код подтверждения заданной длины."""
    characters = string.digits
    confirmation_code = "".join(
        random.choice(characters) for _ in range(length)
    )
    return confirmation_code


def send_confirmation_email(email, confirmation_code):
    """Отправляет email с кодом подтверждения на указанный адрес."""
    subject = "Подтверждение регистрации"
    message = render_to_string(
        "confirmation_email.html", {"code": confirmation_code}
    )
    from_email = "yamdb@yamdb.com"
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)
