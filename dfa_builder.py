"""
Lab 01 — Diseño de Lenguajes de Programación

  1. Calcular nullable, firstpos y lastpos para cada nodo del árbol
  2. Calcular followpos para cada posición
  3. Construir los estados del AFD (conjuntos de posiciones)
  4. Construir la tabla de transiciones
  5. Identificar estados de aceptación (los que contienen la posición de #)

"""

#python dfa_builder.py --demo 

from parser import Node, get_leaf_positions, parse
from typing import Dict, Set, List, Tuple, Optional
from collections import defaultdict
import sys


#calcular nullable, firstpos, lastpos
def compute_nullable(node: Node) -> bool:
    """
    Calcula si un nodo es nullable (puede generar la cadena vacía).
    
    Reglas:
    - Hoja (símbolo o #): False (solo si es ε, pero no manejamos ε explícito)
    - Nodo '|': nullable(left) or nullable(right)
    - Nodo '·': nullable(left) and nullable(right)
    - Nodo '*': True
    - Nodo '+': nullable(left)   (una o más veces, puede ser vacío solo si left es nullable)
    - Nodo '?': True
    """
    if node.is_leaf():
        # Las hojas nunca son nullables (excepto ε, que no tenemos)
        return False
    
    if node.value == '|':
        return compute_nullable(node.left) or compute_nullable(node.right)
    
    elif node.value == '·':
        return compute_nullable(node.left) and compute_nullable(node.right)
    
    elif node.value == '*':
        return True
    
    elif node.value == '+':
        # Una o más repeticiones: puede ser vacío solo si el operando es nullable
        return compute_nullable(node.left)
    
    elif node.value == '?':
        return True
    
    else:
        raise ValueError(f"Operador desconocido: {node.value}")


def compute_firstpos(node: Node) -> Set[int]:
    """
    Calcula el conjunto firstpos para un nodo.
    
    Reglas:
    - Hoja (símbolo o #): {posición}
    - Nodo '|': firstpos(left) ∪ firstpos(right)
    - Nodo '·': firstpos(left) ∪ (firstpos(right) si nullable(left))
    - Nodo '*', '+', '?': firstpos(left)
    """
    if node.is_leaf():
        return {node.position}
    
    if node.value == '|':
        return compute_firstpos(node.left) | compute_firstpos(node.right)
    
    elif node.value == '·':
        left_first = compute_firstpos(node.left)
        if compute_nullable(node.left):
            return left_first | compute_firstpos(node.right)
        else:
            return left_first
    
    elif node.value in {'*', '+', '?'}:
        return compute_firstpos(node.left)
    
    else:
        raise ValueError(f"Operador desconocido: {node.value}")


def compute_lastpos(node: Node) -> Set[int]:
    """
    Calcula el conjunto lastpos para un nodo.
    
    Reglas:
    - Hoja (símbolo o #): {posición}
    - Nodo '|': lastpos(left) ∪ lastpos(right)
    - Nodo '·': lastpos(right) ∪ (lastpos(left) si nullable(right))
    - Nodo '*', '+', '?': lastpos(left)
    """
    if node.is_leaf():
        return {node.position}
    
    if node.value == '|':
        return compute_lastpos(node.left) | compute_lastpos(node.right)
    
    elif node.value == '·':
        right_last = compute_lastpos(node.right)
        if compute_nullable(node.right):
            return right_last | compute_lastpos(node.left)
        else:
            return right_last
    
    elif node.value in {'*', '+', '?'}:
        return compute_lastpos(node.left)
    
    else:
        raise ValueError(f"Operador desconocido: {node.value}")


