import grpc
import IDL_pb2
import IDL_pb2_grpc

class ClienteProcesos:
    def __init__(self, num_procesos=5):
        self.num_procesos = num_procesos

    def _obtener_stub(self, id_destino):
        host = f"p{id_destino}"
        puerto = "50051"
        channel = grpc.insecure_channel(f"{host}:{puerto}")
        return IDL_pb2_grpc.ProcesoDistribuidoStub(channel)

    def enviar(self, id_receptor, contenido, vector, id_emisor):
        stub = self._obtener_stub(id_receptor)
        
        # Empaquetamos el vector en la estructura de Protobuf
        reloj_msg = IDL_pb2.RelojVectorial(vector=vector)
        req = IDL_pb2.MensajeRecepcion(
            id_emisor=id_emisor, 
            contenido=contenido, 
            reloj_recibido=reloj_msg
        )
        
        try:
            # Llamamos al endpoint del servidor destino
            stub.RecibirMensaje(req)
        except Exception as e:
            print(f"Error de red enviando a P{id_receptor}: {e}")

    def difundir(self, contenido, vector, id_emisor):
        # Itera y envía a todos los procesos menos a sí mismo
        for i in range(1, self.num_procesos + 1):
            if i != id_emisor:
                self.enviar(i, contenido, vector, id_emisor)