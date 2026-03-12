import sys
from dfa_builder import build_dfa_from_regex, print_transition_table


def show_dfa_table(dfa):
    """Muestra la tabla de transición de forma clara y legible."""
    print_transition_table(
        dfa.states,
        dfa.transitions,
        dfa.alphabet,
        dfa.accepting,
        dfa.start_state,
        dfa.symbols,
    )


def evaluate_string(dfa, candidate: str) -> bool:
    """Evalúa una cadena y muestra ACEPTA/RECHAZA."""
    result = dfa.simulate(candidate)
    print(f"Resultado: {'ACEPTA' if result else 'RECHAZA'}")
    return result


def run_required_demo():
    """Corre las 3 expresiones del README con casos válidos e inválidos."""
    demo_data = [
        {
            "regex": "(a|b)*abb",
            "tests": [
                ("abb", True),
                ("aabb", True),
                ("ab", False),
            ],
        },
        {
            "regex": "a+b?c",
            "tests": [
                ("ac", True),
                ("abc", True),
                ("bc", False),
            ],
        },
        {
            "regex": "(a|b)+c*(d?)",
            "tests": [
                ("acd", True),
                ("bc", True),
                ("cd", False),
            ],
        },
    ]

    print("=" * 72)
    print("DEMO OFICIAL — Lab 01 (Persona 3)")
    print("=" * 72)

    for index, case in enumerate(demo_data, start=1):
        regex = case["regex"]
        print(f"\n[{index}] Regex: {regex}")
        dfa = build_dfa_from_regex(regex)

        show_dfa_table(dfa)

        print("Pruebas de cadenas:")
        for candidate, expected in case["tests"]:
            result = dfa.simulate(candidate)
            expected_label = "ACEPTA" if expected else "RECHAZA"
            actual_label = "ACEPTA" if result else "RECHAZA"
            ok_mark = "✓" if result == expected else "✗"
            print(f"  {ok_mark} '{candidate}' -> {actual_label} (esperado: {expected_label})")


def run_interactive_mode():
    """Permite construir AFD y probar cadenas de forma interactiva."""
    print("=" * 72)
    print("SIMULADOR DE AFD — Lab 01")
    print("Operadores soportados: |  *  +  ?  y paréntesis")
    print("Escribe 'salir' para terminar")
    print("=" * 72)

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
            dfa = build_dfa_from_regex(regex)
        except ValueError as error:
            print(f"Error en la regex: {error}")
            continue

        print("\nTabla de transición del AFD:")
        show_dfa_table(dfa)

        print("\nAhora prueba cadenas contra este AFD.")
        print("Deja la cadena vacía y presiona Enter para ingresar otra regex.")

        while True:
            try:
                candidate = input("Cadena: ")
            except (EOFError, KeyboardInterrupt):
                print("\nRegresando al ingreso de regex...")
                break

            if candidate == "":
                break

            evaluate_string(dfa, candidate)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        run_required_demo()
    else:
        run_interactive_mode()
