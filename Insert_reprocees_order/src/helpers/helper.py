import re 
import json
import os 
import requests
from datetime import datetime
from pathlib import Path
from difflib import get_close_matches
from services.top_services import *
import logging
from pathlib import Path

BASE_DIR = Path(os.getenv("PYTHONPATH", "/app/src")).resolve()

def formatar_cnpj(cnpj):
    # Remove qualquer caractere que não seja número
    cnpj = str(cnpj)
    cnpj = re.sub(r'\D', '', cnpj)
    # Aplica a formatação padrão
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"

def buscar_codigo_por_cnpj(cnpj_procurado):
    with open('clientes.json', 'r', encoding='utf-8') as file:
        lista = json.load(file)  # Carrega o JSON em uma lista de dicionários
    for item in lista:
        if item["cnpj"] == cnpj_procurado:
            return item["codigo"]
    return None

def transformar_json(order, filial):
    json2 = []  # Lista principal para o JSON transformado
    json_alternativo = []  # Lista para itens de bonificação (caso a filial não seja 6)

    for item in order["items"]:
        produto = int(item["dynamicAttributes"]["sku"])
        qtde = item["quantity"]
        unitario = item["summaryItem"]["price"]
        valor_desconto = item["summaryItem"].get("discount", 0)


        with open(rf"{BASE_DIR}/data/produtos.json", "r", encoding="utf-8") as arquivo:
            produtos_data = json.load(arquivo)

        if str(produto) in produtos_data:
            qtd_top = produtos_data[str(produto)]["qtd_top"]

            if unitario == 0: #TODO mapear base_price 

                uom_list = item.get("uom", [])
                if uom_list:
                    base_price = next((u["basePrice"] for u in uom_list if u.get("type") == "PACK"), None)
                else:
                    base_price = item.get("summaryItem", {}).get("basePrice")

                if filial == 6:
                    json_alternativo == None
                    # Para filial 6: adicionar no JSON principal com TipoPedido = 58 
                    valor_top = ((base_price * qtde) /  (qtd_top * qtde))
                    
                    valor_top = round(valor_top, 2)
                    qtd_final = qtd_top * qtde

                    total = valor_top * qtd_top
                    total = round(total, 2)  #  TODO ALTERAR AQUI!
                    
                    json2.append({
                        "Produto": produto,
                        "Qtde": qtd_final, 
                        "Unitario": valor_top,
                        "ValorDesconto": 0,
                        "PercDesconto": 0,
                        "Total": total,
                        "TipoPedido": 79
                    })

                else:
                    # Para outras filiais: alocar no JSON alternativo  
                    valor_top = ((base_price * qtde) /  (qtd_top * qtde))
                    valor_top = round(valor_top, 2)
                    qtd_final = qtd_top * qtde

                    total = valor_top * qtd_top
                    total = round(total, 2)  #  TODO ALTERAR AQUI!

                    json_alternativo.append({
                        "Produto": produto,
                        "Qtde": qtd_final ,
                        "Unitario": valor_top,
                        "ValorDesconto": 0,
                        "PercDesconto": 0,
                        "Total": total,
                        "TipoPedido": None
                    })
            else:
                # Para filial 6: adicionar no JSON principal com TipoPedido = 58 
                valor_top = ((unitario * qtde) /  (qtd_top * qtde))
                
                valor_top = round(valor_top, 2)
                qtd_final = qtd_top * qtde

                total = valor_top * qtd_top
                total = round(total, 2)  #  TODO ALTERAR AQUI!

                json2.append({
                    "Produto": produto,
                    "Qtde": qtd_final,
                    "Unitario": valor_top,
                    "ValorDesconto": 0,
                    "PercDesconto": 0,
                    "Total": total,
                    "TipoPedido": None
                })

        else: 
            """ PODE SER USADO DEPOIS
            # Tratando itens do tipo FREEGOOD
            if item["type"] == "FREEGOOD": #TODO mapear base_price 
                if filial == 6:
                    json_alternativo == None
                    # Para filial 6: adicionar no JSON principal com TipoPedido = 58
                    0 = 0 # 100% de desconto para itens promocionais
                    total = 0.0  
                    json2.append({
                        "Produto": produto,
                        "Qtde": qtde,
                        "Unitario": base_price,
                        "ValorDesconto": 0,
                        "PercDesconto": 0,
                        "Total": total,
                        "TipoPedido": 79
                    })
            """
            if unitario == 0: #TODO mapear base_price 

                uom_list = item.get("uom", [])
                if uom_list:
                    base_price = next((u["basePrice"] for u in uom_list if u.get("type") == "PACK"), None)
                else:
                    base_price = item.get("summaryItem", {}).get("basePrice")

                if filial == 6:
                    json_alternativo == None
                    total = qtde * base_price
                    # Para filial 6: adicionar no JSON principal com TipoPedido = 58
                    json2.append({
                        "Produto": produto,
                        "Qtde": qtde,
                        "Unitario": base_price,
                        "ValorDesconto": 0,
                        "PercDesconto": 0,
                        "Total": total,
                        "TipoPedido": 79
                    })

                else:
                    # Para outras filiais: alocar no JSON alternativo
                    total = qtde * base_price 
                    json_alternativo.append({
                        "Produto": produto,
                        "Qtde": qtde,
                        "Unitario": base_price,
                        "ValorDesconto": 0,
                        "PercDesconto": 0,
                        "Total": total,
                        "TipoPedido": None
                    })
            else:
                total = (unitario * qtde)
                total = round(total, 2)
                json2.append({
                    "Produto": produto,
                    "Qtde": qtde,
                    "Unitario": unitario,
                    "ValorDesconto": 0,
                    "PercDesconto": 0,
                    "Total": total,
                    "TipoPedido": None
                })

    return json2, json_alternativo

