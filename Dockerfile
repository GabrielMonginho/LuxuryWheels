# Use a imagem base oficial do Python 3.11
FROM python:3.11.4-slim

# Define o diretório de trabalho no contêiner
WORKDIR /app

# Copia os arquivos do projeto para o contêiner
COPY . /app

# Instala as dependências do projeto
RUN pip install -r requirements.txt

# Comando para executar a aplicação
CMD ["gunicorn", "-b", ":8080", "app:app"]
steps:
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', 'gcr.io/$PROJECT_ID/luxurywheels', '.']
images:
- 'gcr.io/$PROJECT_ID/luxurywheels'
