import requests # type: ignore
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from datetime import datetime, timedelta
from helpers.cnpja_helper import consultar_cnpja
from services.top_services import *
from helpers.helper import *
from extrators.bigquery import BigQuery
from services.bees_services import token_bees, add_order_to_bulk, send_bulk_orders
from helpers.structlogger import get_logger
from handlers.send_email import send_cadastro, send_divergencias
from pathlib import Path

BASE_DIR = Path(os.getenv("PYTHONPATH", "/app/src")).resolve()
logger = get_logger()

def insert_order():
    logger.info("Iniciando o processo de inserção de pedidos")
    token = token_bees()
    # URL da API
    url = ''

    # Headers
    headers = {
        'Authorization': f'Bearer {token}',
        'requestTraceId': '',
        'country': '',
        'Content-Type': '',
    }
    # Enviando a requisição GET
    response = requests.get(url, headers=headers)

    BigQuery2 = BigQuery()

    # Verificando a resposta
    if response.status_code == 200:
        logger.info("Extraindo pedido")  
        data = response.json()

        bulk_orders = []
        div_lat_long = []

        # Iterando sobre todos os pedidos
        for order in data.get('orders', [0]):
 
            # determinando variaveis
            id_bees = order['orderNumber']
            if id_bees not in {'9216704964','9216707436', '9216727540', '9216729714','9216732659','9216740336','9216740824','921674964','9216743544','9216746162','9216746691','9216750579','9216754000','9216754420','9216756798','9216773311'}:
                continue
            center = order['delivery']['deliveryCenterId']
            payment_method = order['payment']['paymentMethod']
            cnpj = order['invoicing']['taxIds'][0]['value']
            dia_max = order["delivery"]["distributionCenters"][0]["maxDays"]
            placementDate = order['placementDate']
            dia_max = int(dia_max)
            telefone = order['invoicing']['phone']
            fantasia = order['invoicing']['displayName']


            # tratando a data atual para Emissão e Entrega
            # Converter a string para um objeto datetime
            dt = datetime.fromisoformat(placementDate)

            # Formatando para o formato desejado: YYYY-MM-DD
            data_formatada = dt.strftime("%Y-%m-%d")

            # validar filial ( ver como são as outras )
            if center == 'UMBARA':
                filial = 4
                tabela_preco = 170

            if center == 'Cascavel':
                filial = 5
                tabela_preco = 570            

            if center == 'CAMBE':
                tabela_preco = 370
                filial = 3
                
            if center == 'BIGUACU':
                tabela_preco = 650
                filial = 6
                continue

            # validando tabela preço 
            if payment_method == 'CASH':
                forma_pagamento = 1
            
            if payment_method == 'PIX_AT_DELIVERY':
                forma_pagamento = 47
            
            if payment_method == 'CREDIT_CARD_POS':
                forma_pagamento = 15

            if payment_method == 'CHECK': 
                forma_pagamento = 14

            # inserindo o placed
            dados = {
                "id_bees": id_bees,
                "old_status": "PENDING",
                "id_topsytem": None,
                "new_status" : "PLACED",
                "filial" : filial,
                "error" : None,
                "create_date" : data_formatada,
                "max_days" : dia_max
            }
             
            BigQuery2.insert_order_sql(dados) 
            logger.info("Status enviado: PLACED (GCP) ") # inserir placed no Banco de dados. 

            payload_data = add_order_to_bulk(id_bees, "PLACED", center,placementDate, dia_max)
            bulk_orders.append(payload_data)
            logger.info("Status atualizado na lista para Bees: PLACED") # inserir placed no Banco de dados.
            

    
            logger.info("Iniciando Validações.")
            # verificar cadastro top system. 
            id_autenticacao = autenticar_usuario_top(filial) # logando na top 
            
            status, cnpj_data = consultar_cnpj_top(cnpj, id_autenticacao) # consulta na TOP 
            if status == False: # fazer esse retornar o json completo para eu modificar apenas o endereço 
                resultado = consultar_cnpja(cnpj) #TODO nunca atualizar endereço, principalmente se ja tiver cadastro. 
                if resultado['status'] == "Ativa":
                    
                    dados = resultado.get('dados_completos', {})

                    dados['Informacao_bees'] =  {'phone': telefone,
                                                 'fantasia': fantasia,
                                                 'pedido': id_bees,
                                                 'metodo de pagamento': payment_method,
                                                 'codigo metodo de pagamento': forma_pagamento}


                    msg = json.dumps(dados, indent=4, ensure_ascii=False)

                    msg = json.dumps(resultado['dados_completos'], indent=4, ensure_ascii=False)
                    send_cadastro(msg, id_bees) # se CNPJ ativo mas sem cadastro, enviado o email para o  setor cadastro. 

                    dados = {
                        "id_bees": id_bees,
                        "old_status": "PLACED",
                        "id_topsytem": None,
                        "new_status" : "VERIFY",
                        "filial" : filial,
                        "error" : "Aguardando Cadastro",
                    }

                    BigQuery2.update_order(dados) 
                    logger.info("Status enviado: VERIFY (GCP) ") # inserir placed no Banco de dados.

                    continue

                else:  
                    payload_data = add_order_to_bulk(id_bees, "DENIED", center, placementDate, dia_max)  # atualizando GCO e Bees caso CNPJ estiver inativo
                    bulk_orders.append(payload_data)
                    logger.info("Status atualizado na lista para Bees: PLACED") # inserir placed no Banco de dados.

                    dados = {
                        "id_bees": id_bees,
                        "old_status": "PLACED",
                        "id_topsytem": None,
                        "new_status" : "DENIED",
                        "filial" : filial,
                        "error" : f"CNPJ: {resultado['status']}",
                    }

                    BigQuery2.update_order(dados) 
                    logger.info("Status enviado: DENIED (GCP) ") # inserir placed no Banco de dados.

                    continue
            else: 

                resultado = consultar_cnpja(cnpj)
                if resultado['status'] == "Ativa":

                    if str(cnpj_data["latitude"]) == str(resultado["endereco"].get("latitude")) and str(cnpj_data["longitude"]) == str(resultado["endereco"].get("longitude")):
                        logging.info("As coordenadas dos sistemas são IGUAIS.")
                    else:
                        logging.info("As coordenadas dos sistemas são DIFERENTES.")
                        dados_clifor = {
                            "cnpj" : cnpj,
                            "lat_top":cnpj_data["latitude"],
                            "long_top" : cnpj_data["longitude"],
                            "lat_receita" : resultado["endereco"].get("latitude"),
                            "long_receita" :resultado["endereco"].get("longitude")
                        }

                        div_lat_long.append(dados_clifor)
 
                    clifor = cnpj_data["codigo"]
                    
                        
                    # realizar busca se não deve ser filial 7
                    with open(rf"{BASE_DIR}/data/client.json", "r", encoding="utf-8") as arquivo:
                        clifor_f7 = json.load(arquivo)
            
                        
                    # Verifica se o cliente existe
                    for cliente in clifor_f7:
                        if cliente["cliente"] == clifor:
                            filial = 7  # Retorna 'Sim' se o cliente for encontrado
                            tabela_preco = 750
                            id_autenticacao = autenticar_usuario_top(filial) # logando na top

                    with open(rf"{BASE_DIR}/data/endereco_entrega.json", "r", encoding="utf-8") as arquivo:
                        endereco_json = json.load(arquivo)

                    for i in endereco_json:
                        if i["clifor"] == str(clifor):
                            endereco_entrega = i["id"]
                        else: 
                            endereco_entrega = None

                    condicaoPagamento = 100

                    dados_pedido = {
                        "TopSystemAutorizacao": {
                            "ID": id_autenticacao
                        },
                        "Valores": {
                            "Filial": filial,
                            "CliFor": clifor,
                            "TipoPedido": 58,
                            "Emissao": data_formatada,
                            "Entrega": data_formatada,
                            "FormaPagamento": forma_pagamento,
                            "CondicaoPagamento": condicaoPagamento,
                            "EnderecoEntrega": endereco_entrega,
                            "TotalProduto": 0,
                            "TotalRetorno": 0,
                            "PercDesconto": 0,
                            "ValorDesconto": 0,
                            "PercAcrescimo": 0,
                            "ValorAcrescimo": 0,
                            "ValorFrete": 0,
                            "Total": 0,
                            "Obs": f"Bees {id_bees}",
                            "Funcionario": 2262,
                            "TabelaPreco": tabela_preco,
                            "Pedido": id_bees,
                            "Transportador": 1,
                            "ItemPedidoList": {
                                "Items": []
                            }
                        }
                    }

                    logger.info("Transformando Json")
                    json2, json_itens_bonificado = transformar_json(order, filial) 
                    bonificado = None

                    for item in json2:
                        dados_pedido["Valores"]["ItemPedidoList"]["Items"].append({
                            "Produto": item["Produto"],
                            "Qtde": item["Qtde"],
                            "Unitario": item["Unitario"],
                            "ValorDesconto": item["ValorDesconto"],
                            "PercDesconto": item["PercDesconto"],
                            "Total": item["Total"]
                        })

                    logger.info("Enviando pedido para Top System")
                    resposta_top, novo_pedido = enviar_json_para_top(dados_pedido, id_bees, filial, bonificado) 

                    logger.info(resposta_top)

                    logger.info("Atualizando GCP")

                    BigQuery2.update_order(novo_pedido) # atualizando GCP 

                    if "Erro" not in resposta_top["result"][0]:
                        logger.info("Atualizando Bees")
                        payload_data = add_order_to_bulk(id_bees, "CONFIRMED", center, placementDate, dia_max)
                        bulk_orders.append(payload_data)
                        logger.info("Status atualizado na lista para Bees : PLACED) ") # inserir placed no Banco de dados. 

                    if json_itens_bonificado: # TODO Arrumar item bonificado 
                        bonificado = "TRUE"
                        id_bees = int(f"77{id_bees}")

                        dados_pedido["Valores"]["TipoPedido"] = 2
                        dados_pedido["Valores"]["FormaPagamento"] = 8
                        dados_pedido["Valores"]["CondicaoPagamento"] = 4
                        dados_pedido["Valores"]["Pedido"] = id_bees


                        for item in json_itens_bonificado:
                            dados_pedido["Valores"]["ItemPedidoList"]["Items"].append({
                                "Produto": item["Produto"],
                                "Qtde": item["Qtde"],
                                "Unitario": item["Unitario"],
                                "ValorDesconto": item["ValorDesconto"],  # TODO passar para o jsone  tirar o outro 
                                "PercDesconto": item["PercDesconto"],
                                "Total": item["Total"]
                            })

                        logger.info("Enviando pedido de bonificacao para Top System")
                        resposta_top, novo_pedido = enviar_json_para_top(dados_pedido, id_bees, filial, bonificado) # passando parametros para que depois possamos atualizar. 

                        logger.info(resposta_top)

                        logger.info("Atualizando GCP")

                        BigQuery2.insert_order_sql(novo_pedido) # atualizando GCP 

                    logger.info(" Pedidos Atualizados!! ")
                                    
                else: 
                    payload_data = add_order_to_bulk(id_bees, "DENIED", center,placementDate, dia_max)  # atualizando GCO e Bees caso CNPJ estiver inativo
                    bulk_orders.append(payload_data)
                    logger.info("Status atualizado na lista para Bees: PLACED") # inserir placed no Banco de dados.

                    dados = {
                        "id_bees": id_bees,
                        "old_status": "PLACED",
                        "id_topsytem": None,
                        "new_status" : "DENIED",
                        "filial" : filial,
                        "error" : f"CNPJ: {resultado['status']}",
                    }

                    BigQuery2.update_order(dados) 
                    logger.info("Status enviado: DENIED (GCP) ") # inserir placed no Banco de dados. 
        logger.info(f"Bulk de envio: \n {bulk_orders}")
        if bulk_orders != []:
            logger.info("Enviando Bulk para Bees")
            send_bulk_orders(token, bulk_orders)
        logger.info("Enviando lista de disvergentes para Ecommerce")
        if div_lat_long:
            send_divergencias(div_lat_long) # enviando e-mail de divergencia
        
                      
    else:
        logger.info('Erro ao fazer requisição. Status code:', response.status_code)
        logger.info('Detalhes:', response.text)

