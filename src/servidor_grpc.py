import grpc
import IDL_pb2
import IDL_pb2_grpc

class ProcesoServicer(IDL_pb2_grpc.ProcesoDistribuidoServicer):
    def __init__(self, reloj_local, cliente_grpc):
        self.reloj = reloj_local
        self.cliente = cliente_grpc
        # Sumamos 1 porque process_id va de 0 a 4, pero los nombres son P1 a P5
        self.pid = self.reloj.process_id + 1

    def RecibirMensaje(self, request, context):
        # 1. Extraemos el vector del mensaje Protobuf
        vector_recibido = list(request.reloj_recibido.vector)
        
        # 2. Actualizamos el reloj local con la lógica matemática
        vector_actualizado = self.reloj.evento_recepcion(vector_recibido)
        
        # 3. Registramos en la bitácora con el formato exacto
        print(f"[RECEIVE] P{self.pid} <- P{request.id_emisor} msg=\"{request.contenido}\" vector_recibido={vector_recibido} vector_actualizado={vector_actualizado}", flush=True)
        
        return IDL_pb2.Ack(exito=True)

    def EventoInterno(self, request, context):
        vector_actualizado = self.reloj.evento_interno()
        print(f"[INTERNAL] P{self.pid} vector={vector_actualizado}", flush=True)
        return IDL_pb2.Ack(exito=True)

    def EnviarMensaje(self, request, context):
        # Este método es invocado por el trigger.py para ordenarle a este contenedor que envíe
        vector_actualizado = self.reloj.evento_envio()
        
        print(f"[SEND] P{self.pid} -> P{request.id_receptor} msg=\"{request.contenido}\" vector={vector_actualizado}", flush=True)
        
        # Delegamos al cliente para que haga la conexión de red hacia el otro contenedor
        self.cliente.enviar(request.id_receptor, request.contenido, vector_actualizado, self.pid)
        return IDL_pb2.Ack(exito=True)

    def Difusion(self, request, context):
        # Incrementa una sola vez por el evento de broadcast
        vector_actualizado = self.reloj.evento_envio() 
        
        print(f"[BROADCAST] P{self.pid} -> TODOS msg=\"{request.contenido}\" vector={vector_actualizado}", flush=True)
        
        self.cliente.difundir(request.contenido, vector_actualizado, self.pid)
        return IDL_pb2.Ack(exito=True)