"""
Equipo:
- Duque Malpica Victor Javier
- Espinoza Matamoros Percival Ulises
- Flores Colín Victor Jaziel
- Migueles Martínez Lino Shatini
Fecha: 02-06-2026
"""

import os
import time
import grpc
from concurrent import futures
import IDL_pb2_grpc
from reloj import RelojVectorial
from servidor_grpc import ProcesoServicer
from cliente_grpc import ClienteProcesos

# Función principal para iniciar el servidor gRPC
def serve():
    # Obtener el ID del proceso desde la variable de entorno
    process_id_str = os.environ.get("PROCESS_ID", "1")
    try:
        process_id_int = int(process_id_str)
    except ValueError:
        process_id_int = 1

    indice_proceso = process_id_int - 1

    # Inicializacion del reloj vectorial y el cliente gRPC
    reloj_local = RelojVectorial(indice_proceso, num_procesos=5)
    cliente_grpc = ClienteProcesos(num_procesos=5)
    
    # Configuración e inicio del servidor gRPC
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = ProcesoServicer(reloj_local, cliente_grpc)

    IDL_pb2_grpc.add_ProcesoDistribuidoServicer_to_server(servicer, server)

    # Puerto fijo para todos los procesos  
    puerto = "50051"
    server.add_insecure_port(f"[::]:{puerto}")
    server.start()
    
    print(f"Servidor P{process_id_int} iniciado y escuchando en el puerto {puerto}...", flush=True)
    
    # Esperando conexiones o eventos
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()