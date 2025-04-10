Projeto Bees 🐝

O Projeto Bees é composto por um conjunto de aplicações que integram e sincronizam dados entre diferentes sistemas, tais como a plataforma Bees, o ERP Top System e o serviço de validação de CNPJs. O projeto possui três módulos principais:

    📬 Bees Email Alert System: Gerencia o envio de alertas e e-mails relacionados aos pedidos.

    🔄 Atualização de Status no Sistema Bees: Atualiza os status dos pedidos no sistema Bees por meio de consultas ao ERP Top System utilizando BigQuery.

    🔗 Integração Bees → Top System (Insert e Reprocess): Responsável pela inserção de pedidos da Bees na plataforma Top System, com validação de dados e reprocessamento de pedidos com inconsistências.

Cada módulo é empacotado em containers Docker, facilitando a implantação e execução em diversos ambientes.
Estrutura do Projeto 📁

A organização do projeto segue a separação de responsabilidades por pasta/serviço:

    /email
    Contém o código e os scripts para o Bees Email Alert System, responsável por:

        📧 Envio de alertas por e-mail para pedidos que serão cancelados no dia.

        📊 Acompanhamento do status dos pedidos.

        🚨 Geração de relatórios de erros e falhas.

    /atualizacao
    Abriga a aplicação de Atualização de Status no Sistema Bees, que:

        🔍 Consulta e atualiza os status dos pedidos com base em dados fornecidos pelo ERP Top System.

        ☁️ Utiliza o BigQuery para buscas e armazenamento intermediário de dados.

        📄 Integra com planilhas (Sheets) contendo regras e informações da equipe comercial.

    /insert_reprocess
    Contém o código para a Integração Bees → Top System, cuja finalidade é:

        ➕ Inserir os pedidos oriundos da Bees na plataforma Top System.

        📜 Aplicar regras de negócio específicas e validações externas, como a verificação de CNPJs via CNPJÁ.

        📑 Gerar logs de erros para pedidos inconsistentes.

        🔄 Realizar reprocessamento controlado de pedidos com falhas.

        👥 Enviar dados de clientes não cadastrados no Top System.

Contato

Se tiver dúvidas, sugestões ou precisar de mais informações, entre em contato:

✉️ E-mail: kewindelazeri7@gmail.com
