import csv
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple
from ap_robot import PasoAP, reconocerAp, validarLenguaje

Coord = Tuple[int, int]

FILAS = 6
COLUMNAS = 6
ROBOT_INICIAL: Coord = (6, 1)
ROBOT_FINAL: Coord = (6, 1)
CAJAS_INICIALES: Set[Coord] = {(1, 1), (1, 5), (2, 3), (3, 6)}
OBSTACULOS: Set[Coord] = {(2, 2), (2, 4), (3, 4), (5, 3)}
DESTINOS: Set[Coord] = {(3, 3), (4, 4), (5, 5), (6, 6)}

DELTAS: Dict[str, Coord] = {
    "arriba": (-1, 0),
    "abajo": (1, 0),
    "izquierda": (0, -1),
    "derecha": (0, 1),
}

@dataclass
class RegistroPaso:
    indice: int
    orden: str
    estado_ap: str
    pila: str
    posicion: Coord
    carga: bool

@dataclass
class ResultadoEjecucion:
    categoria: str
    mensaje: str
    registros: List[RegistroPaso]
    mov_sin_carga: int = 0
    mov_con_carga: int = 0
    altura_max_pila: int = 0
    posicion_final: Coord = ROBOT_INICIAL
    carga_final: bool = False
    cajas_finales: Set[Coord] = None

def resertGrilla(posicion_robot: Coord, cajas: Set[Coord]) -> str:
    encabezado = " " + " ".join(f"{c}" for c in range(1, COLUMNAS + 1))
    separador = " " + " " * COLUMNAS
    lineas = [encabezado, separador]

    for f in range(1, FILAS + 1):
        celdas = []
        for c in range(1, COLUMNAS + 1):
            coord = (f, c)
            if coord in OBSTACULOS:
                marca = "X"
            elif coord == posicion_robot and coord in cajas:
                marca = "R/C"
            elif coord == posicion_robot:
                marca = "R"
            elif coord in cajas and coord in DESTINOS:
                marca = "C*"
            elif coord in cajas:
                marca = "C"
            elif coord in DESTINOS:
                marca = "T"
            else:
                marca = "."
            celdas.append(marca)
        lineas.append(f"{f} | " + "|".join(f"{m:^4}" for m in celdas) + "|")
        lineas.append(separador)
    
    return "\n".join(lineas)

