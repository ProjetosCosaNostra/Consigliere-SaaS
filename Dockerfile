# Usa uma versão ESTÁVEL do Python (Baseada no Debian Bullseye)
# Isso evita o erro de "Unable to locate package"
FROM python:3.10-slim-bullseye

# Define diretório de trabalho
WORKDIR /app

# Instala apenas o essencial (git, curl e compiladores)
# Removemos 'software-properties-common' que estava quebrando
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos do projeto
COPY . .

# Atualiza o pip e instala as dependências
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expõe a porta do Streamlit
EXPOSE 8501

# Checagem de saúde
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Comando de Início
ENTRYPOINT ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]