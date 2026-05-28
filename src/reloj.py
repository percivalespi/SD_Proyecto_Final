import threading

class RelojVectorial:
    def __init__(self, process_id, num_procesos=5):
        """
        Inicializa el reloj vectorial para un proceso específico.
        process_id: Índice del proceso actual (0 para P1, 1 para P2, etc.)
        num_procesos: Tamaño del vector.
        """
        self.process_id = process_id
        self.num_procesos = num_procesos
        self.vector = [0] * num_procesos
        self.lock = threading.Lock()

    def evento_interno(self):
        """
        Incrementa el reloj local en la posición del proceso.
        Retorna una copia del vector actualizado.
        """
        with self.lock:
            self.vector[self.process_id] += 1
            return list(self.vector)

    def evento_envio(self):
        """
        Incrementa el reloj local antes de enviar un mensaje.
        Retorna una copia del vector actualizado para empaquetarlo.
        """
        with self.lock:
            self.vector[self.process_id] += 1
            return list(self.vector)

    def evento_recepcion(self, vector_recibido):
        """
        Actualiza el reloj local al recibir un mensaje:
        1. Incrementa su propia posición.
        2. Toma el valor máximo entre el vector local y el recibido para cada posición.
        Retorna una copia del vector actualizado.
        """
        with self.lock:
            self.vector[self.process_id] += 1
            for i in range(self.num_procesos):
                self.vector[i] = max(self.vector[i], vector_recibido[i])
            return list(self.vector)

    def get_vector(self):
        """
        Retorna el estado actual del vector sin incrementarlo.
        """
        with self.lock:
            return list(self.vector)