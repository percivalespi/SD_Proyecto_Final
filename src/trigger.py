import sys
import grpc
import IDL_pb2
import IDL_pb2_grpc

def main():
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python src/trigger.py interno")
        print("  python src/trigger.py enviar <id_destino> <mensaje>")
        print("  python src/trigger.py difusion <mensaje>")
        sys.exit(1)

    comando = sys.argv[1].lower()
    
    channel = grpc.insecure_channel('localhost:50051')
    stub = IDL_pb2_grpc.ProcesoDistribuidoStub(channel)

    try:
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
            
        else:
            print("Comando desconocido.")
            
    except grpc.RpcError as e:
        print(f"Error al conectar con el servidor local: {e}")

if __name__ == '__main__':
    main()