# Especificaciones del Proyecto

## Descripción General
Desarrollar una simulación de un sistema distribuido compuesto por varios procesos independientes,
donde cada proceso estará implementado dentro de un contenedor Docker.

Cada proceso deberá ejecutar su propio servidor RPC usando gRPC, enviar mensajes a otros procesos
mediante un cliente RPC, mantener un reloj vectorial para registrar el orden lógico de los eventos, y
registrar eventos internos, envíos y recepciones en una bitácora.

El objetivo del proyecto es comprender cómo se mantiene  el orden lógico de eventos en sistemas
distribuidos mediante el uso de relojes vectoriales.

El sistema estará compuesto por 5 contenedores Docker. Cada contenedor representará un proceso
distribuido e incluirá:

-Servidor gRPC
-Cliente gRPC
-Reloj vectorial propio
-Registro de eventos (bitácora)