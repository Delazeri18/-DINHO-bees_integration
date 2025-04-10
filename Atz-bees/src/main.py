from handlers.handler_atz import order_atz

if __name__ == "__main__":
    print("Executando o arquivo principal: main_atz.py")
    try:
        order_atz()  # Chama a função do handler
    except Exception as e:
        print(f"Erro durante a execução de order_atz: {e}")
    print("Finalizado execução: main_atz.py")