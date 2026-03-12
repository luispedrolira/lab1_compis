import sys

# ─── Constantes ───────────────────────────────────────────────────────────────

UNARY_OPS  = frozenset({'*', '+', '?'})
BINARY_OPS = frozenset({'|', '·'})

# Precedencia de operadores (mayor número = mayor prioridad)
PRECEDENCE = {
    '|': 1,   # unión           (menor prioridad)
    '·': 2,   # concatenación
    '*': 3,   # Kleene
    '+': 3,   # positiva
    '?': 3,   # opcional        (mayor prioridad)
}


# ─── Nodo del árbol sintáctico ────────────────────────────────────────────────

class Node:
    """
    Nodo del árbol sintáctico.

    - Hojas:    value = símbolo del alfabeto (o '#'), position = entero único
    - Internos: value = operador, left/right = hijos,  position = None
    """

    def __init__(self, value: str, left: 'Node' = None, right: 'Node' = None):
        self.value    = value
        self.left     = left
        self.right    = right
        self.position = None   # solo se asigna en hojas

    def is_leaf(self) -> bool:
        return self.left is None and self.right is None

    # Representación visual del árbol (útil para depurar)
    def __repr__(self, depth: int = 0, prefix: str = "Raíz: ") -> str:
        pad  = "    " * depth
        line = f"{pad}{prefix}'{self.value}'"
        if self.position is not None:
            line += f"  [pos={self.position}]"
        line += "\n"
        if self.left:
            line += self.left.__repr__(depth + 1, "├── ")
        if self.right:
            line += self.right.__repr__(depth + 1, "└── ")
        return line


# ─── Paso 1: Tokenizador ──────────────────────────────────────────────────────

def tokenize(regex: str) -> list:
    """
    Convierte la string de regex en una lista de tokens (un carácter por token).
    Ignora espacios en blanco.

    Ejemplo:
        "(a|b)*abb"  →  ['(', 'a', '|', 'b', ')', '*', 'a', 'b', 'b']
    """
    return [ch for ch in regex if ch != ' ']


# ─── Paso 2: Insertar concatenación explícita ─────────────────────────────────

# Después de estos tokens se puede insertar '·'
_CAN_PRECEDE = frozenset(
    'abcdefghijklmnopqrstuvwxyz'
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    '0123456789)*+?'
)

# Antes de estos tokens se puede insertar '·'
_CAN_FOLLOW = frozenset(
    'abcdefghijklmnopqrstuvwxyz'
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    '0123456789('
)


def add_explicit_concat(tokens: list) -> list:
    """
    Inserta el operador de concatenación explícita '·' donde corresponda.

    Regla: insertar '·' entre tokens[i] y tokens[i+1] si:
        tokens[i]   ∈ { letra, dígito, ), *, +, ? }
        tokens[i+1] ∈ { letra, dígito, ( }

    Ejemplos:
        ['a', 'b']       → ['a', '·', 'b']
        ['a', '*', 'b']  → ['a', '*', '·', 'b']
        [')', '(']       → [')', '·', '(']
        ['a', '|', 'b']  → ['a', '|', 'b']   (no se inserta después de '|')
    """
    result = []
    for i, tok in enumerate(tokens):
        result.append(tok)
        if i + 1 < len(tokens):
            nxt = tokens[i + 1]
            if tok in _CAN_PRECEDE and nxt in _CAN_FOLLOW:
                result.append('·')
    return result


# ─── Paso 3: Shunting-Yard (infix → postfix) ─────────────────────────────────