def ejecutarPrograma(texto_programa: str) -> ResultadoEjecucion:
    entradas, error_entrada = validarLenguaje(texto_programa)
    if error_entrada is not None:
        return ResultadoEjecucion(
            categoria="ERROR_ENTRADA",
            mensaje= error_entrada,
            registros=[],
            cajas_finales= set(CAJAS_INICIALES),
        )

    res_ap = reconocerAp(entradas)
    if not res_ap.aceptado:
        return ResultadoEjecucion(
            categoria= "RECHAZO_AP",
            mensaje= res_ap.mensaje,
            registros=[],
            altura_max_pila= res_ap.altura_max_pila,
            cajas_finales= set(CAJAS_INICIALES),
        )

    pos = ROBOT_INICIAL
    carga = False
    cajas = set(CAJAS_INICIALES)
    registros: List[RegistroPaso] = []
    mov_sin_carga = 0
    mov_con_carga = 0

    for paso in res_ap.pasos:
        orden = paso.entrada

        if orden in DELTAS:
            df, dc = DELTAS[orden]
            nueva_pos = (pos[0] + df, pos[1] + dc)

            if not (1 <= nueva_pos[0] <= FILAS and 1 <= nueva_pos[1] <= COLUMNAS):
                return ResultadoEjecucion(
                    categoria= "ERROR_FISICO",
                    mensaje= f"Error en la entrada #{paso.indice} ('{orden}'):"
                             f"salida de grilla al intentar ir a {nueva_pos}",
                    registros= registros,
                    mov_sin_carga= mov_sin_carga,
                    mov_con_carga= mov_con_carga,
                    altura_max_pila= res_ap.altura_max_pila,
                    posicion_final= pos,
                    carga_final= carga,
                    cajas_finales= cajas,
                )
            if nueva_pos in OBSTACULOS:
                return ResultadoEjecucion(
                    categoria= "ERROR_FISICO",
                    mensaje= f"Error físico en entrada #{paso.indice} ('{orden}'): "
                            f"colisión con obstáculo en {nueva_pos}.",
                    registros= registros,
                    mov_sin_carga= mov_sin_carga,
                    mov_con_carga= mov_con_carga,
                    altura_max_pila= res_ap.altura_max_pila,
                    posicion_final= pos,
                    carga_final= carga,
                    cajas_finales= cajas,
                )

            pos = nueva_pos
            if carga:
                mov_con_carga += 1
            else:
                mov_sin_carga += 1

        elif orden == "agarrar":
            if carga:
                return ResultadoEjecucion(
                    categoria= "ERROR_FISICO",
                    mensaje= f"Error físico en entrada #{paso.indice} ('agarrar'): la pinza ya lleva carga.",
                    registros= registros,
                    mov_sin_carga= mov_sin_carga,
                    mov_con_carga= mov_con_carga,
                    altura_max_pila= res_ap.altura_max_pila,
                    posicion_final= pos,
                    carga_final= carga,
                    cajas_finales= cajas,
                )
            if pos not in cajas:
                return ResultadoEjecucion(
                    categoria= "ERROR_FISICO",
                    mensaje=f"Error físico en entrada #{paso.indice} ('agarrar'): no hay caja en {pos}.",
                    registros= registros,
                    mov_sin_carga= mov_sin_carga,
                    mov_con_carga= mov_con_carga,
                    altura_max_pila= res_ap.altura_max_pila,
                    posicion_final= pos,
                    carga_final= carga,
                    cajas_finales= cajas,
                )
            cajas.remove(pos)
            carga = True
            
        elif orden == "soltar":
            if not carga:
                return ResultadoEjecucion(
                   categoria= "ERROR_FISICO",
                    mensaje=f"Error físico de entrada #{paso.indice} ('soltar'): la pinza está vacía.",
                    registros= registros,
                    mov_sin_carga= mov_sin_carga,
                    mov_con_carga= mov_con_carga,
                    altura_max_pila= res_ap.altura_max_pila,
                    posicion_final= pos,
                    carga_final= carga,
                    cajas_finales= cajas, 
                )
            if pos in cajas:
                return ResultadoEjecucion(
                    categoria= "ERROR_FISICO",
                    mensaje=f"Error físico de entrada #{paso.indice} ('soltar'): ya existe una caja en {pos}.",
                    registros= registros,
                    mov_sin_carga= mov_sin_carga,
                    mov_con_carga= mov_con_carga,
                    altura_max_pila= res_ap.altura_max_pila,
                    posicion_final= pos,
                    carga_final= carga,
                    cajas_finales= cajas,
                )
            cajas.add(pos)
            carga = False

        registros.append(
            RegistroPaso(
                indice= paso.indice,
                orden= orden,
                estado_ap= paso.estado,
                pila= paso.pila,
                posicion= pos,
                carga= carga,
            )
        )
    
    if cajas == DESTINOS and pos == ROBOT_FINAL and not carga:
        return ResultadoEjecucion(
            categoria="COMPLETADA",
            mensaje="Problema resuelto: todas las cajas están en destino y el robot regresó a (6,1) vacío.",
            registros=registros,
            mov_sin_carga=mov_sin_carga,
            mov_con_carga=mov_con_carga,
            altura_max_pila=res_ap.altura_max_pila,
            posicion_final=pos,
            carga_final=carga,
            cajas_finales=cajas,
        )

    return ResultadoEjecucion(
       categoria="OBJETIVO_NO_ALCANZADO",
        mensaje=f"Objetivo no alcanzado: robot en {pos} (carga={carga}), cajas en {sorted(cajas)}.",
        registros=registros,
        mov_sin_carga=mov_sin_carga,
        mov_con_carga=mov_con_carga,
        altura_max_pila=res_ap.altura_max_pila,
        posicion_final=pos,
        carga_final=carga,
        cajas_finales=cajas, 
    )

def exportarRegistroCSV(registros: List[RegistroPaso], ruta_csv: str) -> None:
    with open(ruta_csv, mode="w", newline="", encoding="utf-8") as archivo:
        writer = csv.writer(archivo)
        writer.writerow(["indice", "orden", "estado_ap", "pila", "posicion", "carga"])
        for reg in registros:
            writer.writerow([
                reg.indice,
                reg.orden,
                reg.estado_ap,
                reg.pila,
                f"({reg.posicion[0]},{reg.posicion[1]})",
                "con_carga" if reg.carga else "sin_carga",
            ])