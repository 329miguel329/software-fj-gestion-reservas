"""
gestor.py - SistemaGestion de Software FJ.

Mantiene en memoria las listas de clientes, servicios y reservas, y coordina
las operaciones entre ellos. Cada operación registra en el log su resultado
y deja que las excepciones personalizadas lleguen a quien la llamó.
"""
from .cliente import Cliente
from .servicios import Servicio, ReservaSala, AlquilerEquipo, Asesoria
from .reserva import Reserva
from .excepciones import (
    SoftwareFJError,
    ClienteInvalidoError,
    ServicioInvalidoError,
    ServicioNoDisponibleError,
    ReservaInvalidaError,
    OperacionNoPermitidaError,
)
from .logger import registrar_evento, registrar_error


class SistemaGestion:
    """Gestor central: guarda las entidades y coordina las operaciones."""

    # Tipos de servicio que se pueden crear con crear_servicio()
    TIPOS_SERVICIO = {
        "sala": ReservaSala,
        "equipo": AlquilerEquipo,
        "asesoria": Asesoria,
    }

    def __init__(self) -> None:
        self._clientes: list = []
        self._servicios: list = []
        self._reservas: list = []
        registrar_evento("Sistema de gestión iniciado.")

    # ---------- Listas internas (solo lectura desde fuera) ----------
    @property
    def clientes(self) -> tuple:
        return tuple(self._clientes)

    @property
    def servicios(self) -> tuple:
        return tuple(self._servicios)

    @property
    def reservas(self) -> tuple:
        return tuple(self._reservas)

    # ---------- Búsquedas ----------
    def buscar_cliente(self, id_cliente: str) -> Cliente:
        for cliente in self._clientes:
            if cliente.id == id_cliente:
                return cliente
        registrar_error(f"Gestor: cliente {id_cliente} no encontrado.")
        raise ClienteInvalidoError("id", f"No existe un cliente con id {id_cliente}.")

    def buscar_servicio(self, id_servicio: str) -> Servicio:
        for servicio in self._servicios:
            if servicio.id == id_servicio:
                return servicio
        registrar_error(f"Gestor: servicio {id_servicio} no encontrado.")
        raise ServicioNoDisponibleError(f"No existe un servicio con id {id_servicio}.")

    def buscar_reserva(self, id_reserva: str) -> Reserva:
        for reserva in self._reservas:
            if reserva.id == id_reserva:
                return reserva
        registrar_error(f"Gestor: reserva {id_reserva} no encontrada.")
        raise ReservaInvalidaError(f"No existe una reserva con id {id_reserva}.")

    # ---------- Clientes ----------
    def registrar_cliente(self, datos: dict) -> Cliente:
        """Crea un cliente a partir de un diccionario y lo agrega al sistema."""
        try:
            if isinstance(datos, dict):
                documento = str(datos.get("documento") or "").strip()
                if any(c.documento == documento for c in self._clientes):
                    raise OperacionNoPermitidaError(
                        f"Ya existe un cliente con documento {documento}.")
            cliente = Cliente.desde_diccionario(datos)  # Valida y encadena sus propios errores
        except SoftwareFJError as e:
            registrar_error(f"Gestor: cliente no registrado - {e}")
            raise
        else:
            self._clientes.append(cliente)
            registrar_evento(f"Gestor: cliente {cliente.id} agregado al sistema.")
            return cliente
        finally:
            registrar_evento("Gestor: fin del registro de cliente.")

    # ---------- Servicios ----------
    def crear_servicio(self, tipo: str, **datos) -> Servicio:
        """Crea un servicio del tipo indicado ('sala', 'equipo' o 'asesoria') y lo agrega.

        Los datos se pasan como argumentos con nombre, igual que al constructor
        de la clase correspondiente (identificador, nombre, costo_hora, ...).
        """
        try:
            clase = self.TIPOS_SERVICIO.get(str(tipo).strip().lower())
            if clase is None:
                raise ServicioInvalidoError(
                    f"Tipo de servicio desconocido: '{tipo}'. "
                    f"Use: {', '.join(self.TIPOS_SERVICIO)}.")
            identificador = datos.get("identificador")
            if isinstance(identificador, str) and any(
                    s.id == identificador.strip() for s in self._servicios):
                raise OperacionNoPermitidaError(
                    f"Ya existe un servicio con id {identificador}.")
            try:
                servicio = clase(**datos)
            except (TypeError, ValueError) as e:
                # Faltan argumentos o el identificador es inválido: se traduce a un error propio
                raise ServicioInvalidoError(
                    f"Datos incompletos o incorrectos para el servicio '{tipo}'.") from e
        except SoftwareFJError as e:
            registrar_error(f"Gestor: servicio no creado - {e}")
            raise
        else:
            self._servicios.append(servicio)
            registrar_evento(f"Gestor: servicio {servicio.id} ({servicio.nombre}) agregado.")
            return servicio
        finally:
            registrar_evento("Gestor: fin de la creación de servicio.")

    def cambiar_disponibilidad_servicio(self, id_servicio: str, disponible: bool) -> Servicio:
        """Activa o desactiva un servicio existente."""
        servicio = self.buscar_servicio(id_servicio)
        servicio.cambiar_disponibilidad(disponible)
        estado = "activado" if servicio.disponible else "desactivado"
        registrar_evento(f"Gestor: servicio {servicio.id} {estado}.")
        return servicio

    # ---------- Reservas ----------
    def crear_reserva(self, id_cliente: str, id_servicio: str, duracion, **extras) -> Reserva:
        """Crea una reserva PENDIENTE para un cliente y un servicio existentes.

        `duracion` son horas, días o sesiones según el servicio; `extras`
        recibe datos opcionales como `asistentes` o `cantidad`.
        """
        try:
            cliente = self.buscar_cliente(id_cliente)
            servicio = self.buscar_servicio(id_servicio)
            cliente.verificar_activo()
            servicio.verificar_disponibilidad()
            reserva = Reserva(cliente, servicio, duracion, **extras)
        except SoftwareFJError as e:
            registrar_error(f"Gestor: reserva no creada - {e}")
            raise
        else:
            cliente.registrar_reserva(reserva.id)
            self._reservas.append(reserva)
            registrar_evento(
                f"Gestor: reserva {reserva.id} creada ({cliente.id} -> {servicio.id}).")
            return reserva
        finally:
            registrar_evento("Gestor: fin de la creación de reserva.")

    def confirmar_reserva(self, id_reserva: str) -> Reserva:
        reserva = self.buscar_reserva(id_reserva)
        reserva.confirmar()  # Registra en el log y lanza OperacionNoPermitidaError si no aplica
        return reserva

    def cancelar_reserva(self, id_reserva: str) -> Reserva:
        reserva = self.buscar_reserva(id_reserva)
        reserva.cancelar()
        return reserva

    def procesar_reserva(self, id_reserva: str, impuesto: float = 0.19,
                         descuento: float = 0) -> float:
        """Confirma (si hace falta) y procesa la reserva. Devuelve el total cobrado."""
        reserva = self.buscar_reserva(id_reserva)
        return reserva.procesar(impuesto, descuento)

    def calcular_costo_reserva(self, id_reserva: str, impuesto: float = 0,
                               descuento: float = 0) -> float:
        """Costo de una reserva. Sobrecarga simulada con parámetros opcionales:
        calcular_costo_reserva(id) | (id, impuesto) | (id, impuesto, descuento)."""
        reserva = self.buscar_reserva(id_reserva)
        try:
            total = reserva.calcular_total(impuesto, descuento)
        except SoftwareFJError as e:
            registrar_error(f"Gestor: no se pudo calcular el costo de {id_reserva} - {e}")
            raise
        else:
            registrar_evento(
                f"Gestor: costo de {id_reserva} (impuesto={impuesto}, "
                f"descuento={descuento}) = ${total:,.2f}")
            return total

    # ---------- Resumen ----------
    def resumen(self) -> dict:
        """Totales del sistema y número de reservas en cada estado."""
        por_estado: dict = {}
        for reserva in self._reservas:
            por_estado[reserva.estado] = por_estado.get(reserva.estado, 0) + 1
        return {
            "clientes": len(self._clientes),
            "servicios": len(self._servicios),
            "reservas": len(self._reservas),
            "reservas_por_estado": por_estado,
        }
