"""
main.py - Simulación de operaciones del sistema Software FJ.

Ejecuta operaciones válidas e inválidas sobre clientes, servicios y reservas.
Cada operación se ejecuta de forma protegida: si falla, el error se muestra,
se registra en logs/eventos.log y el programa continúa con la siguiente.
"""
from software_fj.excepciones import SoftwareFJError
from software_fj.gestor import SistemaGestion
from software_fj.logger import ARCHIVO_LOG, registrar_error, registrar_evento

# Resultado de cada operación ejecutada, para el resumen final
RESULTADOS: list = []


def ejecutar_operacion(numero, descripcion, funcion, espera_error=False):
    """Ejecuta `funcion` sin dejar que un error detenga el programa.

    `espera_error` indica si la operación está diseñada para fallar (caso
    inválido); se usa para comprobar en el resumen que todo se comportó como
    se esperaba. Devuelve el resultado de la función o None si falló.
    """
    print(f"\n[{numero:02d}] {descripcion}")
    resultado = None
    tipo = "exito"
    try:
        resultado = funcion()
    except SoftwareFJError as e:
        tipo = "controlado"
        print(f"     [ERROR CONTROLADO] {type(e).__name__}: {e}")
        if e.__cause__ is not None:  # Muestra la excepción original encadenada
            print(f"       Causa: {type(e.__cause__).__name__}: {e.__cause__}")
        registrar_error(f"Operación {numero}: error controlado - {type(e).__name__}: {e}")
    except Exception as e:  # Red de seguridad: nada debe interrumpir la simulación
        tipo = "inesperado"
        print(f"     [ERROR INESPERADO] {type(e).__name__}: {e}")
        registrar_error(f"Operación {numero}: error inesperado - {type(e).__name__}: {e}")
    else:
        print(f"     [OK] {resultado}")
    finally:
        esperado = (tipo == "controlado") if espera_error else (tipo == "exito")
        RESULTADOS.append({"numero": numero, "descripcion": descripcion,
                           "tipo": tipo, "esperado": esperado})
        registrar_evento(f"Operación {numero} finalizada ({tipo}).")
    return resultado


def mostrar_resumen(sistema):
    """Imprime el balance de las operaciones y el estado final del sistema."""
    total = len(RESULTADOS)
    exitosas = sum(1 for r in RESULTADOS if r["tipo"] == "exito")
    controlados = sum(1 for r in RESULTADOS if r["tipo"] == "controlado")
    inesperados = sum(1 for r in RESULTADOS if r["tipo"] == "inesperado")
    esperados = sum(1 for r in RESULTADOS if r["esperado"])

    print("\n" + "=" * 70)
    print("RESUMEN DE LA SIMULACIÓN")
    print("=" * 70)
    print(f"Operaciones ejecutadas: {total}")
    print(f"  Exitosas:            {exitosas}")
    print(f"  Errores controlados: {controlados}")
    print(f"  Errores inesperados: {inesperados}")
    print(f"Comportamiento esperado: {esperados}/{total}")
    for r in RESULTADOS:
        if not r["esperado"]:
            print(f"  ! Operación {r['numero']:02d} no se comportó como se esperaba "
                  f"({r['tipo']}): {r['descripcion']}")

    print("\nClientes registrados:")
    for cliente in sistema.clientes:
        print(f"  - {cliente}")
    print("\nServicios registrados:")
    for servicio in sistema.servicios:
        estado = "disponible" if servicio.disponible else "no disponible"
        print(f"  - [{servicio.id}] {servicio} ({estado})")
    print("\nReservas:")
    for reserva in sistema.reservas:
        print(f"  - {reserva}")

    datos = sistema.resumen()
    print(f"\nTotales: {datos['clientes']} clientes, {datos['servicios']} servicios, "
          f"{datos['reservas']} reservas")
    for estado, cantidad in datos["reservas_por_estado"].items():
        print(f"  {estado}: {cantidad}")
    print(f"\nRegistro de eventos: {ARCHIVO_LOG}")


