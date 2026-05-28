import os
import time
import grpc
from concurrent import futures
import IDL_pb2_grpc
from reloj import RelojVectorial
from servidor_grpc import ProcesoServicer
from cliente_grpc import ClienteProcesos

def serve():
    # Obtenemos el ID del proceso desde Docker (1 a 5)
    process_id_str = os.environ.get("PROCESS_ID", "1")
    try:
        process_id_int = int(process_id_str)
    except ValueError:
        process_id_int = 1

    # El índice interno del vector va de 0 a 4
    indice_proceso = process_id_int - 1

    # Instanciamos la memoria del vector y el cliente de red
    reloj_local = RelojVectorial(indice_proceso, num_procesos=5)
    cliente_grpc = ClienteProcesos(num_procesos=5)
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = ProcesoServicer(reloj_local, cliente_grpc)
    
    IDL_pb2_grpc.add_ProcesoDistribuidoServicer_to_server(servicer, server)
    
    
    puerto = "50051"
    server.add_insecure_port(f"[::]:{puerto}")
    server.start()
    
    print(f"Servidor P{process_id_int} iniciado y escuchando en el puerto {puerto}...", flush=True)
    
    try:
        # Mantenemos el contenedor vivo esperando conexiones o eventos
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()