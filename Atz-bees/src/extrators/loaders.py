import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from extrators.bigquery import *
from datetime import datetime

BigQuery = BigQuery()

# atualizando diretorio de dados 
def update_data():
    BigQuery.get_addrees_delivery()
    BigQuery.get_produtos_data()
    BigQuery.get_city()
    BigQuery.get_client()
    BigQuery.get_uf()
    BigQuery.get_bairros()