def to_postfix(tokens: list) -> list:
    """
    Convierte una lista de tokens en notación postfija (RPN)
    usando el algoritmo Shunting-Yard.

    Reglas especiales para regex:
    - Operadores UNARIOS postfijos (*, +, ?): se envían directamente al output
      (ya fueron aplicados al operando anterior, no necesitan ir a la pila).
    - Operadores BINARIOS (|, ·): usan la pila con comparación de precedencia.
    - Todos son left-associative.

    Lanza ValueError si los paréntesis están desbalanceados.
    """
    output   = []
    op_stack = []

    for tok in tokens:

        if tok == '(':
            op_stack.append(tok)

        elif tok == ')':
            while op_stack and op_stack[-1] != '(':
                output.append(op_stack.pop())
            if not op_stack:
                raise ValueError("Paréntesis desbalanceados: ')' sin '(' correspondiente.")
            op_stack.pop()   # descartar '('

        elif tok in UNARY_OPS:
            # Operador unario postfijo: va directo al output
            output.append(tok)

        elif tok in BINARY_OPS:
            # Sacar de la pila operadores de mayor o igual precedencia (left-assoc)
            while (op_stack
                   and op_stack[-1] != '('
                   and op_stack[-1] in PRECEDENCE
                   and PRECEDENCE[op_stack[-1]] >= PRECEDENCE[tok]):
                output.append(op_stack.pop())
            op_stack.append(tok)

        else:
            # Operando: símbolo del alfabeto o '#'
            output.append(tok)

    # Vaciar la pila
    while op_stack:
        top = op_stack.pop()
        if top == '(':
            raise ValueError("Paréntesis desbalanceados: '(' sin ')' correspondiente.")
        output.append(top)

    return output


# ─── Paso 4: Construir árbol sintáctico ──────────────────────────────────────

def build_tree(postfix: list) -> Node:
    """
    Construye el árbol sintáctico a partir de una expresión postfija.

    Operadores unarios  (*, +, ?): un hijo  → nodo.left = operando
    Operadores binarios (|,  ·  ): dos hijos → nodo.left = operando izquierdo
                                               nodo.right = operando derecho
    Todo lo demás: nodo hoja (símbolo).

    Lanza ValueError si la expresión está mal formada.
    """
    stack = []

    for tok in postfix:
        if tok in UNARY_OPS:
            if not stack:
                raise ValueError(f"Operador unario '{tok}' sin operando.")
            child = stack.pop()
            stack.append(Node(tok, left=child))

        elif tok in BINARY_OPS:
            if len(stack) < 2:
                raise ValueError(f"Operador binario '{tok}' requiere dos operandos.")
            right = stack.pop()
            left  = stack.pop()
            stack.append(Node(tok, left=left, right=right))

        else:
            stack.append(Node(tok))

    if len(stack) != 1:
        raise ValueError(f"Expresión mal formada: quedaron {len(stack)} nodos en la pila.")

    return stack[0]


# ─── Paso 5: Numerar hojas ────────────────────────────────────────────────────

def _number_leaves_inorder(node: Node, counter: list) -> None:
    """Recorrido in-order: asigna posiciones a las hojas de izquierda a derecha."""
    if node is None:
        return
    _number_leaves_inorder(node.left, counter)
    if node.is_leaf():
        node.position = counter[0]
        counter[0] += 1
    _number_leaves_inorder(node.right, counter)


def number_leaves(root: Node) -> None:
    """
    Asigna posiciones únicas a todas las hojas del árbol.
    Las posiciones se asignan de izquierda a derecha (recorrido in-order),
    comenzando en 1, tal como especifica el método directo del Libro del Dragón.
    """
    _number_leaves_inorder(root, [1])


# ─── Helpers internos ────────────────────────────────────────────────────────

def _find_hash_position(node: Node):
    """Busca y retorna la posición de la hoja '#' en el árbol."""
    if node is None:
        return None
    if node.is_leaf() and node.value == '#':
        return node.position
    return _find_hash_position(node.left) or _find_hash_position(node.right)


def _collect_leaves(node: Node, result: dict) -> None:
    """Recorre el árbol y llena el diccionario {posición: símbolo}."""
    if node is None:
        return
    if node.is_leaf():
        result[node.position] = node.value
    _collect_leaves(node.left, result)
    _collect_leaves(node.right, result)


# ─── Interfaz pública (para Persona 2) ───────────────────────────────────────

def get_leaf_positions(root: Node) -> dict:
    """
    Retorna un diccionario {posición: símbolo} para todas las hojas del árbol.
    Ejemplo: {1: 'a', 2: 'b', 3: 'a', 4: 'b', 5: 'b', 6: '#'}

    Persona 2 lo usa para saber qué símbolo corresponde a cada posición
    al construir la tabla de transiciones.
    """
    result = {}
    _collect_leaves(root, result)
    return result


