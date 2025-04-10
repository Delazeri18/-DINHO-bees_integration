from extrators.bigquery import BigQuery
from helpers.helper_send import send_email_with_attachment, send_email
import os
import logging
import pandas as pd
from datetime import datetime, timedelta

def send():
        BigQuery2 = BigQuery()

        #importando df
        df_error = BigQuery2.ler_dados()
        logging.info("Dados extraidos - GCP")

        # trasnformando em excel e salvando
        file_path ="Relatório"
        df_error.to_excel(file_path, index=False, engine='openpyxl')

        # mandando email 
        send_email_with_attachment(
                subject="Relatório de Pedidos com Erro",
                body="Segue anexo o relatório de pedidos com erro na inserção.",  # TODO  colcoar identificador para saber quantas vezes foram enviados os emails
                recipient="Kewin.delazeri@dinhodistribuidora.com.br",
                attachment_path=file_path
        )
        # apagando arquivo. 
        os.remove(file_path)
        logging.info(f"Arquivo {file_path} excluído com sucesso.")

def send_cadastro(msg):

        # mandando email 
        send_email(
                subject="Cliente para cadstrar Bees",
                body=f"Segue dados de cliente para cadstrar:  {msg}",  # TODO  colcoar identificador para saber quantas vezes foram enviados os emails
                recipient="Kewin.delazeri@dinhodistribuidora.com.br",
        )

def send_alert_orders():
        BigQuery2 = BigQuery()

        #importando df
        df_error = BigQuery2.get_failed_orders()
        logging.info("Dados extraidos - GCP")

        df = df_error[df_error['create_date'] <= datetime.now() - timedelta(days=7)]

        # trasnformando em excel e salvando
        file_path ="Relatório"
        df.to_excel(file_path, index=False, engine='openpyxl')

        # mandando email 
        send_email_with_attachment(
                subject="Relatório de Pedidos que serão cancelados hoje",
                body="Segue anexo o relatório de pedidos com erro na inserção.",  # TODO  colcoar identificador para saber quantas vezes foram enviados os emails
                recipient="Kewin.delazeri@dinhodistribuidora.com.br",
                attachment_path=file_path
        )
        # apagando arquivo. 
        os.remove(file_path)
        logging.info(f"Arquivo {file_path} excluído com sucesso.")        

def send_divergencias(msg):
        # mandando email 
        send_email(
                subject="Clientes com Lat e Long diferentes",
                body=f"Segue dados de cliente:  {msg}",  # TODO  colcoar identificador para saber quantas vezes foram enviados os emails
                recipient="Kewin.delazeri@dinhodistribuidora.com.br",
        )
