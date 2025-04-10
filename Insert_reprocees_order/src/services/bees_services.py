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
        'client_secret': ''
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

def add_order_to_bulk(id_bees, new_status, center, placementDate, dia_max):

    """
    Adiciona o pedido a uma lista para envio em bulk posteriormente.

    :param id_bees: ID do pedido (str)
    :param new_status: Novo status do pedido (str)
    :param center: Centro de entrega Bees (str)
    :param placementDate: Data de colocação do pedido (datetime)
    """
    # Adiciona 3 dias à data de colocação para entrega futura
    
    dt = datetime.now(timezone.utc)
    current_date = dt.isoformat().replace('+00:00', 'Z')

    if placementDate != None and dia_max != None:
        if isinstance(placementDate, str):
            placementDate_format = isoparse(placementDate)
    
    future_datetime = placementDate_format + timedelta(days=dia_max)
    future_datetime_iso = future_datetime.isoformat(timespec='milliseconds')



    print(f'iso formato: {future_datetime_iso} ')
    if center == 4:
        center = "UMBARA" 
    elif center == 5:
        center = 'Cascavel'
    elif center == 3:
        center = 'Cascavel'
    elif center == 7:
        center = 'UMBARA'

    
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
                    "deliveredDate": current_date,
                    "date": current_date
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
        "country": "",
        "Content-Type": "",
        "accept": "",
        "requestTraceId": ""
    }

    # Enviar a requisição PATCH
    response = requests.patch(url, json=payload, headers=headers)

    # Limpar a lista após envio
    bulk_orders.clear()

    # Verifica a resposta
    if response.status_code == 200:
        print({"status": "success", "data": response.json()})
    elif response.status_code == 202:
        print({"status": "processing", "data": response.text})
    else:
        print({"status": "error", "code": response.status_code, "message": response.text})