Atualização de Status no Sistema Bees

Este projeto tem como objetivo atualizar os status no sistema Bees, realizando consultas no sistema Top System (ERP). A comunicação entre os sistemas é realizada utilizando o BigQuery, que atua como intermediador para buscas, armazenamento de informações e integração ao sheets, onde é preenchidos informações de regras da equipe comercial.
Funcionalidades

    Atualização de Status: Consulta e atualiza os status no sistema Bees com base nos dados do ERP.

    Integração com BigQuery: Utiliza o BigQuery para realizar buscas e armazenar informações.

    Execução via Docker: Facilita o deploy e execução do projeto por meio de container.

Pré-requisitos

    Docker: O projeto é empacotado em uma imagem Docker, portanto é necessário ter o Docker instalado para executá-lo.

    Acesso ao BigQuery: Certifique-se de ter as credenciais e permissões necessárias para acessar o BigQuery.

    Acesso ao Sistema Top System (ERP): O projeto consulta dados no ERP, sendo necessário que as configurações de acesso estejam corretamente definidas.

Instalação

    Clone o repositório:

git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio

(Opcional) Configure as variáveis de ambiente ou arquivos de configuração necessários para acessar o BigQuery e o ERP. (Verifique se há instruções específicas para as credenciais.)

Construa a imagem Docker (caso ainda não esteja construída):

    docker build -t atz_bees_image .

Como Executar

Para rodar o projeto, utilize o comando abaixo:

docker run -it --rm atz_bees_image

Este comando iniciará o container, executando o script responsável pela atualização dos status.
