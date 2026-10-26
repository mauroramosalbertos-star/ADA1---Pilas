# ADA1---Pilas
pila.py - La clase pila que usan los programas
evaluador.py - 	Evalúa expresiones aritméticas en notación posfija y prefija, mostrando la pila paso a paso.
hanoi.py - Juego de las Torres de Hanoi con interfaz gráfica. Manual y automático.

Evaluador:
Tokens separados por espacio. Operadores: + - * / ^
Posfija: 3 4 + 2 * → 14
Prefija: * + 3 4 2 → 14
Valida división entre cero, operandos faltantes o sobrantes y símbolos inválidos.

Torres de Hanoi:
Manual: clic en la torre de origen y luego en la de destino.
Resolver / Paso / Pausar: solución automática calculada con una segunda Pila de tareas.
Cada torre es un objeto Pila; cada disco es un número.
Mínimo de movimientos: 2^n - 1.
