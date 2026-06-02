"""
Equipo:
- Duque Malpica Victor Javier
- Espinoza Matamoros Percival Ulises
- Flores Colín Victor Jaziel
- Migueles Martínez Lino Shatini
Fecha: 02-06-2026
"""

# Modulo para interacutar con los procesos por medio de la linea de comandos

import sys
import grpc
import IDL_pb2
import IDL_pb2_grpc

def main():
    # Validando formato de los argumentos por linea de comandos
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python src/trigger.py interno")
        print("  python src/trigger.py enviar <id_destino> <mensaje>")
        print("  python src/trigger.py difusion <mensaje>")
        sys.exit(1)

    comando = sys.argv[1].lower()

    # Estableciendo conexión gRPC con el servidor local
    channel = grpc.insecure_channel('localhost:50051')
    stub = IDL_pb2_grpc.ProcesoDistribuidoStub(channel)

    # Ejecucion del comando correspondiente
    try:
        # El servicio de evento interno no requiere argumentos adicionales
        if comando == "interno":
            stub.EventoInterno(IDL_pb2.Vacio())
        
        elif comando == "enviar":
            id_destino = int(sys.argv[2])
            mensaje = sys.argv[3]
            req = IDL_pb2.MensajeEnvio(id_receptor=id_destino, contenido=mensaje)
            stub.EnviarMensaje(req)
            
        elif comando == "difusion":
            mensaje = sys.argv[2]
            req = IDL_pb2.MensajeEnvio(contenido=mensaje)
            stub.Difusion(req)
        
        # NOTA: La recepción de mensajes la realiza el servidor gRPC automáticamente
            
        else:
            print("Comando desconocido.")
            
    except grpc.RpcError as e:
        print(f"Error al conectar con el servidor local: {e}")

if __name__ == '__main__':
    main()