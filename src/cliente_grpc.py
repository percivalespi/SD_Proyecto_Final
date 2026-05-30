"""
Equipo:
- Duque Malpica Victor Javier
- Espinoza Matamoros Percival Ulises
- Flores Colín Victor Jaziel
- Migueles Martínez Lino Shatinni
Fecha: 02-06-2026
"""

import grpc
import IDL_pb2
import IDL_pb2_grpc

# Clase para el cliente gRPC encargado de la comunicación entre procesos
class ClienteProcesos:
    def __init__(self, num_procesos=5):
        self.num_procesos = num_procesos

    # Obtiene el stub gRPC a partir del ID del proceso destino
    def _obtener_stub(self, id_destino):
        host = f"p{id_destino}"
        # Puerto fijo para todos los procesos, todos los conetedores escuchan en el mismo puerto
        puerto = "50051" 
        # Canal gRPC para la comunicación con los demas procesos.
        channel = grpc.insecure_channel(f"{host}:{puerto}")
        return IDL_pb2_grpc.ProcesoDistribuidoStub(channel)

    # Método para enviar un mensaje a otro proceso
    def enviar(self, id_receptor, contenido, vector, id_emisor):
        stub = self._obtener_stub(id_receptor)
        reloj_msg = IDL_pb2.RelojVectorial(vector=vector)

        # Construcción del mensaje de recepción
        req = IDL_pb2.MensajeRecepcion(
            id_emisor=id_emisor, # ID del proceso
            contenido=contenido, # MSG (JSON con los datos de la transacción)
            reloj_recibido=reloj_msg # Reloj vectorial del emisor
        )
        
        # Envio del proceso emisor al receptor
        try:
            stub.RecibirMensaje(req)
        except Exception as e:
            print(f"Error de red enviando a P{id_receptor}: {e}")

    # Método para el broadcast
    def difundir(self, contenido, vector, id_emisor):
        # Envía el mensaje a todos los procesos excepto a el emisor
        for i in range(1, self.num_procesos + 1):
            if i != id_emisor:
                self.enviar(i, contenido, vector, id_emisor)