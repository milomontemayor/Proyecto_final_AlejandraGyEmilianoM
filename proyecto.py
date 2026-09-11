# ALEJANDRA GARCÍA BARRIO - A01564273
# EMILIANO MONTEMAYOR BURROLA - A01564346

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

        if instruccion == 0:    # HLT
            break

        elif instruccion == 901:   # INP

            if len(entradas) == 0:
                raise ValueError(
                    "Error: no hay más entradas disponibles."
                )

            acumulador = entradas.pop(0)

        elif instruccion == 902:    # OUT
            salidas.append(acumulador)

        elif opcode == 5:    # LDA
            acumulador = memoria[direccion]

        elif opcode == 3:      # STA
            memoria[direccion] = acumulador

        elif opcode == 1:        # ADD
            acumulador = (
                acumulador + memoria[direccion]
            ) % 1000

        elif opcode == 2:      # SUB
            acumulador = acumulador - memoria[direccion]

        elif opcode == 6:     # BRA
            pc = direccion

        elif opcode == 7:    # BRZ
            if acumulador == 0:
                pc = direccion

        elif opcode == 8:     # BRP
            if acumulador >= 0:
                pc = direccion

        elif opcode == 4:      # CALL
            returns.append(pc)
            pc = direccion

        elif instruccion == 999:  # RET

            if len(returns) == 0:
                raise ValueError(
                    "Error: RET se ejecutó con la pila vacía."
                )

            pc = returns.pop()

        else:
            raise ValueError(
                f"Opcode desconocido: {instruccion}"
            )

    return salidas


# ---------------- ENSAMBLADOR ----------------

mnemónicos = {
    "INP": 901,
    "OUT": 902,
    "HLT": 000
}

mnemónicos_direccion = {
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
    direccion = 0  # Dirección de memoria

    for linea in lineas:

        partes = linea.split()

        # Si es que empieza con una etiqueta
        if (
            partes[0].upper() not in mnemónicos
            and partes[0].upper() not in mnemónicos_direccion
            and partes[0].upper() != "DAT"
            and partes[0].upper() != "RET"
        ):

            etiqueta = partes[0].upper()

            if etiqueta in simbolos:

                raise ValueError(
                    f"Error: la etiqueta '{etiqueta}' "
                    "está definida dos veces."
                )

            simbolos[etiqueta] = direccion

            partes = partes[1:]

        # Si después de quitar la etiqueta
        # no queda instrucción
        if len(partes) > 0:

            direccion += 1

            if direccion > 100:

                raise ValueError(
                    "Error: el programa excede "
                    "las 100 casillas."
                )

    # -------- SEGUNDA PASADA --------

    memoria = []

    for linea in lineas:

        partes = linea.split()

        # Revisar si hay etiqueta
        if (
            partes[0].upper() not in mnemónicos
            and partes[0].upper() not in mnemónicos_direccion
            and partes[0].upper() != "DAT"
            and partes[0].upper() != "RET"
        ):

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

                try:
                    codigo = int(partes[1])

                except ValueError:

                    raise ValueError(
                        f"Error: DAT necesita "
                        f"un valor numérico en '{linea}'."
                    )

        # Instrucciones que necesitan dirección
        elif instruccion in mnemónicos_direccion:

            if len(partes) < 2:

                raise ValueError(
                    f"Error: falta el operando "
                    f"en '{linea}'."
                )

            operando = partes[1].upper()

            # Si es una etiqueta
            if operando in simbolos:

                direccion = simbolos[operando]

            else:

                try:
                    direccion = int(operando)

                except ValueError:

                    raise ValueError(
                        f"Error: la etiqueta "
                        f"'{operando}' no está definida."
                    )

            # Revisar que la dirección exista en LMC
            if direccion < 0 or direccion > 99:

                raise ValueError(
                    f"Error: la dirección "
                    f"'{direccion}' debe estar "
                    "entre 0 y 99."
                )

            codigo = (
                mnemónicos_direccion[instruccion]
                + direccion
            )

        else:

            raise ValueError(
                f"Error: mnemónico desconocido "
                f"'{instruccion}'."
            )

        # Revisar que el código quepa
        # en tres dígitos
        if codigo < 0 or codigo > 999:

            raise ValueError(
                f"Error: el valor '{codigo}' "
                "no cabe en 3 dígitos."
            )

        memoria.append(codigo)

    # Rellenar hasta 100 casillas
    while len(memoria) < 100:
        memoria.append(0)

    return memoria, simbolos


# ---------------- PROGRAMA PRINCIPAL ----------------

archivo = "programa1.txt"


try:

    memoria, simbolos = ensamblar(archivo)

    print("Tabla de símbolos:")
    print(simbolos)

    print("\nMemoria:")

    for i in range(100):

        print(
            f"{i:02d},{memoria[i]:03d}"
        )

    # guardar la memoria ensamblada en un archivo

    with open(
        "programa_ensamblado.txt",
        "w"
    ) as f:

        for i in range(100):

            f.write(
                f"{i:02d},{memoria[i]:03d}\n"
            )

    print(
        "\nArchivo "
        "'programa_ensamblado.txt' "
        "creado correctamente..."
    )

    # Pedir entradas al usuario
    entrada_usuario = input(
        "\nEntradas separadas por espacios: "
    )

    if entrada_usuario.strip() == "":

        entradas = []

    else:

        try:

            entradas = [
                int(x)
                for x in entrada_usuario.split()
            ]

        except ValueError:

            raise ValueError(
                "Error: las entradas deben "
                "ser números enteros."
            )

    # Ejecutar el programa
    salidas = ejecutar_lmc_subrutinas(
        memoria,
        entradas
    )

    print("\nSalidas:")
    print(salidas)


except ValueError as e:

    print(e)