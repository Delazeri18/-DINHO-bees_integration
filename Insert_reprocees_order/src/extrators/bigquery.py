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
            #print("Consulta executada com sucesso!")
            return df
        except Exception as e:
            #(f"Erro ao executar a consulta: {e}")
            return None

    def insert_order_sql(self, dados):
        """
        Insere um pedido na tabela Orders_Bees do BigQuery usando SQL padrão.

        Args:
            dados (dict): Dicionário contendo os campos a serem inseridos.
        """
        tabela = "dinho-dw.update_control.orders_Bees"

        # Verificar se o dicionário tem os campos obrigatórios
        required_fields = ["id_bees", "new_status", "old_status", "filial"]
        for field in required_fields:
            if field not in dados:
                raise ValueError(f"O campo '{field}' é obrigatório.")

        # Criar a query de inserção com base no dicionário
        query = f"""
            INSERT INTO `{tabela}` 
                (id_bees, id_topsytem, old_status, new_status, filial, error, create_date, max_days, bonificado)
            VALUES (
                '{dados["id_bees"]}',
                {'NULL' if dados.get("id_topsytem") is None else f"'{dados['id_topsytem']}'"},
                '{dados["old_status"]}',
                '{dados["new_status"]}',
                '{dados["filial"]}',
                {'NULL' if dados.get("error") is None else f"'{dados['error']}'"},
                {'NULL' if dados.get("create_date") is None else f"'{dados['create_date']}'"},
                { "NULL" if dados.get("max_days") is None else int(dados["max_days"]) },
                { "NULL" if dados.get("bonificado") is None else f"'{dados['bonificado']}'"}
            );
        """

        try:
            # Executar a consulta
            query_job = self.client.query(query)
            query_job.result()  # Aguarda a conclusão da consulta
            logger.info(f"Pedido com id_bees='{dados['id_bees']}' inserido com sucesso.")
        except Exception as e:
            logger.info(f"Erro ao inserir pedido no BigQuery: {e}")

    def update_order(self, dados):
        """
        Atualiza um pedido na tabela Orders_Bees do BigQuery com base em um dicionário.

        Args:
            dados (dict): Dicionário contendo os campos a serem atualizados. Deve conter:
                - id_bees (str): ID do pedido no Bees (obrigatório).
                - new_status (str): Novo status do pedido.
                - id_topsystem (str, optional): ID do pedido no TopSystem.
        """
        tabela = "dinho-dw.update_control.orders_Bees"

        # Verificar se o dicionário tem os campos obrigatórios
        if "id_bees" not in dados or "new_status" not in dados:
            raise ValueError("O dicionário deve conter 'id_bees' e 'new_status'.")

        # Criar a query dinâmica com base no dicionário
        query = f"""
            UPDATE `{tabela}`
            SET
                new_status = '{dados["new_status"]}',
                id_topsytem = {f"NULL" if dados.get("id_topsytem") is None else f"'{dados['id_topsytem']}'"},
                old_status = '{dados["old_status"]}',
                filial = '{dados["filial"]}',
                error = {f"NULL" if dados.get("error") is None else f"'{dados['error']}'"},
                bonificado = {f"NULL" if dados.get("bonificado") is None else f"'{dados['bonificado']}'"}
            WHERE id_bees = '{dados["id_bees"]}'
        """

        try:
            # Executa a consulta
            query_job = self.client.query(query)
            query_job.result()  # Aguarda a conclusão da consulta
            print(f"Pedido com id_bees='{dados['id_bees']}' atualizado com sucesso.")
        except Exception as e:
            print(f"Erro ao atualizar pedido no BigQuery: {e}")

    def get_failed_orders(self):
        query = """
        SELECT 
            id_bees
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

    def get_city(self): 
        query = """
            SELECT 
                codigo,
                codigofiscal
            FROM 
                `dinho-dw.topsystem_raw.CIDADE`
            """        
        try:
            # Executar a consulta e armazenar os resultados em um DataFrame
            df = self.client.query(query).to_dataframe()
            logger.info("Consulta executada com sucesso!")
            # Converter o DataFrame para JSON (lista de registros)
            result_json = df.to_json(orient='records')
            
            # Definir o caminho completo do arquivo para salvar o JSON
            file_path = rf"{BASE_DIR}/data/city_json.json"
            
            # Salvar o JSON no arquivo
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(result_json)
            
            return result_json

        except Exception as e:
            logger.info(f"Erro ao executar a consulta: {e}")
            return None

    def get_addrees_delivery(self):
        query = """
            SELECT 
                clifor,
                id
            FROM 
                `dinho-dw.topsystem_raw.CLIFORENDERECO`
            """ 
        try:
            # Executar a consulta e armazenar os resultados em um DataFrame
            df = self.client.query(query).to_dataframe()
            logger.info("Consulta executada com sucesso!")
            # Converter o DataFrame para JSON (lista de registros)
            result_json = df.to_json(orient='records')
            
            # Definir o caminho completo do arquivo para salvar o JSON
            file_path = rf"{BASE_DIR}/data/endereco_entroga.json"
            
            # Salvar o JSON no arquivo
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(result_json)
            
            return result_json
        
        except Exception as e:
            logger.info("Consulta executada com sucesso!")
            return None
              
    def get_uf(self):
        query = """
            SELECT 
                codigo, uf
            FROM 
                `dinho-dw.topsystem_raw.ESTADO`
            """ 
        try:
            # Executar a consulta e armazenar os resultados em um DataFrame
            df = self.client.query(query).to_dataframe()
            logger.info("Consulta executada com sucesso!")
            # Converter o DataFrame para JSON (lista de registros)
            result_json = df.to_json(orient='records')
            
            # Definir o caminho completo do arquivo para salvar o JSON
            file_path = rf"{BASE_DIR}/data/uf_json.json"
            
            # Salvar o JSON no arquivo
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(result_json)
            
            return result_json

        except Exception as e:
            print(f"Erro ao executar a consulta: {e}")
            return None

    def get_client(self):
        query = """
            SELECT 
                cliente, 
                cnpj
            FROM 
                `dinho-dw.gsheets.clientes_bees_centro` 
            """ 
        try:
            # Executar a consulta e armazenar os resultados em um DataFrame
            df = self.client.query(query).to_dataframe()
            logger.info("Consulta executada com sucesso!")

            # Converter o DataFrame para uma lista de dicionários
            result_list = df.to_dict(orient='records')

            # Definir o caminho completo do arquivo para salvar o JSON
            file_path = rf"{BASE_DIR}/data/client.json"

            # Salvar o JSON no arquivo corretamente
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(result_list, f, ensure_ascii=False, indent=4)  # Formatação mais legível

            return json.dumps(result_list, ensure_ascii=False)

        except Exception as e:
            logger.info(f"Erro ao executar a consulta: {e}")
            return None

    def get_bairros(self):
        query = """
                SELECT 
                    codigo, nome
                FROM 
                    `dinho-dw.topsystem_raw.BAIRRO`
                """ 
        try:
            # Executar a consulta e armazenar os resultados em um DataFrame
            df = self.client.query(query).to_dataframe()
            logger.info("Consulta executada com sucesso!")
            # Converter o DataFrame para JSON (lista de registros)
            result_json = df.to_json(orient='records')
            
            # Definir o caminho completo do arquivo para salvar o JSON
            file_path = rf"{BASE_DIR}.json"
            
            # Salvar o JSON no arquivo
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(result_json)
            
            return result_json

        except Exception as e:
            logger.info(f"Erro ao executar a consulta: {e}")
            return None

    def get_produtos_data(self): # TODO planilha 
        query = """
            SELECT 
                *
            FROM 
                `dinho-dw.gsheets.produtos_bees`
            """ 
        try:
            # Executar a consulta e armazenar os resultados em um DataFrame
            df = self.client.query(query).to_dataframe()
            df = df.drop_duplicates(subset="sku")
            logger.info("Consulta executada com sucesso!")
            # Converter o DataFrame para JSON (lista de registros)
            json_output = df.set_index("sku").to_dict(orient="index")

            
            # Definir o caminho completo do arquivo para salvar o JSON
            file_path = rf"{BASE_DIR}/data/produtos.json"
            
            # Salvar o JSON no arquivo
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(json_output, f, indent=2, ensure_ascii=False)
            
            return json_output

        except Exception as e:
            logger.info(f"Erro ao executar a consulta: {e}")
            return None