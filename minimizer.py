from typing import Dict, Set, List, Tuple

def minimize_dfa(
    states: List[Set[int]],
    transitions: Dict[Tuple[int, str], int],
    alphabet: List[str],
    accepting: Set[int],
    start_state: int = 0,
) -> Tuple[
    List[frozenset],           
    Dict[Tuple[int, str], int], 
    Set[int],                  
    int,                       
    List[int],                 
]:
    n = len(states)

    # ── Paso 1: alcanzabilidad desde el estado inicial ──────────────────────
    reachable = _reachable_states(n, transitions, alphabet, start_state)

    # ── Paso 2: partición inicial ────────────────────────────────────────────
    accepting_r   = frozenset(s for s in reachable if s in accepting)
    non_accepting = frozenset(s for s in reachable if s not in accepting)

    partition: List[frozenset] = []
    if accepting_r:
        partition.append(accepting_r)
    if non_accepting:
        partition.append(non_accepting)

    # ── Paso 3: refinamiento ────────────────────────────────────────────────
    changed = True
    while changed:
        changed = False
        new_partition: List[frozenset] = []

        # Mapa rápido estado -> índice de bloque actual
        state_to_block = _state_to_block_map(partition)

        for block in partition:
            splits = _split_block(block, transitions, alphabet, state_to_block)
            new_partition.extend(splits)
            if len(splits) > 1:
                changed = True

        partition = new_partition

    # construir AFD minimizado
    state_to_block = _state_to_block_map(partition)

    min_start = state_to_block[start_state]


    min_accepting: Set[int] = set()
    for s in accepting:
        if s in state_to_block:
            min_accepting.add(state_to_block[s])


    min_transitions: Dict[Tuple[int, str], int] = {}
    for block_idx, block in enumerate(partition):
        rep = next(iter(block))   # representante del bloque
        for sym in alphabet:
            dest = transitions.get((rep, sym))
            if dest is not None and dest in state_to_block:
                min_transitions[(block_idx, sym)] = state_to_block[dest]

    mapping = [state_to_block.get(i, -1) for i in range(n)]

    return partition, min_transitions, min_accepting, min_start, mapping


# Helpers
def _reachable_states(
    n: int,
    transitions: Dict[Tuple[int, str], int],
    alphabet: List[str],
    start: int,
) -> Set[int]:
    """BFS/DFS desde el estado inicial para obtener estados alcanzables."""
    visited = set()
    stack = [start]
    while stack:
        s = stack.pop()
        if s in visited:
            continue
        visited.add(s)
        for sym in alphabet:
            dest = transitions.get((s, sym))
            if dest is not None and dest not in visited:
                stack.append(dest)
    return visited


def _state_to_block_map(partition: List[frozenset]) -> Dict[int, int]:
    """Construye el mapa {estado: índice_de_bloque}."""
    mapping: Dict[int, int] = {}
    for idx, block in enumerate(partition):
        for state in block:
            mapping[state] = idx
    return mapping


def _split_block(
    block: frozenset,
    transitions: Dict[Tuple[int, str], int],
    alphabet: List[str],
    state_to_block: Dict[int, int],
) -> List[frozenset]:
    def signature(s: int) -> tuple:
        sig = []
        for sym in alphabet:
            dest = transitions.get((s, sym))
            if dest is None:
                sig.append(None)
            else:
                sig.append(state_to_block.get(dest))
        return tuple(sig)

    # Agrupar estados por firma
    groups: Dict[tuple, List[int]] = {}
    for s in block:
        sig = signature(s)
        groups.setdefault(sig, []).append(s)

    return [frozenset(g) for g in groups.values()]


# Clase MinimizedDFA

class MinimizedDFA:


    def __init__(self, original_dfa):

        self.alphabet = original_dfa.alphabet
        self.original = original_dfa

        (
            self.states,        # List[frozenset]  — bloques/estados minimizados
            self.transitions,   # Dict[(int,str), int]
            self.accepting,     # Set[int]
            self.start_state,   # int
            self.mapping,       # List[int]  old_state -> new_state
        ) = minimize_dfa(
            original_dfa.states,
            original_dfa.transitions,
            original_dfa.alphabet,
            original_dfa.accepting,
            original_dfa.start_state,
        )

    #Simulación 

    def simulate(self, input_string: str) -> bool:
        """Simula el AFD minimizado con una cadena. Retorna True si acepta."""
        current = self.start_state
        for char in input_string:
            if char not in self.alphabet:
                return False
            nxt = self.transitions.get((current, char))
            if nxt is None:
                return False
            current = nxt
        return current in self.accepting

    def print_transition_table(self):
        """Imprime la tabla de transición del AFD minimizado."""
        print("TABLA DE TRANSICIONES DEL AFD MINIMIZADO")
        header = "Estado   | " + " | ".join(f"{sym:^5}" for sym in self.alphabet)
        print(header)
        print("-" * len(header))

        for i in range(len(self.states)):
            label = f"{i}"
            if i == self.start_state:
                label += " ->"
            if i in self.accepting:
                label += "*"
            row = f"{label:10} |"
            for sym in self.alphabet:
                dest = self.transitions.get((i, sym), "-")
                row += f" {dest:^5} |"
            print(row)

        print("\nLeyenda:")
        print("  -> : Estado inicial")
        print("  * : Estado de aceptación")
        print("  - : Transición no definida (lleva a rechazo)")

    def print_comparison(self):

        orig = self.original

        orig_states = len(orig.states)
        orig_trans  = len(orig.transitions)
        min_states  = len(self.states)
        min_trans   = len(self.transitions)

        delta_s = orig_states - min_states
        delta_t = orig_trans  - min_trans

        print("COMPARACIÓN: AFD DIRECTO  vs  AFD MINIMIZADO")
        print(f"{'':30} {'Directo':>10}   {'Mínimo':>10}   {'Reducción':>10}")
        print("-" * 68)
        print(f"  {'Número de estados':<28} {orig_states:>10}   {min_states:>10}   {delta_s:>+10}")
        print(f"  {'Número de transiciones':<28} {orig_trans:>10}   {min_trans:>10}   {delta_t:>+10}")

        if delta_s == 0 and delta_t == 0:
            print("\n  ✓ El AFD generado por el método directo YA ES MÍNIMO.")
        else:
            print(f"\n  ✓ La minimización redujo {delta_s} estado(s) y {delta_t} transición(ones).")

    
        if delta_s > 0:
            print("\n  Fusión de estados (original -> minimizado):")
            for old, new in enumerate(self.mapping):
                if new != -1:
                    print(f"    Estado {old} -> Bloque {new}")