def reprocess_order():
     

    token = token_bees()

    # URL da API
    url = ''


    # Headers
    headers = {
        'Authorization': f'Bearer {token}',
        'requestTraceId': '',
        'country': '',
        'Content-Type': '',
    }
    # Enviando a requisição GET
    response = requests.get(url, headers=headers)

    BigQuery2 = BigQuery()

    df = BigQuery2.ler_dados()
    logger.info("Pedidos extraídos GCP")

    # Verificando a resposta
    if response.status_code == 200:
        logger.info("Extraindo pedido")  
        data = response.json()

        bulk_orders = []

        # Iterando sobre todos os pedidos
        for order in data.get('orders', [0]):

            # determinando variaveis
            id_bees = order['orderNumber']

            if id_bees in df['id_bees'].values and df.loc[df['id_bees'] == id_bees, 'new_status'].values[0] == 'VERIFY':
                logger.info(f"Processando pedido {id_bees} - Status: VERIFY")

                center = order['delivery']['deliveryCenterId']
                payment_method = order['payment']['paymentMethod']
                cnpj = order['invoicing']['taxIds'][0]['value']
                cep =  order['delivery']['location']['zipCode']     
                rua = order['delivery']['location']['streetAddress']
                cidade = order['delivery']['location']['city']
                estado = order['delivery']['location']['state']
                dia_max = order["delivery"]["distributionCenters"][0]["maxDays"]
                placementDate = order['placementDate']

                # formatando a data para o formato desejado: YYYY-MM-DD
                dt = datetime.fromisoformat(placementDate)

                # Formatando para o formato desejado: YYYY-MM-DD
                data_formatada = dt.strftime("%Y-%m-%d")

                if center == 'UMBARA':
                    filial = 4
                    tabela_preco = 170
                if center == 'Cascavel':
                    filial = 5
                    tabela_preco = 570
                if center == 'CAMBE':
                    filial = 3
                    tabela_preco = 370
                if center == 'BIGUACU':
                    filial = 6
                    tabela_preco = 670
                    continue

                
                logger.info("Iniciando Validações.")
                # verificar cadastro top system. 
                id_autenticacao = autenticar_usuario_top(filial) # logando na top 

                status, cnpj_data = consultar_cnpj_top(cnpj, id_autenticacao) # consulta na TOP 
                if status == False: # fazer esse retornar o json completo para eu modificar apenas o endereço 
                    continue
                else: 
                    clifor = cnpj_data["codigo"]

                    # realizar busca se não deve ser filial 7
                    with open(rf"{BASE_DIR}/data/client.json", "r", encoding="utf-8") as arquivo:
                        clifor_f7 = json.load(arquivo)

                    # Verifica se o cliente existe
                    for cliente in clifor_f7:
                        if cliente["cliente"] == clifor:
                            filial = 7  # Retorna 'Sim' se o cliente for encontrado
                            tabela_preco = 750
                            id_autenticacao = autenticar_usuario_top(filial) # logando na top 

                    with open(rf"{BASE_DIR}/data/endereco_entrega.json", "r", encoding="utf-8") as arquivo:
                        endereco_json = json.load(arquivo)
                    for i in endereco_json:
                        if i["clifor"] == str(clifor):
                            endereco_entrega = i["id"]
                        else: 
                            endereco_entrega = None

                    # validando tabela preço
                    if payment_method == 'CASH':
                        forma_pagamento = 1
                    
                    if payment_method == 'PIX_AT_DELIVERY':
                        forma_pagamento = 47
                    
                    if payment_method == 'CREDIT_CARD_POS':
                        forma_pagamento = 15
                    
                    if payment_method == 'CHECK': 
                        forma_pagamento = 14

                    condicaoPagamento = 100

                    dados_pedido = {
                        "TopSystemAutorizacao": {
                            "ID": id_autenticacao
                        },
                        "Valores": {
                            "Filial": filial,
                            "CliFor": clifor,
                            "TipoPedido": 58,
                            "Emissao": data_formatada,
                            "Entrega": data_formatada,
                            "FormaPagamento": forma_pagamento,
                            "CondicaoPagamento": condicaoPagamento,
                            "EnderecoEntrega": endereco_entrega,
                            "TotalProduto": 0,
                            "TotalRetorno": 0,
                            "PercDesconto": 0,
                            "ValorDesconto": 0,
                            "PercAcrescimo": 0,
                            "ValorAcrescimo": 0,
                            "ValorFrete": 0,
                            "Total": 0,
                            "Obs": f"Bees {id_bees}",
                            "Funcionario": 2262,
                            "TabelaPreco": tabela_preco,
                            "Pedido": id_bees,
                            "Transportador": 1,
                            "ItemPedidoList": {
                                "Items": []
                            }
                        }
                    }
                    logger.info("Transformando Json")
                    json2, json_itens_bonificado = transformar_json(order, filial) # transformando json de pedidos do Bees para o TOP 
                    bonificado = None

                    for item in json2:
                        dados_pedido["Valores"]["ItemPedidoList"]["Items"].append({
                            "Produto": item["Produto"],
                            "Qtde": item["Qtde"],
                            "Unitario": item["Unitario"],
                            "ValorDesconto": item["ValorDesconto"],
                            "PercDesconto": item["PercDesconto"],
                            "Total": item["Total"]
                        })
                    logger.info("Enviando pedido para Top System")
                    resposta_top, novo_pedido = enviar_json_para_top(dados_pedido, id_bees, filial, bonificado) # passando parametros para que depois possamos atualizar. 
                    logger.info(resposta_top)
                    logger.info("Atualizando GCP")
                    BigQuery2.update_order(novo_pedido) # atualizando GCP 

                    if "Erro" not in resposta_top["result"][0]:
                        logger.info("Atualizando Bees")
                        payload_data = add_order_to_bulk(id_bees, "CONFIRMED", center, placementDate, dia_max)
                        bulk_orders.append(payload_data)
                        logger.info("Status atualizado na lista para Bees : CONFIRMED) ") # inserir placed no Banco de dados. 

                    if json_itens_bonificado: # TODO Arrumar item bonificado 
                        bonificado = "TRUE"
                        id_bees = int(f"77{id_bees}")
                        dados_pedido["Valores"]["TipoPedido"] = 2
                        dados_pedido["Valores"]["FormaPagamento"] = 8
                        dados_pedido["Valores"]["CondicaoPagamento"] = 4
                        dados_pedido["Valores"]["Pedido"] = id_bees
                        for item in json_itens_bonificado:
                            dados_pedido["Valores"]["ItemPedidoList"]["Items"].append({
                                "Produto": item["Produto"],
                                "Qtde": item["Qtde"],
                                "Unitario": item["Unitario"],
                                "ValorDesconto": item["ValorDesconto"],  # TODO passar para o jsone  tirar o outro 
                                "PercDesconto": item["PercDesconto"],
                                "Total": item["Total"]
                            })
                        logger.info("Enviando pedido de bonificacao para Top System")
                        resposta_top, novo_pedido = enviar_json_para_top(dados_pedido, id_bees, filial, bonificado) # passando parametros para que depois possamos atualizar. 
                        logger.info(resposta_top)
                        logger.info("Atualizando GCP")
                        BigQuery2.update_order(novo_pedido) # atualizando GCP 

                        logger.info("Pedidos Atualizados!! ")


        logger.info(f"Bulk de envio: \n {bulk_orders}")
        logger.info("Enviando Bulk para Bees")
        if bulk_orders != []:
            send_bulk_orders(token, bulk_orders)
            logger.info("Enviado com sucesso!")
        
                      
    else:
        logger.info('Erro ao fazer requisição. Status code:', response.status_code)
        logger.info('Detalhes:', response.text)

