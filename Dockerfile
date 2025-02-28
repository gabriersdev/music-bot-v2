# Use uma imagem base Python adequada (com a versão que seu projeto precisa)
FROM python:3.12-slim

# Atualizar pacotes e instalar FFmpeg
RUN apt-get update && apt-get install -y ffmpeg && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia os arquivos de requisitos (se houver)
COPY requirements.txt .

# Instala as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código-fonte do projeto
COPY . .

# Comando para executar a aplicação
CMD ["python", "Main.py"]