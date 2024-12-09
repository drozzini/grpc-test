import os
import time
import logging
import grpc
import helloworld_pb2
import helloworld_pb2_grpc

# Configurar o logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_channel():
    # Configurações de host e porta
    host = os.getenv("GRPC_SERVER_HOST", "localhost")
    port = os.getenv("GRPC_SERVER_PORT", "50051")

    # Controle para habilitar ou desabilitar o keepalive
    enable_keepalive = os.getenv("ENABLE_KEEPALIVE", "false").lower() == "true"

    # Configurações de keepalive obtidas das variáveis de ambiente
    keepalive_time_ms = int(os.getenv("KEEPALIVE_TIME_MS", "60000"))  # Tempo entre pings
    keepalive_timeout_ms = int(os.getenv("KEEPALIVE_TIMEOUT_MS", "20000"))  # Tempo para timeout de ping

    options = []
    if enable_keepalive:
        options.extend([
            ('grpc.keepalive_time_ms', keepalive_time_ms),
            ('grpc.keepalive_timeout_ms', keepalive_timeout_ms),
            ('grpc.http2.max_pings_without_data', 0),
            ('grpc.keepalive_permit_without_calls', 1),
        ])
        logger.info("Keepalive enabled with the following settings:")
        logger.info(f"  KEEPALIVE_TIME_MS={keepalive_time_ms}")
        logger.info(f"  KEEPALIVE_TIMEOUT_MS={keepalive_timeout_ms}")
    else:
        logger.info("Keepalive is disabled.")

    # Criando o canal com ou sem keepalive
    target = f"{host}:{port}"
    channel = grpc.insecure_channel(target, options=options)
    logger.info(f"Channel created for target: {target}")
    return channel

def main():
    # Intervalo entre as requisições
    request_interval = int(os.getenv("REQUEST_INTERVAL", "5"))  # Em segundos

    # Criar o canal e o stub
    channel = create_channel()
    stub = helloworld_pb2_grpc.GreeterStub(channel)

    try:
        # Fazer requisições periódicas
        while True:
            name = os.getenv("REQUEST_NAME", "World")
            logger.info(f"Sending request with name: {name}")
            response = stub.SayHello(helloworld_pb2.HelloRequest(name=name))
            logger.info(f"Received response: {response.message}")
            time.sleep(request_interval)
    except KeyboardInterrupt:
        logger.info("Client interrupted. Shutting down.")
    finally:
        channel.close()
        logger.info("Channel closed.")

if __name__ == '__main__':
    main()
