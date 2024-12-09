# Use a imagem base oficial do Python
FROM python:3.9-slim

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copie o arquivo requirements.txt para o diretório de trabalho
COPY requirements.txt .

# Instale as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie apenas os arquivos necessários para o diretório de trabalho
COPY helloworld.proto .
COPY server.py .

# Gere os arquivos pb2 a partir dos arquivos .proto
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. helloworld.proto

# Exponha a porta que o servidor gRPC usará
EXPOSE 50051

# Comando para executar o servidor gRPC
CMD ["python", "server.py"]