def main():
    registrar_evento("===== Inicio de la simulación =====")
    sistema = SistemaGestion()

    print("=" * 70)
    print("SOFTWARE FJ - Simulación de operaciones")
    print("=" * 70)

    # ---------- Clientes ----------
    cliente = ejecutar_operacion(
        1, "Registro válido de un cliente",
        lambda: sistema.registrar_cliente({
            "nombre": "Ana María Pérez", "documento": "1012345678",
            "correo": "ana.perez@correo.com", "telefono": "3001234567"}))
    id_cliente = cliente.id if cliente is not None else None

    ejecutar_operacion(
        2, "Registro de un cliente con correo inválido",
        lambda: sistema.registrar_cliente({
            "nombre": "Carlos Gómez", "documento": "80123456",
            "correo": "carlos.gomez@", "telefono": "3109876543"}),
        espera_error=True)

    ejecutar_operacion(
        3, "Registro de un cliente con datos faltantes (sin teléfono)",
        lambda: sistema.registrar_cliente({
            "nombre": "Laura Ríos", "documento": "52123456",
            "correo": "laura.rios@correo.com"}),
        espera_error=True)

    # ---------- Servicios ----------
    ejecutar_operacion(
        4, "Creación válida de una ReservaSala",
        lambda: sistema.crear_servicio(
            "sala", identificador="SAL-01", nombre="Sala Innovación",
            costo_hora=50000, capacidad=10))

    ejecutar_operacion(
        5, "Creación válida de un AlquilerEquipo",
        lambda: sistema.crear_servicio(
            "equipo", identificador="EQU-01", nombre="Portátil",
            costo_dia=80000, stock=5))

    ejecutar_operacion(
        6, "Creación válida de una Asesoria (Ciberseguridad, nivel senior)",
        lambda: sistema.crear_servicio(
            "asesoria", identificador="ASE-01", nombre="Asesoría en ciberseguridad",
            especialidad="Ciberseguridad", nivel="senior", costo_sesion=120000))

    ejecutar_operacion(
        7, "Creación de una Asesoria con parámetros inválidos (nivel 'master')",
        lambda: sistema.crear_servicio(
            "asesoria", identificador="ASE-02", nombre="Asesoría en desarrollo web",
            especialidad="Desarrollo web", nivel="master", costo_sesion=100000),
        espera_error=True)

    # ---------- Reservas ----------
    def reservar_y_confirmar():
        nueva = sistema.crear_reserva(id_cliente, "SAL-01", 3, asistentes=8)
        sistema.confirmar_reserva(nueva.id)
        return nueva

    reserva = ejecutar_operacion(
        8, "Reserva exitosa y confirmada (sala, 3 horas, 8 asistentes)",
        reservar_y_confirmar)
    id_reserva = reserva.id if reserva is not None else None

    def reservar_asesoria():
        # El costo se calcula con la fórmula propia de Asesoria (polimorfismo)
        nueva = sistema.crear_reserva(id_cliente, "ASE-01", 2)
        costo = sistema.calcular_costo_reserva(nueva.id, impuesto=0.19)
        return f"{nueva} | Costo con IVA: ${costo:,.2f}"

    ejecutar_operacion(
        9, "Reserva exitosa de una Asesoria (senior, 2 sesiones)",
        reservar_asesoria)

    ejecutar_operacion(
        10, "Reserva con duración negativa (equipo, -2 días)",
        lambda: sistema.crear_reserva(id_cliente, "EQU-01", -2),
        espera_error=True)

    def reservar_servicio_desactivado():
        sistema.cambiar_disponibilidad_servicio("EQU-01", False)
        return sistema.crear_reserva(id_cliente, "EQU-01", 2, cantidad=1)

    ejecutar_operacion(
        11, "Reserva sobre un servicio no disponible (equipo desactivado)",
        reservar_servicio_desactivado,
        espera_error=True)

    def calcular_variantes():
        # Sobrecarga simulada: el mismo método con 0, 1 o 2 parámetros opcionales
        base = sistema.calcular_costo_reserva(id_reserva)
        con_iva = sistema.calcular_costo_reserva(id_reserva, impuesto=0.19)
        con_descuento = sistema.calcular_costo_reserva(
            id_reserva, impuesto=0.19, descuento=0.10)
        return (f"Base: ${base:,.2f} | Con IVA: ${con_iva:,.2f} | "
                f"Con IVA y 10 % de descuento: ${con_descuento:,.2f}")

    ejecutar_operacion(
        12, "Cálculo de costo con impuesto y descuento",
        calcular_variantes)

    def procesar():
        total = sistema.procesar_reserva(id_reserva)
        return f"{id_reserva} procesada. Total cobrado: ${total:,.2f}"

    ejecutar_operacion(
        13, "Procesamiento exitoso de una reserva",
        procesar)

    ejecutar_operacion(
        14, "Cancelación de una reserva ya procesada",
        lambda: sistema.cancelar_reserva(id_reserva),
        espera_error=True)

    mostrar_resumen(sistema)
    registrar_evento("===== Fin de la simulación =====")


if __name__ == "__main__":
    main()
