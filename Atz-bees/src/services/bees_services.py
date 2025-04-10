import json
import requests # type: ignore
from datetime import datetime, timezone, timedelta
from dateutil.parser import isoparse

def token_bees():
    # URL do serviço de autenticação para o ambiente UAT
    url = ''

    # Cabeçalhos
    headers = {
        'Content-Type': '',
        "requestTraceId": ""
    }

    # Dados do corpo da requisição
    data = {
        'client_id': '',
        'client_secret': '',
        'scope': '',
        'grant_type': '',
    }

    # Enviando a requisição POST
    response = requests.post(url, headers=headers, data=data)

    # Verificando o status da resposta
    if response.status_code == 200:
        # Se a requisição foi bem-sucedida, imprime o token de acesso
        token_data = response.json()
        access_token = token_data.get('access_token')
        return access_token
    
    else:
        # Caso a requisição falhe, imprime o erro
        print('Erro ao obter o token. Status code:', response.status_code)
        print('Detalhes:', response.text)

def normalize_iso(date_str):
    """
    Normaliza uma string de data no formato ISO 8601 para garantir que
    a parte fracionária (milissegundos) tenha 6 dígitos, se presente.
    """
    if '.' in date_str:
        date_part, frac = date_str.split('.')
        # Remove o sufixo de fuso horário (ex: 'Z')
        frac = frac.rstrip('Z')
        # Preenche com zeros à direita para ter 6 dígitos
        frac = frac.ljust(6, '0')
        normalized = f"{date_part}.{frac}"
        # Se a string original terminava com 'Z', adiciona-o novamente
        if date_str.endswith('Z'):
            normalized += 'Z'
        return normalized
    return date_str

def add_order_to_bulk(id_bees, new_status, center, datahora):

    """
    Adiciona o pedido a uma lista para envio em bulk posteriormente.

    :param id_bees: ID do pedido (str)
    :param new_status: Novo status do pedido (str)
    :param center: Centro de entrega Bees (str)
    :param placementDate: Data de colocação do pedido (datetime)
    """
    # Adiciona 3 dias à data de colocação para entrega futura

        # Se datahora for fornecida, normalize e converta para datetime
    if datahora:
        # Se datahora já for datetime, converte para string ISO
        if isinstance(datahora, datetime):
            datahora_str = datahora.isoformat()
        else:
            datahora_str = str(datahora)
        normalized_date = normalize_iso(datahora_str)
        # Remove 'Z' para usar fromisoformat e depois ajusta o tzinfo para UTC
        formatted_date = datetime.fromisoformat(normalized_date.rstrip('Z')).replace(tzinfo=timezone.utc).isoformat().replace('+00:00', 'Z')
    else:
        formatted_date = None
        
    if center == 4:
        center = "UMBARA" 
    elif center == 5:
        center = 'Cascavel'
    elif center == 3:
        center = 'Cascavel'
    elif center == 7:
        center = 'UMBARA'
    elif center == 6:
        center = 'BIGUACU'

    
    # Você pode adicionar outros mapeamentos de centro aqui.

    # Cria o payload para o pedido
    if new_status == "PLACED":
        payload_data = {
            "order" : {
                "orderNumber": id_bees,
                "status": new_status,
                "deliveryCenterId": center,
                
            }
        }
    elif new_status == "DELIVERED":
        payload_data = {
            "order" : {
                "orderNumber": id_bees,
                "status": new_status,
                "delivery": {
                    "deliveryCenterId": center,
                    "deliveredDate": formatted_date,
                    "date": formatted_date
                }
            }   
        }
    elif new_status == "CONFIRMED":
        payload_data = {
            "order" : {
                "orderNumber": id_bees,
                "status": new_status,
                "delivery": {
                    "deliveryCenterId": center
                }
            }
        }
    elif new_status == "CANCELLED":
        payload_data = {
            "order" : {
                "orderNumber": id_bees,
                "status": new_status,
                "delivery": {
                    "deliveryCenterId": center,
                }
            }
        }
    elif new_status == "DENIED":
        payload_data = {
            "order" : {
                "orderNumber": id_bees,
                "status": new_status,
                "delivery": {
                    "deliveryCenterId": center
                }
            }
        }
    else:
        raise ValueError("Status inválido. Use 'PLACED', 'DELIVERED', 'CONFIRMED' ou 'CANCELLED'.")
    return payload_data

def send_bulk_orders(token, bulk_orders):
    """
    Envia todos os pedidos armazenados em bulk_orders em uma única solicitação para a API.

    :param token: Token de autenticação (str)
    """
    if not bulk_orders:
        return {"status": "error", "message": "Nenhum pedido para enviar."}

    # Monta o payload para o envio em bulk
    payload = {
        "entity": "ORDERS",
        "version": "v3",
        "payload": json.dumps(bulk_orders)
    }

    # URL da API
    url = ""

    # Cabeçalhos da requisição
    headers = {
        "Authorization": f"Bearer {token}",
        "country": "BR",
        "Content-Type": "application/json",
        "accept": "application/json",
        "requestTraceId": "bulk-request"
    }

    # Enviar a requisição PATCH
    response = requests.patch(url, json=payload, headers=headers)

    # Verifica a resposta
    if response.status_code == 200:
        print({"status": "success", "data": response.json()})
    elif response.status_code == 202:
        print({"status": "processing", "data": response.text})
    else:
        print({"status": "error", "code": response.status_code, "message": response.text})