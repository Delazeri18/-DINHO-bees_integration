# Usa uma imagem base leve
FROM python:3.10-slim

# Define variáveis de ambiente para otimizar a execução e o cache do pip
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore \
    PYTHONPATH=/app/src

# Define o diretório de trabalho
WORKDIR /app

# Copia somente o arquivo de requisitos para aproveitar o cache na instalação das dependências
COPY src/requirements.txt ./

# Atualiza os pacotes, instala dependências do sistema (se necessário), 
# atualiza o pip e instala as dependências Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copia o restante dos arquivos da aplicação
COPY src /app/src

# Comando para rodar a aplicação
CMD ["python", "src/main.py"]