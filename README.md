# Laboratorios 01 & 02 — Diseño de Lenguajes de Programación

Mario Rocha - 23501, Luis Pedro Lira - 23669, Oliver Viau - 23544 

Repositorio compartido para los laboratorios 01 y 02. Ambos comparten base de código porque el Lab 02 es continuación directa del Lab 01.

### Links del los Videos

- https://youtu.be/FyY4pvIDbAA. Lab1 
- https://youtu.be/aMaKFScaeF4. Lab2 

---

## Lab 01 — Conversión de Expresiones Regulares a AFD

Conversión directa de expresiones regulares a AFD (método directo) y simulación de cadenas.

### Archivos

| Archivo | Descripción |
|---|---|
| `parser.py` | Parser de expresiones regulares y construcción del árbol sintáctico |
| `dfa_builder.py` | Construcción del AFD usando el método directo |
| `simulator.py` | Simulación de cadenas y demo final |

### Operadores soportados

| Operador | Símbolo |
|---|---|
| Unión | `\|` |
| Concatenación | implícita |
| Kleene | `*` |
| Positiva | `+` |
| Opcional | `?` |

### Ejecución

```bash
python simulator.py --demo   # ejecuta la demo oficial
python simulator.py          # demo + modo interactivo
```


---

## Lab 02 — Minimización de un AFD

Aplicación del algoritmo de minimización sobre el AFD generado en el Lab 01.

### Archivo adicional

| Archivo | Descripción |
|---|---|
| `minimizer.py` | Algoritmo de minimización (tabla de Myhill-Nerode / particionamiento) |

### Funcionalidad agregada

- Construcción del AFD directo a partir de una regex.
- Aplicación del algoritmo de minimización.
- Tabla de transición del AFD original y del minimizado.
- Comparación de estados y transiciones entre ambos autómatas.
- Simulación de cadenas usando el AFD minimizado.

### Ejecución

```bash
python simulator.py --demo   # demo oficial con dos expresiones de prueba
python simulator.py          # demo + modo interactivo
```

En el modo interactivo se ingresa la regex y luego se validan cadenas una por una.

---

## Requisitos

Python 3.8 o superior. Sin dependencias externas (no se usan librerías de expresiones regulares).