def annotate_tree(node: Node) -> Tuple[bool, Set[int], Set[int]]:
    """
    Anota el árbol completo con nullable, firstpos y lastpos.
    Retorna (nullable, firstpos, lastpos) para el nodo actual.
    """
    if node.is_leaf():
        nullable = False
        firstpos = {node.position}
        lastpos = {node.position}
    
    elif node.value == '|':
        left_null, left_first, left_last = annotate_tree(node.left)
        right_null, right_first, right_last = annotate_tree(node.right)
        nullable = left_null or right_null
        firstpos = left_first | right_first
        lastpos = left_last | right_last
    
    elif node.value == '·':
        left_null, left_first, left_last = annotate_tree(node.left)
        right_null, right_first, right_last = annotate_tree(node.right)
        nullable = left_null and right_null
        firstpos = left_first | (right_first if left_null else set())
        lastpos = right_last | (left_last if right_null else set())
    
    elif node.value == '*':
        child_null, child_first, child_last = annotate_tree(node.left)
        nullable = True
        firstpos = child_first
        lastpos = child_last
    
    elif node.value == '+':
        child_null, child_first, child_last = annotate_tree(node.left)
        nullable = child_null
        firstpos = child_first
        lastpos = child_last
    
    elif node.value == '?':
        child_null, child_first, child_last = annotate_tree(node.left)
        nullable = True
        firstpos = child_first
        lastpos = child_last
    
    else:
        raise ValueError(f"Operador desconocido: {node.value}")
    
    # Guardamos los valores en el nodo para referencia
    node.nullable = nullable
    node.firstpos = firstpos
    node.lastpos = lastpos
    
    return nullable, firstpos, lastpos


# followpos 

def compute_followpos(node: Node, followpos: Dict[int, Set[int]]) -> None:
    """
    Calcula followpos para todas las posiciones del árbol.
    
    Reglas:
    - Nodo '·': para cada posición i en lastpos(left), 
                followpos[i] ∪= firstpos(right)
    - Nodo '*', '+': para cada posición i en lastpos(node),
                     followpos[i] ∪= firstpos(node)
    """
    if node.is_leaf():
        return
    
    if node.value == '·':
        # Regla 1: followpos para lastpos del hijo izquierdo
        left_last = node.left.lastpos
        right_first = node.right.firstpos
        for pos in left_last:
            followpos[pos].update(right_first)
        
        #  recursivamente
        compute_followpos(node.left, followpos)
        compute_followpos(node.right, followpos)
    
    elif node.value in {'*', '+'}:
        # Regla 2: followpos para lastpos del nodo actual
        node_last = node.lastpos
        node_first = node.firstpos
        for pos in node_last:
            followpos[pos].update(node_first)
        
        # recursivamente
        compute_followpos(node.left, followpos)
    
    elif node.value == '|':
        #  procesar recursivamente
        compute_followpos(node.left, followpos)
        compute_followpos(node.right, followpos)
    
    elif node.value == '?':
        #  procesar recursivamente
        compute_followpos(node.left, followpos)
    
    else:
        raise ValueError(f"Operador desconocido: {node.value}")


def build_followpos(root: Node) -> Dict[int, Set[int]]:
    """
    Construye el diccionario de followpos para todas las posiciones.
    """
    followpos = defaultdict(set)
    compute_followpos(root, followpos)
    return dict(followpos)


#Construcción de estados AFD

def build_dfa_states(
    firstpos_root: Set[int],
    followpos: Dict[int, Set[int]],
    symbols: Dict[int, str]
) -> Tuple[List[Set[int]], Dict[Tuple[int, str], int], Set[int]]:
    """
    Construye los estados del AFD usando el método directo.
    
    Args:
        firstpos_root: firstpos del nodo raíz
        followpos: diccionario de followpos
        symbols: mapa {posición: símbolo}
    
    Returns:
        states: lista de conjuntos de posiciones (cada conjunto es un estado)
        transitions: diccionario (estado_idx, símbolo) -> estado_idx
        accepting_states: conjunto de índices de estados de aceptación
    """
    # Obtener símbolos únicos del alfabeto (excluyendo '#')
    alphabet = sorted(set(sym for pos, sym in symbols.items() if sym != '#'))
    
    # El estado inicial es firstpos de la raíz
    start_state = firstpos_root
    
    states = [start_state]  # lista de conjuntos de posiciones
    state_indices = {frozenset(start_state): 0}  # mapeo conjunto -> índice
    
    # Identificar estados de aceptación (los que contienen la posición de #)
    hash_positions = [pos for pos, sym in symbols.items() if sym == '#']
    # En una expresión augmentada bien formada, solo hay un '#'
    hash_pos = hash_positions[0] if hash_positions else None
    
    transitions = {}
    accepting_states = set()
    
    # Construcción iterativa de estados
    queue = [0]  # cola de estados por procesar
    while queue:
        current_idx = queue.pop(0)
        current_state = states[current_idx]
        
        # Verificar si es estado de aceptación
        if hash_pos and hash_pos in current_state:
            accepting_states.add(current_idx)
        
        # Para cada símbolo del alfabeto
        for sym in alphabet:
            # Calcular el conjunto de posiciones alcanzables con este símbolo
            next_state = set()
            for pos in current_state:
                if symbols.get(pos) == sym:
                    next_state.update(followpos.get(pos, set()))
            
            if not next_state:
                continue  # no hay transición para este símbolo
            
            # Normalizar a frozenset para usar como clave
            next_frozen = frozenset(next_state)
            
            if next_frozen not in state_indices:
                # Nuevo estado
                new_idx = len(states)
                state_indices[next_frozen] = new_idx
                states.append(next_state)
                queue.append(new_idx)
            else:
                new_idx = state_indices[next_frozen]
            
            # Registrar transición
            transitions[(current_idx, sym)] = new_idx
    
    return states, transitions, accepting_states