def parse(regex: str):
    """
    Pipeline completo: string de regex → árbol sintáctico con hojas numeradas.

    Pasos internos:
      1. Tokenizar
      2. Insertar concatenación explícita (·)
      3. Augmentar: añadir '·' '#' al final  →  r · #
      4. Convertir a postfijo (Shunting-Yard)
      5. Construir árbol sintáctico
      6. Numerar hojas (in-order, empezando en 1)

    Retorna:
        (root, hash_position)
        root          — Node raíz del árbol augmentado
        hash_position — posición entera del símbolo '#'
                        (Persona 2: un estado es de ACEPTACIÓN si contiene
                         esta posición en su conjunto de posiciones)

    NOTA: No se acepta '#' como símbolo en la regex del usuario, ya que
          se usa internamente como marcador de fin.
    """
    if '#' in regex:
        raise ValueError("El símbolo '#' está reservado como marcador de fin. "
                         "No puede usarse en la expresión regular.")

    # 1. Tokenizar
    tokens = tokenize(regex)
    if not tokens:
        raise ValueError("La expresión regular está vacía.")

    # 2. Concatenación explícita
    tokens = add_explicit_concat(tokens)

    # 3. Augmentar: r · #
    tokens = tokens + ['·', '#']

    # 4. Postfijo
    postfix = to_postfix(tokens)

    # 5. Árbol
    root = build_tree(postfix)

    # 6. Numerar hojas
    number_leaves(root)

    # Posición del marcador de aceptación
    hash_pos = _find_hash_position(root)

    return root, hash_pos


# ─── Demo / CLI ───────────────────────────────────────────────────────────────

def _demo():
    """Ejecuta el pipeline con las 3 expresiones regulares del lab."""
    test_cases = [
        "(a|b)*abb",
        "a+b?c",
        "(a|b)+c*(d?)",
    ]

    for regex in test_cases:
        print(f"\n{'═' * 58}")
        print(f"  Regex:           {regex}")
        print(f"{'═' * 58}")

        # Pasos intermedios (para verificación)
        tok_raw    = tokenize(regex)
        tok_concat = add_explicit_concat(tok_raw)
        tok_full   = tok_concat + ['·', '#']
        postfix    = to_postfix(tok_full)

        print(f"  Tokens:          {tok_raw}")
        print(f"  Con concat (·):  {tok_concat}")
        print(f"  Augmentado:      {tok_full}")
        print(f"  Postfijo:        {postfix}")

        # Árbol final
        root = build_tree(postfix)
        number_leaves(root)
        hash_pos = _find_hash_position(root)
        leaves   = get_leaf_positions(root)

        print(f"\n  Árbol sintáctico:")
        print(root)
        print(f"  Mapa de posiciones: {leaves}")
        print(f"  Posición de '#':    {hash_pos}  ← estados de aceptación")


def _interactive():
    """Modo interactivo: el usuario ingresa su propia regex."""
    print("=" * 58)
    print("  Parser de Expresiones Regulares — Lab 01")
    print("  Operadores soportados: | * + ? ( )")
    print("  Escribe 'salir' para terminar.")
    print("=" * 58)

    while True:
        try:
            regex = input("\n  Ingresa una regex: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Saliendo...")
            break

        if regex.lower() in ('salir', 'exit', 'quit'):
            break
        if not regex:
            continue

        try:
            root, hash_pos = parse(regex)
            leaves = get_leaf_positions(root)

            print(f"\n  Árbol sintáctico (regex augmentada: ({regex})·#):")
            print(root)
            print(f"  Mapa de posiciones: {leaves}")
            print(f"  Posición de '#':    {hash_pos}  ← estados de aceptación")

        except ValueError as e:
            print(f"  ✗ Error: {e}")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        _demo()
    else:
        _demo()
        print(f"\n{'─' * 58}")
        print("  Modo interactivo (Ctrl+C para salir)")
        _interactive()
