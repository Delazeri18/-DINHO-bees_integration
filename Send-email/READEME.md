📬 Bees Email Alert System

Este projeto tem como objetivo enviar alertas por e-mail relacionados a pedidos da integração com a Bees, incluindo:

    ⚠️ Alertas de pedidos que serão cancelados no dia

    🔄 Acompanhamento de status dos pedidos

    ❗ Relatórios de erros encontrados

A aplicação é executada dentro de um container Docker, facilitando o deploy e a execução em ambientes diversos.
🚀 Como executar

A forma mais simples de rodar o sistema é utilizando o seguinte comando Docker:

docker run -it --rm bees_email_image

Esse comando irá:

    Inicializar a aplicação

    Processar os dados dos pedidos

    Enviar e-mails com os alertas necessários

    Gerar relatórios de erro (caso existam)

🛠️ Funcionalidades

    📅 Verifica e envia alertas sobre pedidos que serão cancelados no dia

    📦 Monitora e acompanha o status atual dos pedidos

    🧾 Gera e envia relatórios de falhas ou inconsistências detectadas

    📤 Envio de e-mails automatizado com base nos dados processados
🧪 Requisitos

Nenhuma instalação adicional é necessária além do Docker.

Certifique-se apenas de ter:

    Docker instalado e em funcionamento

    Permissões para executar containers

📬 Contato

Se tiver dúvidas ou sugestões, sinta-se à vontade para abrir uma issue ou me chamar!
E-mail: kewindelazeri7@gmail.com
