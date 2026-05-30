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

# Clase que implementa el servicio gRPC definido en el archivo .proto
class ProcesoServicer(IDL_pb2_grpc.ProcesoDistribuidoServicer):
    def __init__(self, reloj_local, cliente_grpc):
        self.reloj = reloj_local
        self.cliente = cliente_grpc
        # Para que coincida con el número de procesos del diagrama, se incrementa en 1 (P1, P2, P3, P4, P5)
        self.pid = self.reloj.process_id + 1

    # Metodo para el servicio de recepción de mensajes.
    def RecibirMensaje(self, request, context):
        # Recuperación y actualización del reloj vectorial
        vector_recibido = list(request.reloj_recibido.vector)
        vector_actualizado = self.reloj.evento_recepcion(vector_recibido)

        # Registro en la bitscora        
        print(f"[RECEIVE] P{self.pid} <- P{request.id_emisor} msg=\"{request.contenido}\" vector_recibido={vector_recibido} vector_actualizado={vector_actualizado}", flush=True)
        
        # Retorna un ACK al emisor
        return IDL_pb2.Ack(exito=True)

    # Método para la simulación de eventos internos
    def EventoInterno(self, request, context):
        # Incremento del reloj vecotorial
        vector_actualizado = self.reloj.evento_interno()
        # Registro en la bitscora
        print(f"[INTERNAL] P{self.pid} vector={vector_actualizado}", flush=True)
        return IDL_pb2.Ack(exito=True)
    
    # Método para el servicio de envío de mensajes
    def EnviarMensaje(self, request, context):
        # Incrementa el reloj vectorial del emisor
        vector_actualizado = self.reloj.evento_envio()
        
        # Registro en la bitacora
        print(f"[SEND] P{self.pid} -> P{request.id_receptor} msg=\"{request.contenido}\" vector={vector_actualizado}", flush=True)
        
        # Envía el mensaje del mensaje al receptor
        self.cliente.enviar(request.id_receptor, request.contenido, vector_actualizado, self.pid)
        return IDL_pb2.Ack(exito=True)
    

    def Difusion(self, request, context):
        # Incrementa el reloj vectorial del emisor
        vector_actualizado = self.reloj.evento_envio() 
        
        # Registro en la bitacora
        print(f"[BROADCAST] P{self.pid} -> TODOS msg=\"{request.contenido}\" vector={vector_actualizado}", flush=True)
        
        # Difusión (broadcast) del mensaje a todos los procesos
        self.cliente.difundir(request.contenido, vector_actualizado, self.pid)
        return IDL_pb2.Ack(exito=True)