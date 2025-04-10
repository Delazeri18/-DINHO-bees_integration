import requests # type: ignore
import json

def autenticar_usuario_top(filial):
    # Dados de autenticação

   
    produção_autenticação = ''
    testes_autenticação = ''

    dados_autenticacao = {
        'Usuario': ,
        'Filial': ,
        'Senha' : ''
    }
    
    headers = {'Content-Type': 'application/json'}

    try:
        # Envia a requisição para autenticação
        response = requests.post(produção_autenticação, headers=headers, json=dados_autenticacao)
        response.raise_for_status()  # Levanta um erro para status 4xx ou 5xx
        
        # Imprime a resposta completa para análise
        print("Resposta da API:", response.text)

        if response.status_code == 200:
            # Tenta converter a resposta para JSON
            auth_data = response.json()

            # Verifica a estrutura da resposta antes de tentar acessar 'Retorno'
            if 'result' in auth_data and len(auth_data['result']) > 0:
                if 'Retorno' in auth_data['result'][0]:
                    id_autenticacao = auth_data['result'][0]['Retorno']['ID']
                    print(f"Autenticação bem-sucedida. ID: {id_autenticacao}")
                    return id_autenticacao
                else:
                    print("A chave 'Retorno' não foi encontrada na resposta.")
            else:
                print("A chave 'result' não está no formato esperado.")
        else:
            print(f"Erro na autenticação: {response.status_code}, {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")

def enviar_json_para_top(json_pedido, id_bees,filial, bonificado):

    testes_pedido = ''
    produção_pedido = ''

    url_pedido = produção_pedido

    # Cabeçalhos da requisição
    headers2 = {'Content-Type': 'application/json'}

    try:
        # Realiza a requisição para inserir o pedido
        response = requests.post(url_pedido, headers=headers2, json=json_pedido)
        response.raise_for_status()  # Levanta um erro para status 4xx ou 5xx

        # Verifica se o pedido foi inserido com sucesso
        if response.status_code == 200:
            # Retorna o objeto inserido
            resposta_data = response.json()
            print("Enviando")
            
            if "Erro" not in resposta_data["result"][0]:
                # Pedido enviado com sucesso, ajustar no json
                id_topsystem = resposta_data.get("result", [{}])[0].get("Retorno", {}).get("ID", None)
                novo_pedido = {
                    "id_bees": id_bees,
                    "old_status": "PLACED",
                    "id_topsytem": id_topsystem,
                    "new_status" : "CONFIRMED",
                    "filial" : filial,
                    "error" : None,
                    "bonificado": bonificado
                }
                print("Pedido enviado com sucesso:", json.dumps(resposta_data, indent=4))

            # condicinal caso der erro 
            if "Erro" in resposta_data["result"][0]:

                error_value = resposta_data["result"][0].get("Erro", "")
                error_value = error_value.replace('"', '\\"').replace("'", "\\'") 
                error_value = error_value.replace('\n', ' ').replace('\r', '')
                                                                    
                # Pedido enviado com sucesso, ajustar no json
                novo_pedido = {
                    "id_bees": id_bees,
                    "old_status": "PLACED",
                    "new_status" : "VERIFY",
                    "filial" : filial,
                    "id_topsystem": None,
                    "error" : error_value,
                    "bonificado": bonificado
                }



            return resposta_data, novo_pedido
        else:
            print(f"Erro ao enviar pedido: {response.status_code} - {response.text}")

            error_value = resposta_data["result"][0].get("Erro", "")
            error_value = error_value.replace('"', '\\"').replace("'", "\\'")
            error_value = error_value.replace('\n', ' ').replace('\r', '')

            novo_pedido = {
                    "id_bees": id_bees,
                    "old_status": "PLACED",
                    "new_status" : "VERIFY",
                    "filial" : filial,
                    "id_topsystem": None,
                    "error" : error_value,
                    "bonificado": bonificado
                }
            return novo_pedido

    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        novo_pedido = {
            "id_bees": id_bees,
            "old_status": "PLACED",
            "new_status" : "VERIFY",
            "filial" : filial,
            "id_topsystem": None,
            "error" : e,
            "bonificado": bonificado
        }

        return novo_pedido
      
