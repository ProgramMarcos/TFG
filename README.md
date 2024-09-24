# TFG
Hola, mi nombre es Marcos López López y vengo a presentarles mi trabajo de fin de grado, basado en el desarrollo de una aplicación interactiva para un sistema multieje, empleando técnicas de visión artificial, desarrollado bajo la tutela de los profesores Julio Garrido Campos y Diego Silva Muñiz.

En el departamento de Automática de la Escuela existe una máquina cartesiana XY que cuenta con un rotulador y un borrador en su efector final. Partiendo de esto se me propuso:
1. Sustituir la interfaz táctil de la maqueta por una interfaz comandada con visión artificial.
2. Llevar a cabo una reautomatización completa que la dotase de una nueva funcionalidad.

Concluímos que se podría realizar una especie de videojuego con visión artificial, por el cuál un usuario sin conocimientos en ingeniería pudiese manejar el efector final a través de una estructura pasiva en forma de volante sostenido en el aire, sin ninguna tecnología asociada al mismo, o una libreta en su ausencia.
Por medio de la aplicación desarrollada el usuario debería de ser capaz de hacer que los ejes acompañen el movimiento del volante con el objetivo de seguir un circuito previamente dibujado en la pizarra, como si de un videojuego se tratase. 

El proyecto se divide fundamentalmente en dos partes: 
Una parte correspondiente a lo relacionado con visión Artificial, para lo que se ha creado un modelo de red neuronal personalizado basado en YOLO V8 de Ultralytics y, con el uso de Python 3 y la librería de OpenCV se logra la detección de objetos (un volante de cartón con marcas, una libreta y las manos) detectando angulos de giro, consignas de movimiento, cambios en el modo operativo de la maqueta...

Por otro lado se cuenta con una aplicación en TwinCAT3, que comanda un PLC CX5130 de Beckhoff, encargado de recibir las consignas de la aplicación de Python, por comunicación ADS, y actuar sobre la maqueta en base a estas consignas.

Tanto en el documento RESUMEN.pdf como en el documento presentacion.pdf se puede ver, a grandes rasgos, cómo opera el sistema.