def print_transition_table(
    states: List[Set[int]],
    transitions: Dict[Tuple[int, str], int],
    alphabet: List[str],
    accepting_states: Set[int],
    start_state_idx: int = 0,
    symbols: Dict[int, str] = None
):
    """
    Imprime la tabla de transiciones de forma legible.
    """
    print("TABLA DE TRANSICIONES DEL AFD")

    
    # Cabecera
    header = "Estado   | " + " | ".join(f"{sym:^5}" for sym in alphabet)
    print(header)
    print("-" * len(header))
    
    for i, state in enumerate(states):
        # Marcar estado inicial y estados de aceptación
        state_str = f"{i}"
        if i == start_state_idx:
            state_str += " →"
        if i in accepting_states:
            state_str += "*"
        

        if symbols:
            pos_str = "{" + ",".join(str(p) for p in sorted(state)) + "}"
            state_str += f" {pos_str:15}"
        else:
            state_str = f"{state_str:6}"
        
        row = f"{state_str:10} |"
        for sym in alphabet:
            next_state = transitions.get((i, sym), '-')
            row += f" {next_state:^5} |"
        print(row)
    
    print("\nLeyenda:")
    print("  → : Estado inicial")
    print("  * : Estado de aceptación")
    print("  - : Transición no definida (lleva a rechazo)")


# ─── Interfaz pública (para Persona 3) ──────────────────────────────────────

