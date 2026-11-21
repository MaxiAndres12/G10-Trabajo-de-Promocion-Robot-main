from dataclasses import dataclass
from typing import List, Optional, Tuple
from automata.pda.dpda import DPDA
from automata.base.exceptions import RejectionException

ENTRADA_A_SIMBOLO = {
    "arriba": "a",
    "abajo": "b",
    "derecha": "d",
    "izquierda": "i",
    "viaje": "V",
    "agarrar": "A",
    "soltar": "S",
    "finviaje": "F",
}

SIMBOLOS_PILA = {"Z", "a", "b", "d", "i"}

@dataclass
class PasoAP:
    indice: int
    entrada: str
    estado: str
    pila: str
    altura_pila: int

@dataclass
class ResultadoAP:
    aceptado: bool
    pasos: List[PasoAP]
    altura_max_pila: int
    mensaje: str


"verifica los espacios, saltos de linea y cada palabra de entrada sea valida"
def validarLenguaje(texto: str) -> Tuple[Optional[List[str]], Optional[str]]:
    entrada: List[str] = []
    indice = 0

    for nro_linea, linea in enumerate(texto.splitlines(), start = 1):
        for palabra in linea.split():
            indice += 1
            if palabra not in ENTRADA_A_SIMBOLO:
                return (
                    None,
                    f"Error en el lengueje #{indice} (linea {nro_linea})"
                    f"'{palabra}' no es una instruccion valida.",
                )
            entrada.append(palabra)
    return entrada, None

def construirAp() -> DPDA:
    trancisiones_q1 = {
        "a": {top: ("q1", ("a", top)) for top in SIMBOLOS_PILA},
        "b": {top: ("q1", ("b", top)) for top in SIMBOLOS_PILA},
        "d": {top: ("q1", ("d", top)) for top in SIMBOLOS_PILA},
        "i": {top: ("q1", ("i", top)) for top in SIMBOLOS_PILA},
        "A": {top: ("q2", (top,)) for top in SIMBOLOS_PILA},
    }

    return DPDA(
        states= {"q0", "q1", "q2", "q3", "q4"},
        input_symbols= set(ENTRADA_A_SIMBOLO.values()),
        stack_symbols= SIMBOLOS_PILA,
        transitions= {
            "q0": {
                "a": {"Z": ("q0", ("Z",))},
                "b": {"Z": ("q0", ("Z",))},
                "d": {"Z": ("q0", ("Z",))},
                "i": {"Z": ("q0", ("Z",))},
                "V": {"Z": ("q1", ("Z",))},
            },
            "q1": trancisiones_q1,
            "q2": {
                "a": {"b": ("q2", "")},
                "b": {"a": ("q2", "")},
                "d": {"i": ("q2", "")},
                "i": {"d": ("q2", "")},
                "S": {"Z": ("q3", ("Z",))},
            },
            "q3": {
                "F": {"Z": ("q4", ("Z",))},
            },
            "q4": {
                "a": {"Z": ("q4", ("Z",))},
                "b": {"Z": ("q4", ("Z",))},
                "d": {"Z": ("q4", ("Z",))},
                "i": {"Z": ("q4", ("Z",))},
                "V": {"Z": ("q1", ("Z",))},
            },
        },
        initial_state= "q0",
        initial_stack_symbol= "Z",
        final_states= {"q4"},
        acceptance_mode= "final_state",
    )

def resetPila(pda_stack) -> Tuple[str, int]:
    elementos = getattr(pda_stack, "stack", tuple(pda_stack))
    pila_str = "".join(reversed(elementos))
    altura = max(0, len(elementos) - 1)
    return pila_str, altura

def reconocerAp(entradas: List[str]) -> ResultadoAP:
    ap = construirAp()
    cadena = "".join(ENTRADA_A_SIMBOLO[t] for t in entradas)

    pasos: List[PasoAP] = []
    altura_max = 0
    ultimo_estado = "q0"
    ultima_pila = "Z"

    try:
        for paso_idx, config in enumerate(ap.read_input_stepwise(cadena)):
            pila_str, altura = resetPila(config.stack)
            ultimo_estado = config.state
            ultima_pila = pila_str

            if paso_idx == 0:
                continue
            
            altura_max = max(altura_max, altura)
            pasos.append(
                PasoAP(
                    indice = paso_idx,
                    entrada = entradas[paso_idx - 1],
                    estado = config.state,
                    pila = pila_str,
                    altura_pila = altura,
                )
            )

        return ResultadoAP(
            aceptado = True,
            pasos = pasos,
            altura_max_pila = altura_max,
            mensaje = "Cadena aceptada por el AP."
        )

    except RejectionException: 
        if len(entradas) == 0:
            mensaje = "Rechazo del AP por entrada vacia."
        elif len(pasos) < len(entradas):
            idx_falla = len(pasos) + 1
            ent_falla = entradas[len(pasos)]
            mensaje = (f"Rechazo del AP en entrada #{idx_falla} ('{ent_falla}'): "
                        f"Sin transicion desde estado {ultimo_estado} con pila '{ultima_pila}'"
                        )
        else:
            mensaje = (
                f"Rechazo del AP al finalizar la entrada: termino en estado"
                f"{ultimo_estado} no final con pila '{ultima_pila}'"
            )

        return ResultadoAP(
            aceptado = False,
            pasos = pasos,
            altura_max_pila = altura_max,
            mensaje = mensaje,
        )