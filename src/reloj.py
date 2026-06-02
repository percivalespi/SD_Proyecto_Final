"""
Equipo:
- Duque Malpica Victor Javier
- Espinoza Matamoros Percival Ulises
- Flores Colín Victor Jaziel
- Migueles Martínez Lino Shatini
Fecha: 02-06-2026
"""

import threading

# Clase para el manejo de lo relojes vectorriales
class RelojVectorial:
    def __init__(self, process_id, num_procesos=5):
        self.process_id = process_id
        self.num_procesos = num_procesos
        self.vector = [0] * num_procesos
        # Uso de LOCK para asegurar la consistencia del reloj
        self.lock = threading.Lock()

    # Incremento del reloj local para eventos internos
    def evento_interno(self):
        with self.lock:
            self.vector[self.process_id] += 1
            return list(self.vector)

    # Incremento del reloj local para eventos de envío
    def evento_envio(self):
        with self.lock:
            self.vector[self.process_id] += 1
            return list(self.vector)

    # Incremento del reloj local para eventos de recepción
    def evento_recepcion(self, vector_recibido):
        with self.lock:
            self.vector[self.process_id] += 1
            for i in range(self.num_procesos):
                # Toma el máximo entre el vector local y el recibido
                self.vector[i] = max(self.vector[i], vector_recibido[i])
            return list(self.vector)

    # Obtiene el vector actual del proceso
    def get_vector(self):
        with self.lock:
            return list(self.vector)