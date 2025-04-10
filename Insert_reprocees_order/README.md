🔄 Integração Bees → Top System

Este projeto tem como objetivo inserir pedidos originados da Bees na plataforma Top System, aplicando regras de negócio específicas e garantindo a integridade dos dados por meio de validações externas.
🚀 Execução

A aplicação é executada via Docker com o seguinte comando:

docker run --rm insert_bees_image

⚙️ O que o sistema faz

    🔍 Aplica regras de negócio sobre os dados dos pedidos recebidos da Bees

    ✅ Valida CNPJs via integração com o CNPJÁ (https://www.cnpja.com.br/)

    📝 Gera logs de erros para pedidos inválidos ou com inconsistências

    📤 Envia dados de clientes não cadastrados no Top System

    🔁 Reprocessa pedidos com erros, de forma controlada

    🔗 Realiza a inserção direta no sistema Top System, respeitando os formatos e validações exigidos

🧪 Requisitos

    Docker instalado

    Acesso ao serviço CNPJÁ (com chave de API se necessário)

    Permissão de acesso ao Top System para realizar a inserção de dados

    Acesso ao GCP Big Query

📬 Contato

Fique à vontade para abrir uma issue ou entrar em contato para sugestões, melhorias ou dúvidas sobre o uso do projeto!
E-mail: Kewindelazeri7@gmail.com
