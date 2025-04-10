from google.cloud import bigquery
from google.oauth2 import service_account # type: ignore
import json
import os 
from pathlib import Path
from helpers.structlogger import get_logger

logger = get_logger()

BASE_DIR = Path(os.getenv("PYTHONPATH", "/app/src")).resolve()

class BigQuery:
    def __init__(self):
        # Obter o caminho das credenciais do ambiente
        credential_path = f'{BASE_DIR}/credentials/credential.json'
        credentials = service_account.Credentials.from_service_account_file(
            credential_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        self.client = bigquery.Client(credentials=credentials)
        self.dataset_id = "update_control"

    def ler_dados(self):
        query = """
        SELECT 
            id_bees,
            id_topsytem,
            old_status,
            new_status,
            filial,
            error,
            create_date, 
            bonificado,
            max_days
        FROM    
            `dinho-dw.update_control.orders_Bees`
        """ 
        
        try:
            # Executar a consulta e armazenar os resultados em um DataFrame
            df = self.client.query(query).to_dataframe()
            logger.info("Consulta executada com sucesso!")
            return df
        except Exception as e:
            logger.info(f"Erro ao executar a consulta: {e}")
            return None

    def get_failed_orders(self):
        query = """
        SELECT 
            id_bees,
            id_topsytem,
            old_status,
            new_status,
            filial,
            error,
            create_date
        FROM 
            `dinho-dw.update_control.orders_Bees`
        WHERE 
            new_status = "VERIFY"
        """ 
        
        try:
            # Executar a consulta e armazenar os resultados em um DataFrame
            df = self.client.query(query).to_dataframe()
            logger.info("Consulta executada com sucesso!")
            
            # Converter o DataFrame para uma lista
            failed_orders = df['id_bees'].tolist()
            return failed_orders
        except Exception as e:
            logger.info(f"Erro ao executar a consulta: {e}")
            return []