def carregar_json(caminho_arquivo):
    """Carrega um JSON a partir do arquivo na pasta data."""
    caminho = Path(caminho_arquivo)
    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)

def buscar_codigo_bairro(bairro_receita, bairros_json):
    """
    Busca o código do bairro correspondente no JSON usando correspondência aproximada.
    """
    if not bairro_receita:
        return None  # Retorna None se o nome do bairro for vazio ou inválido

    # Lista de nomes de bairros no JSON
    nomes_bairros = [bairro["nome"] for bairro in bairros_json]

    # Procurar a melhor correspondência
    correspondencias = get_close_matches(bairro_receita.lower(), [nome.lower() for nome in nomes_bairros], n=1, cutoff=0.7)
    
    if correspondencias:
        # Se encontrar correspondência, retorna o código do bairro correspondente
        nome_correspondente = correspondencias[0]
        for bairro in bairros_json:
            if bairro["nome"].lower() == nome_correspondente:
                return bairro["codigo"]
    
    return None  # Retorna None caso nenhuma correspondência seja encontrada

def buscar_codigo_cidade(cod_fiscal, cidades_json):
    """
    Busca o código da cidade baseado no código fiscal no JSON de cidades.
    """
    for cidade in cidades_json:
        if cidade["codigofiscal"] == str(cod_fiscal):
            return cidade["codigo"]
    return None  # Retorna None caso nenhuma correspondência seja encontrada

def buscar_uf(uf, uf_json):
    for estado in uf_json:
        if estado["uf"] == str(uf):
            return estado["codigo"]
# TODO COLOCAR LATITUDE E LONG AQUI 
def update_adrees(cnpj_data, address):
    """
    Atualiza os campos do JSON de CNPJ com base nos dados do endereço fornecido.
    """
    # Carregar os JSONs necessários
    bairros_json = carregar_json("data/bairro_json.json")
    cidades_json = carregar_json("data/city_json.json")
    uf_json = carregar_json("data/uf_json.json")
    
    # Atualizando os campos no JSON
    cnpj_data["endereco"] = address.get("street")
    cnpj_data["numero"] = address.get("number")
    cnpj_data["latitude"] = address.get("latitude")
    cnpj_data["longitude"] = address.get("longitude")

    
    # Busca e validação do bairro
    bairro_receita = address.get("district")
    codigo_bairro = buscar_codigo_bairro(bairro_receita, bairros_json)
    cnpj_data["bairro"] = codigo_bairro if codigo_bairro else bairro_receita
    
    # Busca e validação da cidade
    municipality_fiscal = address.get("municipality")
    codigo_cidade = buscar_codigo_cidade(municipality_fiscal, cidades_json)
    cnpj_data["cidade"] = codigo_cidade if codigo_cidade else municipality_fiscal
       

    estado = address.get("state")  # UF
    codigo_uf = buscar_uf(estado, uf_json)
    cnpj_data["estado"] = codigo_uf


    cnpj_data["cep"] = address.get("zip")
    
    # Adicionando a data de hoje no campo obs
    data_atual = datetime.now().strftime("%Y-%m-%d")
    cnpj_data["infComercial"] = f"{data_atual}"
    
    # Retornando o JSON atualizado
    return cnpj_data

def buscar_endereco(clifor, endereco_json):
    for i in endereco_json:
        if i["clifor"] == str(clifor):
            return i["id"]
        
def salvar_historico(bulk_orders):
    """Salva pedidos em um arquivo JSON para histórico"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"historico_pedidos_{timestamp}.json"
    backup_dir = f"{BASE_DIR}/control_bulk"
    filename = os.path.join(backup_dir, f"bulk_orders_{timestamp}.json")
    print(bulk_orders)
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(bulk_orders, f, indent=4, ensure_ascii=False)
        print(f"Backup salvo: {filename}")
    except Exception as e:
        print(f"Erro ao salvar backup: {e}")