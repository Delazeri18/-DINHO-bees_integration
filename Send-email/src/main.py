import logging
from handlers.send_email import send_update, send_alert_orders


if __name__ == "__main__":
    print("Executando o arquivo principal: main_send_email.py")
    send_update()  # Chama a função do handler
    send_alert_orders()
    print("Finalizado execução: main_send_email.py")