class DFA:
    """
    Clase que encapsula el AFD construido.
    Persona 3 usará esta clase para simular cadenas.
    """
    
    def __init__(self, root: Node, hash_pos: int):
        """
        Construye el AFD a partir del árbol sintáctico augmentado.
        """
        self.root = root
        self.hash_pos = hash_pos
        self.symbols = get_leaf_positions(root)
        
        # Anotar el árbol con nullable, firstpos, lastpos
        annotate_tree(root)
        
        # Calcular followpos
        self.followpos = build_followpos(root)
        
        # Construir estados del DFA
        self.states, self.transitions, self.accepting = build_dfa_states(
            root.firstpos, self.followpos, self.symbols
        )
        
        # Alfabeto (símbolos sin '#')
        self.alphabet = sorted(set(
            sym for pos, sym in self.symbols.items() if sym != '#'
        ))
        
        self.start_state = 0
    
    def simulate(self, input_string: str) -> bool:
        """
        Simula el AFD con una cadena de entrada.
        Retorna True si la cadena es aceptada, False en caso contrario.
        """
        current_state = self.start_state
        
        for i, char in enumerate(input_string):
            if char not in self.alphabet:
                print(f"  Símbolo '{char}' no está en el alfabeto")
                return False
            
            next_state = self.transitions.get((current_state, char))
            if next_state is None:
                print(f"  No hay transición desde {current_state} con '{char}'")
                return False
            
            current_state = next_state
        
        # Verificar si el estado final es de aceptación
        return current_state in self.accepting
    
    def print_info(self):
        """
        Muestra toda la información del AFD.
        """
        print("INFORMACIÓN DEL ÁRBOL SINTÁCTICO")
        print(f"Símbolos por posición: {self.symbols}")
        print(f"Posición de #: {self.hash_pos}")
        
        print("FUNCIONES nullable, firstpos, lastpos")

        self._print_node_info(self.root)
        
        print("FOLLOWPOS")
        for pos in sorted(self.followpos.keys()):
            print(f"  followpos({pos}) = {sorted(self.followpos[pos])}")
        
        print("ESTADOS DEL AFD (conjuntos de posiciones)")

        for i, state in enumerate(self.states):
            marca = "→" if i == self.start_state else " "
            marca += "*" if i in self.accepting else " "
            print(f"  Estado {i}{marca}: {sorted(state)}")
        
        print_transition_table(
            self.states, self.transitions, self.alphabet,
            self.accepting, self.start_state, self.symbols
        )
    
    def _print_node_info(self, node: Node, depth: int = 0):
        """Muestra nullable, firstpos, lastpos para cada nodo."""
        indent = "  " * depth
        if node.is_leaf():
            print(f"{indent}Hoja '{node.value}' [pos={node.position}]: "
                  f"nullable={node.nullable}, firstpos={node.firstpos}, "
                  f"lastpos={node.lastpos}")
        else:
            print(f"{indent}Nodo '{node.value}': nullable={node.nullable}, "
                  f"firstpos={node.firstpos}, lastpos={node.lastpos}")
            if node.left:
                self._print_node_info(node.left, depth + 1)
            if node.right:
                self._print_node_info(node.right, depth + 1)


def build_dfa_from_regex(regex: str) -> DFA:
    """
    Función de alto nivel: recibe una regex y retorna el DFA construido.
    """
    root, hash_pos = parse(regex)
    return DFA(root, hash_pos)


# Demo / CLI 
def _demo():
    """pipeline completo con las 3 expresiones"""
    test_cases = [
        ("(a|b)*abb", [
            ("abb", True),    # válida
            ("aabb", True),   # válida
            ("ab", False),    # inválida
            ("ba", False),    # inválida
        ]),
        ("a+b?c", [
            ("ac", True),     # válida
            ("abc", True),    # válida
            ("bc", False),    # inválida
            ("aabc", False),  # inválida
        ]),
        ("(a|b)+c*(d?)", [
            ("acd", True),    # válida
            ("bc", True),     # válida
            ("cd", False),    # inválida
            ("a", False),     # inválida
        ]),
    ]
    
    for regex, test_strings in test_cases:

        print(f"  EXPRESIÓN REGULAR: {regex}")

        
        # Construir DFA
        dfa = build_dfa_from_regex(regex)
        dfa.print_info()
        
        # Probar cadenas

        print("SIMULACIÓN DE CADENAS")
        for input_str, expected in test_strings:
            result = dfa.simulate(input_str)
            status = " ACEPTA" if result else "RECHAZA"
            expected_str = "ACEPTA" if expected else "RECHAZA"
            print(f"  '{input_str}': {status} (esperado: {expected_str})")


def _interactive():
    """Modo interactivo para probar expresiones personalizadas."""

    print("  Ingresa una expresión regular para construir su AFD")
    print("  Luego puedes probar cadenas (escribe 'salir' para terminar)")
    
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
            # Construir DFA
            dfa = build_dfa_from_regex(regex)
            dfa.print_info()
            
            # Modo simulación de cadenas
            print("MODO SIMULACIÓN — Ingresa cadenas para probar (vacío para volver)")

            
            while True:
                try:
                    input_str = input("\n  Cadena a probar: ").strip()
                    if not input_str:
                        break
                    
                    result = dfa.simulate(input_str)
                    print(f"  → {'ACEPTA' if result else 'RECHAZA'}")
                    
                except KeyboardInterrupt:
                    print("\n  Volviendo...")
                    break
                    
        except ValueError as e:
            print(f"  Error: {e}")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        _demo()
    else:
        _demo()
        print(f"\n{'─'*60}")
        print("  Modo interactivo (Ctrl+C para salir)")
        _interactive()