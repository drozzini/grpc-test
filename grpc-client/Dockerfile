FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY helloworld.proto .
COPY client.py .

# Gere o código protobuf
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. helloworld.proto

CMD ["python", "client.py"]
