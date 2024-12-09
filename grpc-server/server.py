import os
import logging
from concurrent import futures
import grpc
import helloworld_pb2
import helloworld_pb2_grpc
from grpc_reflection.v1alpha import reflection

# Configurar o logging para stdout
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        pod_name = os.getenv("HOSTNAME", "unknown-pod")
        response_message = f"Hello, {request.name} from {pod_name}!"
        logger.info(f"Responding with: {response_message}")
        return helloworld_pb2.HelloReply(message=response_message)

def serve():
    # Porta obtida das variáveis de ambiente
    port = os.getenv("GRPC_PORT", "50051")

    # Controle para habilitar ou não o keepalive
    enable_keepalive = os.getenv("ENABLE_KEEPALIVE", "false").lower() == "true"

    # Configurações de keepalive obtidas das variáveis de ambiente
    keepalive_time_ms = int(os.getenv("KEEPALIVE_TIME_MS", "60000"))  # Tempo entre pings
    keepalive_timeout_ms = int(os.getenv("KEEPALIVE_TIMEOUT_MS", "20000"))  # Tempo para timeout de ping
    max_connection_idle_ms = int(os.getenv("MAX_CONNECTION_IDLE_MS", "120000"))  # Tempo de ociosidade
    max_connection_age_ms = int(os.getenv("MAX_CONNECTION_AGE_MS", "300000"))  # Tempo máximo de conexão antes de reinício
    max_connection_age_grace_ms = int(os.getenv("MAX_CONNECTION_AGE_GRACE_MS", "10000"))  # Tempo de graça após o limite

    # Configurações de keepalive, caso habilitado
    options = []
    if enable_keepalive:
        options.extend([
            ('grpc.keepalive_time_ms', keepalive_time_ms),
            ('grpc.keepalive_timeout_ms', keepalive_timeout_ms),
            ('grpc.http2.max_pings_without_data', 0),
            ('grpc.keepalive_permit_without_calls', 1),
            ('grpc.max_connection_idle_ms', max_connection_idle_ms),
            ('grpc.max_connection_age_ms', max_connection_age_ms),
            ('grpc.max_connection_age_grace_ms', max_connection_age_grace_ms),
        ])
        logger.info("Keepalive enabled with the following settings:")
        logger.info(f"  KEEPALIVE_TIME_MS={keepalive_time_ms}")
        logger.info(f"  KEEPALIVE_TIMEOUT_MS={keepalive_timeout_ms}")
        logger.info(f"  MAX_CONNECTION_IDLE_MS={max_connection_idle_ms}")
        logger.info(f"  MAX_CONNECTION_AGE_MS={max_connection_age_ms}")
        logger.info(f"  MAX_CONNECTION_AGE_GRACE_MS={max_connection_age_grace_ms}")
    else:
        logger.info("Keepalive is disabled.")

    # Criando o servidor gRPC com ou sem keepalive
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), options=options)
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)

    # Ativando reflexão
    SERVICE_NAMES = (
        helloworld_pb2.DESCRIPTOR.services_by_name['Greeter'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)

    # Bind no endereço com a porta especificada
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    logger.info(f"Server started on port {port}")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