def buscar_pedido_por_numero(id_autenticacao, id_topsytem):
    url_pedido = ''
    
    # Definindo o corpo da requisição
    dados_pedido = {
        "TopSystemAutorizacao": {
            "ID": id_autenticacao
        },
        "Valores": {
            "ID": f"{id_topsytem}"
        }
    }

    headers = {'Content-Type': 'application/json'}

    # Realiza a requisição POST
    response = requests.post(url_pedido, headers=headers, json=dados_pedido)

    # Verifica se a requisição foi bem-sucedida
    if response.status_code == 200:
        # Retorna o objeto do pedido
        pedido_inserido = response.json()
        print("Pedido consultado com sucesso:", json.dumps(pedido_inserido, indent=4))
        
        # Extrair o status do pedido
        try:
            status = pedido_inserido["result"][0]["Retorno"]["Status"]
            check_box_cancelado = pedido_inserido["result"][0]["Retorno"]["Cancelado"]
            print(f"Tipo de 'Cancelado': {type(check_box_cancelado)}")
            return status, check_box_cancelado
        except (KeyError, IndexError) as e:
            print("Erro ao extrair o status:", e)
            return None

    else:
        print("Erro ao consultar pedido:", response.status_code, response.text)
        return None

def consultar_cnpj_top(cnpj, token):
    url = f""
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print(response.json())
            return True, response.json()
        elif response.status_code == 401:
            print({"error": "Unauthorized - Verifique seu token ou permissões."})
            return False
        else:
            print({"error": f"Erro inesperado ou cliente nn encontrado : {response.status_code}", "detalhes": response.text})
            return False

    except requests.RequestException as e:
        return {"error": "Erro ao fazer a requisição", "detalhes": str(e)}

def update_cliente(token, cnpj_data):

    codigo = cnpj_data["codigo"]


    url = f""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    # Mapeando os campos
    cidade = cnpj_data["cidade"]
    infComercial = cnpj_data["infComercial"]
    codigo_uf = cnpj_data["estado"]
    endereco = cnpj_data["endereco"]
    numero = cnpj_data["numero"]
    bairro = cnpj_data["bairro"]
    cep = cnpj_data["cep"]
    latitude = cnpj_data["latitude"]
    longitude = cnpj_data["longitude"]

    # Criando o payload com todos os campos
    payload = [
        {
            "operationType": 0,
            "path": "/infComercial",
            "op": "replace",
            "from": None,
            "value": infComercial
        },
        {
            "operationType": 0,
            "path": "/estado",
            "op": "replace",
            "from": None,
            "value": codigo_uf
        },
        {
            "operationType": 0,
            "path": "/endereco",
            "op": "replace",
            "from": None,
            "value": endereco
        },
        {
            "operationType": 0,
            "path": "/numero",
            "op": "replace",
            "from": None,
            "value": numero
        },
        {
            "operationType": 0,
            "path": "/bairro",
            "op": "replace",
            "from": None,
            "value": bairro
        },
        {
            "operationType": 0,
            "path": "/cep",
            "op": "replace",
            "from": None,
            "value": cep
        },
        {
            "operationType": 0,
            "path": "/cidade",
            "op": "replace",
            "from": None,
            "value": cidade
        },
        {
            "operationType": 0,
            "path": "/infComercial",
            "op": "replace",
            "from": None,
            "value": infComercial
        },
        {
            "operationType": 0,
            "path": "/latitude",
            "op": "replace",
            "from": None,
            "value": latitude
        },
        {
            "operationType": 0,
            "path": "/longitude",
            "op": "replace",
            "from": None,
            "value": longitude
        }
    
    ]

    # Enviando a requisição PATCH
    response = requests.patch(url, json=payload, headers=headers)

    # Tratamento da resposta
    if response.status_code == 200:
        print("Atualização bem-sucedida:", response.json())
    else:
        print("Erro:", response.status_code, response.text)
