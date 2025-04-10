import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from extrators.bigquery import BigQuery
from services.bees_services import add_order_to_bulk, token_bees, send_bulk_orders
from services.top_services import buscar_pedido_por_numero, autenticar_usuario_top, consultar_status_pedidos
from helpers.structlogger import get_logger
from datetime import datetime, timedelta, date

logger = get_logger()

def order_atz():
    token = token_bees()

    # veriricar o status do pedido 
    BigQuery2 = BigQuery()  

    df = BigQuery2.ler_dados()
    logger.info("Pedidos extraídos GCP")

    bulk_orders = []

    for index, order in df.iterrows():
        id_bees = order["id_bees"]
        #if id_bees not in {'9213725511',	'9213795935',	'9213832239',	'9214041557',	'9214125932',	'9214128154',	'9213847053',	'9213727226',	'9213614864',	'9213946836',	'9213739787',	'9213697456',	'9214235264',	'9214206255',	'9214253538',	'9214074035',	'9214308572',	'9214195902',	'9213405719',	'9214435783',	'9214418046',	'9214412163',	'9214396575',	'9214405290',	'9214415632',	'9214398384',	'9214387051',	'9214601108',	'9214503161',	'9214527215',	'9214460749',	'9214505684',	'9214542022',	'9214579091',	'9214602696',	'9214595778',	'9214479120',	'9214460755',	'9214521102',	'9214560852',	'9214581772',	'9211430736',	'9211418316',	'9211710603',	'9211781334',	'9211504090',	'9211994623',	'9212890730',	'9213009920',	'9213632302',	'9214103204',	'9214259643',	'9214264157',	'9214396061',	'9214148958',	'9214260139',	'9214412236',	'9214420103',	'9214505710',	'9214555372',	'9214673378',	'9214673818',	'9214679551',	'9214717587',	'9214733785',	'9214740802',	'9214754914',	'9214756867',	'9214775159',	'9214786566',	'9214811107',	'9214828957',	'9214829487',	'9214833136',	'9214835451',	'9214838464',	'9214882163',	'9214893583',	'9214914576',	'9214921062',	'9214924699',	'9214923312',	'9214947088',	'9214967125',	'9214967966',	'9214985873',	'9215003446',	'9215024695',	'9215044930',	'9215046800',	'9215051827',	'9215101198',	'9215102795',	'9215111044',	'9215116290',	'9215116436',	'9215195573',	'9215213256',	'9215220969',	'9215226264',	'9215233848',	'9215237142',	'9215249529',	'9215251254',	'9215265442',	'9215271610',	'9215277071',	'9215317841',	'9215349866',	'9210776122',	'9211355705',	'9211350992',	'9211444065',	'9213364797',	'9213718929',	'9213820099',	'9213982725',	'9213726121',	'9214020071',	'9213850606',	'9214434337',	'9214677976',	'9215123499',	'9215295259',	'9215282184',	'9215250080',	'9215286635',	'9215522301',	'9215717194',	'9215737174',	'9215673850',	'9215684525',	'9215912051',	'9216008563',	'9216055397',	'9215317414',	'9216017869',	'9214281010',	'9215010358',	'9214351545',	'9215099757',	'9216296437',	'9216317518',	'9216288965',	'9216312980',	'9215239864',	'9215244316',	'9214193333',	'9214074629',	'9216380512',	'9216377333',	'9214738607',	'9214333235',	'9215089690',	'9215089844',	'9214313051',	'9215011746',	'9215036070',	'9214888300',	'9214511978',	'9214654327',	'9214704632',	'9214320254',	'9214538583',	'9214632099',	'9214692570',	'9214501852',	'9214435237',	'9214686023',	'9214844377',	'9214805282',	'9214765007',	'9214882025',	'9214605072',	'9214454878',	'9214375508',	'9214861385',	'9214614811',	'9214752827',	'9214383333',	'9215202855',	'9214492091',	'9214577844',	'9214678110',	'9215063832',	'9214414325',	'9214999394',	'9214954675',	'9214965662',	'9214666391',	'9214194080',	'9214722775',	'9214726587',	'9215211839',	'9214592254',	'9214444380',	'9214813622',	'9214354001',	'9214289292',	'9214923697',	'9214678009',	'9214665868'}:
        #    continue
        id_topsytem = order["id_topsytem"]
        create_date = order["create_date"]
        new_status = order["new_status"]
        center = order["filial"]
        error = order["error"]
        create_date = order["create_date"]
        max_days = order["max_days"]

        center = int(center)

        # Converter create_date para datetime, se necessário
        if isinstance(create_date, str):  # Se for string no formato "YYYY-MM-DD"
            create_date = datetime.strptime(create_date, "%Y-%m-%d")
        elif isinstance(create_date, date):  # Se for datetime.date
            create_date = datetime.combine(create_date, datetime.min.time())

        # Verificar status no TopSystem, se aplicável
        if id_topsytem:
            token_top = autenticar_usuario_top(center)
            try:
                status_pedido, check_box_cancelado = buscar_pedido_por_numero(token_top, id_topsytem) 
                if (status_pedido == 804 or status_pedido == 901) and check_box_cancelado == False:
                    new_status2 = "DELIVERED"

                    dados = {
                        "id_bees": id_bees,
                        "id_topsytem": id_topsytem,
                        "old_status": "CONFIRMED",
                        "new_status" : new_status2,
                        "filial" : center,
                        "error" : None
                    }

                    logger.info("Pegando data")
                    sucesso, resultado = consultar_status_pedidos(token=token_top, pedido_id=id_topsytem)
                    data_entrega = resultado["dataHora"]

                    logger.info("Atualizando Bees")
                    payload_data = add_order_to_bulk(id_bees, new_status2, center, data_entrega)
                    bulk_orders.append(payload_data)
                    logger.info(f"Status enviado para Bees: {new_status2}")

                    logger.info("Atualizando GCP")
                    BigQuery2.update_order(dados)

                if check_box_cancelado == True:  # veriricar tipo do campo que vem se é booleano mesmo

                    new_status2 = "CANCELLED"
                    dados = {
                            "id_bees": id_bees,
                            "id_topsytem": id_topsytem,
                            "old_status": "CONFIRMED",
                            "new_status" : new_status2,   # acabei de arrumar isso aqui, verificar apenas com Will!!!!
                            "filial" : center,
                            "error" : None
                        }

                    logger.info("Atualizando GCP")
                    BigQuery2.update_order(dados)

                    logger.info("Atualizando Bees")
                    payload_data = add_order_to_bulk(id_bees, new_status2, center, datahora=None)
                    bulk_orders.append(payload_data)
                    logger.info(f"Status enviado para Bees: {new_status2}")
            except Exception as e:
                logger.error(f"Erro ao buscar pedido no TopSystem: {e}")
                continue
            
        if new_status == "VERIFY" and create_date + timedelta(days=(max_days+12)) < datetime.now():
            # Atualizar para NEGED sem consultar TopSystem
            new_status2 = "CANCELLED"
            dados = {
                    "id_bees": id_bees,
                    "id_topsytem": id_topsytem,
                    "old_status": "VERIFY",
                    "new_status" : new_status2,
                    "filial" : center,
                    "error" : error
                }
            
            logger.info("Atualizando Bees")
            payload_data = add_order_to_bulk(id_bees, new_status2, center, datahora=None)
            bulk_orders.append(payload_data)
            logger.info(f"Status enviado para Bees: {new_status2}")

            logger.info("Atualizando GCP")
            BigQuery2.update_order(dados)

        else:
            logger.info(f"Pedido que não precisa de atualizacao: {id_bees}")

    if bulk_orders != []:
        send_bulk_orders(token, bulk_orders)
        logger.info(f"Bulk orders enviados com sucesso!: {bulk_orders}")

