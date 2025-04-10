from handlers.handler_insert import insert_order, reprocess_order
from extrators.loaders import update_data


if __name__ == "__main__":
    try:
        update_data()
    except Exception as e:
        print("Erro durante a execução do update_data", error=str(e))

    print("Executando o arquivo principal: main_insert.py")
    try:
        insert_order()
    except Exception as e:
        print("Erro durante a execução de insert_order", error=str(e))
    print("Finalizado execução: main_insert.py")

    print("Executando o arquivo principal: reprocess_order.py")
    try:
        reprocess_order()
    except Exception as e:
        print("Erro durante a execução de reprocess_order", error=str(e))
    print("Finalizado execução: reprocess_order.py")
