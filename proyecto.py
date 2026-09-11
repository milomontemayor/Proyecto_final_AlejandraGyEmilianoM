# ALEJANDRA GARCÍA BARRIO - A01564273
# EMILIANO MONTEMAYOR BURROLA - 

import sys

def ejecutar_lmc_subrutinas(memoria: list, entradas: list) -> list:
    memoria = list(memoria)
    pc = 0
    acumulador = 0
    salidas = []
    entradas = list(entradas)

    returns = []

    while True:
        instruccion = memoria[pc]
        opcode = instruccion // 100
        direccion = instruccion % 100
        pc += 1
        if instruccion == 0:                 # HLT
            break

        elif instruccion == 901:             # INP
            acumulador = entradas.pop(0)

        elif instruccion == 902:             # OUT
            salidas.append(acumulador)

        elif opcode == 5:                    # LDA
            acumulador = memoria[direccion]

        elif opcode == 3:                    # STA
            memoria[direccion] = acumulador

        elif opcode == 1:                    # ADD
            acumulador = (acumulador + memoria[direccion]) % 1000

        elif opcode == 2:                    # SUB
            acumulador = acumulador - memoria[direccion]

        elif opcode == 6:                    # BRA
            pc = direccion

        elif opcode == 7:                    # BRZ
            if acumulador == 0:
                pc = direccion

        elif opcode == 8:                    # BRP
            if acumulador >= 0:
                pc = direccion

        elif opcode == 4:                    # CALL
            returns.append(pc)
            pc = direccion

        elif instruccion == 999:             # RET
            pc = returns.pop()

        else:
            raise ValueError(f"Opcode desconocido: {instruccion}")

    return salidas


# ---------------- ENSAMBLADOR ----------------

mnemónicos = {
    "INP": 901, 
    "OUT": 902, 
    "HLT": 000
    }

mnemónicos_a_direccion = {
    "LDA": 500,
    "STA": 300,
    "ADD": 100,
    "SUB": 200,
    "BRA": 600,
    "BRZ": 700,
    "BRP": 800,
    "CALL": 400
}


def ensamblar(archivo):
    lineas = []

    # Leer el archivo
    with open(archivo, "r") as f:
        for linea in f:
            # Ignorar comentarios
            linea = linea.split("//")[0]
            linea = linea.split("#")[0]
            # Quitar espacios
            linea = linea.strip()
            # Ignorar líneas en blanco
            if linea != "":
                lineas.append(linea)

    # -------- PRIMERA PASADA --------

    simbolos = {} # Etiquetas
    direccion = 0 # Dirección de Memoria

    for linea in lineas:

        partes = linea.split() #Separa Usando Espacios

        # Si empieza con una etiqueta
        if partes[0].upper() not in mnemónicos and partes[0].upper() not in mnemónicos_direccion and partes[0].upper() != "DAT" and partes[0].upper() != "RET":

            etiqueta = partes[0].upper()

            if etiqueta in simbolos:
                raise ValueError(f"Error: la etiqueta '{etiqueta}' está definida dos veces.")

            simbolos[etiqueta] = direccion

            partes = partes[1:]

        # Si después de quitar la etiqueta no queda instrucción
        if len(partes) > 0:
            direccion += 1

            if direccion > 100:
                raise ValueError("Error: el programa excede las 100 casillas.")

    # -------- SEGUNDA PASADA --------

    memoria = []

    for linea in lineas:

        partes = linea.split()

        # Revisar si hay etiqueta
        if partes[0].upper() not in mnemónicos and partes[0].upper() not in mnemónicos_direccion and partes[0].upper() != "DAT" and partes[0].upper() != "RET":
            partes = partes[1:]

        if len(partes) == 0:
            continue

        instruccion = partes[0].upper()

        # INP, OUT y HLT
        if instruccion in mnemónicos:
            codigo = mnemónicos[instruccion]

        # RET
        elif instruccion == "RET":
            codigo = 999

        # DAT
        elif instruccion == "DAT":

            if len(partes) == 1:
                codigo = 0
            else:
                codigo = int(partes[1])

        # Instrucciones que necesitan dirección
        elif instruccion in mnemónicos_direccion:

            if len(partes) < 2:
                raise ValueError(f"Error: falta el operando en '{linea}'.")

            operando = partes[1].upper()

            # Si es una etiqueta
            if operando in simbolos:
                direccion = simbolos[operando]

            else:
                try:
                    direccion = int(operando)
                except:
                    raise ValueError(
                        f"Error: la etiqueta '{operando}' no está definida."
                    )

            codigo = mnemónicos_direccion[instruccion] + direccion

        else:
            raise ValueError(
                f"Error: mnemónico desconocido '{instruccion}'."
            )

        if codigo < 0 or codigo > 999:
            raise ValueError(
                f"Error: el valor '{codigo}' no cabe en 3 dígitos."
            )

        memoria.append(codigo)

    # Rellenar hasta 100 casillas
    while len(memoria) < 100:
        memoria.append(0)

    return memoria, simbolos


# ---------------- PROGRAMA PRINCIPAL ----------------

if len(sys.argv) < 2:
    print("Uso: python ensamblador.py programa.txt")
    sys.exit()

archivo = sys.argv[1]

try:
    memoria, simbolos = ensamblar(archivo)

    print("Tabla de símbolos:")
    print(simbolos)

    print("\nMemoria:")
    for i in range(100):
        print(f"{i:02d},{memoria[i]:03d}")

    # Ejecutar el programa
    entradas = [5]

    salidas = ejecutar_lmc_subrutinas(memoria, entradas)

    print("\nSalidas:")
    print(salidas)

except ValueError as e:
    print(e)