import sys
from dfa_builder import build_dfa_from_regex, print_transition_table
from minimizer import MinimizedDFA


#Helpers 
def show_original_table(dfa):
    print_transition_table(
        dfa.states,
        dfa.transitions,
        dfa.alphabet,
        dfa.accepting,
        dfa.start_state,
        dfa.symbols,
    )


def build_and_minimize(regex: str):
    """
    Construye el AFD directo y su versión minimizada.
    Retorna (dfa, min_dfa).
    """
    dfa = build_dfa_from_regex(regex)
    min_dfa = MinimizedDFA(dfa)
    return dfa, min_dfa


# ─── Demo requerida ──────────────────────────────────────────────────────────

def run_required_demo():
    """
    Demo oficial del Lab 02.

    Requisito del enunciado:
      • Una regex cuyo AFD directo YA SEA mínimo.
      • Una regex cuyo AFD directo NO sea mínimo (se reduce al minimizar).
    """
    demo_data = [
        {
            # Este AFD directo ya es mínimo (ab tiene 3 estados y ninguno
            # es equivalente a otro).
            "regex": "ab",
            "tests": [("ab", True), ("a", False), ("b", False)],
            "note": "AFD directo ya mínimo",
        },
        {
            # a(ba)* — el AFD directo produce un estado redundante que
            # el algoritmo de minimización fusiona, reduciendo de 3 a 2 estados.
            "regex": "a(ba)*",
            "tests": [("a", True), ("aba", True), ("ababa", True), ("ab", False), ("ba", False)],
            "note": "AFD directo que se reduce al minimizar",
        },
    ]

    print("=" * 72)
    print("DEMO OFICIAL — Lab 02  (Minimización de un AFD)")
    print("=" * 72)

    for idx, case in enumerate(demo_data, start=1):
        regex = case["regex"]
        note  = case["note"]

        print(f"\n{'─' * 72}")
        print(f"[{idx}] Regex: {regex}   ({note})")
        print(f"{'─' * 72}")

        dfa, min_dfa = build_and_minimize(regex)

        # ── Tabla AFD directo ────────────────────────────────────────────────
        print("\n[Paso 1] AFD generado con el método directo:")
        show_original_table(dfa)

        # ── Tabla AFD minimizado ─────────────────────────────────────────────
        print("\n[Paso 2] AFD minimizado:")
        min_dfa.print_transition_table()

        # ── Comparación ──────────────────────────────────────────────────────
        print(f"\n[Paso 3] Comparación:")
        min_dfa.print_comparison()

        # ── Simulación con el AFD minimizado ─────────────────────────────────
        print(f"\n[Paso 4] Simulación con el AFD minimizado:")
        for candidate, expected in case["tests"]:
            result   = min_dfa.simulate(candidate)
            expected_lbl = "ACEPTA" if expected else "RECHAZA"
            actual_lbl   = "ACEPTA" if result   else "RECHAZA"
            mark = "✓" if result == expected else "✗"
            print(f"  {mark} '{candidate}' -> {actual_lbl}  (esperado: {expected_lbl})")


# ─── Modo interactivo ────────────────────────────────────────────────────────

def run_interactive_mode():
    print("=" * 72)
    print("SIMULADOR DE AFD CON MINIMIZACIÓN — Lab 02")
    print("Operadores soportados:  |  *  +  ?  y paréntesis")
    print("Escribe 'salir' para terminar.\n")
    while True:
        try:
            regex = input("\nIngresa una regex: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo...")
            break

        if regex.lower() in {"salir", "exit", "quit"}:
            print("Saliendo...")
            break
        if not regex:
            continue

        try:
            dfa, min_dfa = build_and_minimize(regex)
        except ValueError as err:
            print(f"Error en la regex: {err}")
            continue

        # 1. Tabla AFD directo
        print("\n AFD")
        show_original_table(dfa)

        # 2. Tabla AFD minimizado
        print("\nAFD minimizado")
        min_dfa.print_transition_table()

        # 3. Comparación
        print()
        min_dfa.print_comparison()

        print("Deja la cadena vacía para ingresar otra regex.\n")

        while True:
            try:
                candidate = input("Cadena: ")
            except (EOFError, KeyboardInterrupt):
                print("\nRegresando...")
                break

            if candidate == "":
                break

            result = min_dfa.simulate(candidate)
            print(f"Resultado: {'ACEPTA' if result else 'RECHAZA'}")


# Entry-point 

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        run_required_demo()
    else:
        run_required_demo()
        print("Modo interactivo  (Ctrl+C para salir)")
        run_interactive_mode()