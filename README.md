# Lab 01 — Diseño de Lenguajes de Programación

## Conversión directa de Regex a AFD y simulación

**Entrega:** jueves 12 de marzo de 2026 | 19:00 horas | **10 puntos**

---

## ¿Qué hay que hacer?

Desarrollar un programa (en el lenguaje que elija el grupo) que:

- Reciba una expresión regular como entrada
- Construya el AFD usando el método directo (árbol sintáctico → nullable/firstpos/lastpos/followpos → tabla de transiciones)
- Muestre la tabla de transición de estados resultante
- Reciba una cadena y determine si **ACEPTA** o **RECHAZA** usando el AFD construido

Además, se debe grabar un video en YouTube (máx. 5 min) demostrando el programa con 3 expresiones regulares distintas.

> ⚠️ **PROHIBIDO** usar librerías de expresiones regulares. Hacerlo = **0 puntos** en el lab.

---

## División de trabajo

El trabajo se divide en tres módulos secuenciales. Persona 1 debe terminar primero para que Persona 2 pueda continuar, y así sucesivamente.

| Integrante | Módulo | Responsabilidad |
|---|---|---|
| **Persona 1** | Parser / Árbol sintáctico | • Tokenizar la regex · • Insertar concatenación explícita · • Convertir a postfijo (shunting yard) · • Construir árbol sintáctico |
| **Persona 2** | AFD (nullable/firstpos/followpos) | • Calcular nullable en cada nodo · • Calcular firstpos y lastpos · • Calcular followpos · • Construir tabla de transiciones |
| **Persona 3** | Simulación + Video | • Simular el AFD con cadenas · • Mostrar tabla de transiciones · • Mostrar resultado ACEPTA/RECHAZA · • Grabar y editar video demo (<5 min) |

---

## Detalle de cada módulo

### Persona 1 — Parser y árbol sintáctico

Es el módulo más crítico, ya que todo lo demás depende de que el árbol esté bien construido.

- Leer la regex como string y tokenizarla (identificar letras, operadores, paréntesis)
- Insertar el operador de concatenación explícita (`·`) donde corresponda
- Convertir la expresión a notación postfija usando el algoritmo **Shunting-Yard**
- Construir el árbol sintáctico desde el postfijo
- Agregar el símbolo `#` al final (para el método directo: `(regex)·#`)
- Numerar las hojas del árbol con posiciones únicas

> **Referencia:** Libro del Dragón (Aho, Lam, Sethi, Ullman), Sección 3.9.

---

### Persona 2 — nullable, firstpos, lastpos, followpos y tabla AFD

Recibe el árbol de Persona 1 y calcula las funciones sobre cada nodo para construir el AFD.

- Calcular `nullable(n)`: ¿puede el nodo generar la cadena vacía?
- Calcular `firstpos(n)`: conjunto de posiciones que pueden ser primera posición
- Calcular `lastpos(n)`: conjunto de posiciones que pueden ser última posición
- Calcular `followpos(i)`: posiciones que pueden seguir a la posición i
- Construir los estados del AFD como conjuntos de posiciones
- Construir la tabla de transición completa
- Identificar estados de aceptación (los que contienen la posición del símbolo `#`)

**Entregar a Persona 3:** la tabla de transiciones, el estado inicial y los estados de aceptación.

---

### Persona 3 — Simulación del AFD + video

Recibe la tabla de Persona 2 y la usa para validar cadenas. También se encarga del video.

- Implementar la función de simulación: leer la cadena símbolo a símbolo siguiendo la tabla
- Si al terminar la cadena estamos en estado de aceptación → **ACEPTA**, de lo contrario → **RECHAZA**
- Manejar el caso donde no existe transición para un símbolo (rechazar inmediatamente)
- Mostrar la tabla de transiciones en consola de forma clara y legible
- Grabar el video de demostración (máx. 5 minutos)

---

## Expresiones regulares para la demo

Estas 3 expresiones cubren todos los operadores requeridos entre sí:

| # | Expresión regular | Operadores usados | Notas |
|---|---|---|---|
| 1 | `(a\|b)*abb` | `\|` , `*` , concatenación | Cadena válida: `abb`, `aabb`. Inválida: `ab` |
| 2 | `a+b?c` | `+` , `?` , concatenación | Cadena válida: `ac`, `abc`. Inválida: `bc` |
| 3 | `(a\|b)+c*(d?)` | `\|` , `+` , `*` , `?` , concat. | Cadena válida: `acd`, `bc`. Inválida: `cd` |

Entre las 3 expresiones deben aparecer: `|` (unión), `*` (Kleene), `+` (positiva), `?` (opcional) y concatenación implícita.

---

## Rúbrica (cómo nos van a calificar)

- **60%** — Tablas de transición correctas y todos los operadores usados
- **30%** — Cadenas validadas correctamente (6 en total: 3 válidas + 3 inválidas)
- **10%** — Calidad de la explicación en el video

---

## Checklist de entrega

- [ ] El programa recibe una expresión regular como input
- [ ] El programa construye el AFD con el método directo (sin librerías de regex)
- [ ] Se muestra la tabla de transición de estados
- [ ] El programa recibe una cadena y dice si ACEPTA o RECHAZA
- [ ] Se probaron las 3 expresiones regulares propuestas
- [ ] Cada expresión tiene: tabla de transición + cadena válida + cadena inválida
- [ ] Entre las 3 expresiones aparecen todos los operadores: `|` `*` `+` `?` concatenación
- [ ] El video dura máximo 5 minutos y está subido a YouTube