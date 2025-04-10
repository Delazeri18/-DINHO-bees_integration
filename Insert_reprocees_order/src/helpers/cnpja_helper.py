import requests
import os
from helpers.structlogger import get_logger

logger = get_logger()

def consultar_cnpja(cnpj):
    # URL base com o CNPJ como variável
    url = f"https://api.cnpja.com/office/{cnpj}?geocoding=true" 
    api_key = ''
    headers = {'Authorization': api_key}
    
    try:
        # Fazendo a requisição GET
        response = requests.get(url, headers=headers)
        
        # Verifica se a requisição foi bem-sucedida
        if response.status_code == 200:
            dados = response.json()  # Converte a resposta JSON em dicionário Python
            
            # Verificar status do CNPJ
            status_cnpj = dados.get('status', {}).get('text', 'Desconhecido')
            
            # Extrair o dicionário de endereço
            endereco = dados.get('address', {})
            
            # Retornar os dados necessários
            return {
                "status": status_cnpj,
                "endereco": endereco,  # Retorna o dicionário de endereço
                "dados_completos": dados,  # Retorna a resposta completa para uso futuro
            }
        else:
            logger.info(f"Erro ao consultar API: {response.status_code}")
            return None
    except Exception as e:
        logger.info(f"Erro durante a consulta: {e}")
        return None
