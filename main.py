import sys
from pathlib import Path
from simulador import (
    CAJAS_INICIALES,
    ROBOT_INICIAL,
    ejecutarPrograma,
    exportarRegistroCSV,
    resertGrilla,
)

PROGRAMA = """
derecha derecha derecha derecha derecha
viaje
arriba arriba arriba
agarrar
abajo abajo abajo
soltar
finviaje
arriba izquierda
viaje
arriba arriba arriba arriba
agarrar
abajo abajo abajo abajo
soltar
finviaje
arriba izquierda
viaje
izquierda arriba arriba
agarrar
abajo abajo derecha
soltar
finviaje
izquierda arriba
viaje
izquierda izquierda arriba arriba
agarrar
abajo abajo derecha derecha
soltar
finviaje
izquierda izquierda abajo abajo abajo
""".strip()

PRUEBAS = [
    ("1. Solución completa correcta (Grupo 10)", PROGRAMA, "COMPLETADA"),
    ("2. Regreso con orden que no es inversa", "viaje arriba agarrar izquierda soltar finviaje", "RECHAZO_AP"),
    ("3. soltar antes de terminar el regreso", "viaje arriba arriba agarrar abajo soltar finviaje", "RECHAZO_AP"),
    ("4. Viaje sin cierre finviaje", "viaje arriba agarrar abajo soltar", "RECHAZO_AP"),
    ("5. Segundo agarrar en el mismo viaje", "viaje arriba agarrar agarrar abajo soltar finviaje", "RECHAZO_AP"),
    ("6. Aceptado por AP, intenta atravesar obstáculo (5,3)", "viaje derecha derecha arriba agarrar abajo izquierda izquierda soltar finviaje", "ERROR_FISICO"),
    ("7. Aceptado por AP, intenta agarrar en celda vacía (5,1)", "viaje arriba agarrar abajo soltar finviaje", "ERROR_FISICO"),
    ("8. Aceptado y ejecutable, pero no alcanza la meta", "derecha derecha derecha derecha derecha viaje arriba arriba arriba agarrar abajo abajo abajo soltar finviaje", "OBJETIVO_NO_ALCANZADO"),
    ("9. Borde: token desconocido", "derecha saltar viaje arriba agarrar abajo soltar finviaje", "ERROR_ENTRADA"),
    ("10. Borde: entrada vacía", "", "RECHAZO_AP"),
    ("11. Borde: salida de la grilla (6,0)", "viaje izquierda agarrar derecha soltar finviaje", "ERROR_FISICO"),
]

def ejecutarArchivo(ruta_txt: str, ruta_csv: str = "registro_ejecucion.csv") -> None:
    contenido = Path(ruta_txt).read_text(encoding="utf-8")
    res = ejecutarPrograma(contenido)

    print("=== GRILLA INICIAL ===")
    print(resertGrilla(ROBOT_INICIAL, CAJAS_INICIALES))
    print(f"\nResultado: {res.categoria}")
    print(f"Detalle: {res.mensaje}")

    if res.registros:
        exportarRegistroCSV(res.registros, ruta_csv)
        print(f"Movimientos sin carga: {res.mov_sin_carga}")
        print(f"Movimientos con carga: {res.mov_con_carga}")
        print(f"Altura maxima de pila: {res.altura_max_pila}")
        print(f"Registro exportado: {ruta_csv}")
        print("\n === GRILLA FINAL ===")
        print(resertGrilla(res.posicion_final, res.cajas_finales))

def ejecutarPruebas()-> None:
    print("=== PRUEBAS ===")
    aprobadas = 0 
    
    for nombre, entrada, esperado in PRUEBAS:
        res = ejecutarPrograma(entrada)
        ok = res.categoria == esperado
        aprobadas += int(ok)
        estado_str = "ok" if ok else "no cumple"
        print(f"[{estado_str}] {nombre}")
        print(f"Esperando: {esperado} | obtenido: {res.categoria}")
        print(f"Detalle: {res.mensaje}\n")

        if nombre.startswith("1.") and res.registros:
            exportarRegistroCSV(res.registros, "registro_solucion.csv")
            print("=== GRILLA INICIAL ===")
            print(resertGrilla(ROBOT_INICIAL, CAJAS_INICIALES))
            print("\n=== GRILLA FINAL ===")
            print(resertGrilla(res.posicion_final, res.cajas_finales))
            print(
                f"\nMétricas solución -> Sin carga: {res.mov_sin_carga} | "
                f"Con carga: {res.mov_con_carga} | "
                f"Altura máx. pila (sin Z): {res.altura_max_pila}\n"
            )
    print(f"Total: {aprobadas}/{len(PRUEBAS)} pruebas coinciden con el resultado esperado.")

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        csv_salida = sys.argv[2] if len(sys.argv) >= 3 else "registro_ejecucion.csv"
        ejecutarArchivo(sys.argv[1], csv_salida)
    else:
        ejecutarPruebas()