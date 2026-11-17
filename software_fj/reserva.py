"""
reserva.py - Clase Reserva de Software FJ.

Integra cliente, servicio, duración y estado. Implementa confirmación,
cancelación y procesamiento con try/except/else/finally y encadenamiento
de excepciones (raise ... from ...).
"""
from .entidad import Entidad                 # Clase base del sistema (la desarrolla un compañero)
from .cliente import Cliente                 # Clase Cliente (la desarrolla un compañero)
from .servicios import Servicio              # Clase abstracta de servicios, para validar el tipo recibido
from .excepciones import (                   # Excepciones personalizadas del proyecto
    ReservaInvalidaError,                    # Se lanza cuando los datos de la reserva son incorrectos
    OperacionNoPermitidaError,               # Se lanza cuando un cambio de estado no está permitido
    ReservaError,                            # Error general al procesar una reserva
)
from .logger import registrar_evento, registrar_error   # Funciones del logger para registrar eventos y errores en el archivo de logs


class Reserva(Entidad):  # La reserva es una entidad del sistema, por eso hereda de Entidad
    """Reserva de un servicio por parte de un cliente."""

    # Estados posibles
    PENDIENTE = "PENDIENTE"  # Reserva creada, aún sin confirmar
    CONFIRMADA = "CONFIRMADA"  # Reserva aprobada
    CANCELADA = "CANCELADA"  # Reserva anulada por el cliente
    PROCESADA = "PROCESADA"  # Reserva confirmada y con el total ya calculado (estado final)
    FALLIDA = "FALLIDA"  # Reserva que no se pudo procesar

    PREFIJO = "RES"  # Prefijo que usa Entidad para generar los ids: RES-0001, RES-0002...

    def __init__(self, cliente, servicio, duracion, **extras):  # Constructor; **extras guarda datos opcionales como asistentes o cantidad
        # Validamos los tipos ANTES de gastar un id
        if not isinstance(cliente, Cliente):  # El cliente debe ser un objeto de la clase Cliente
            raise ReservaInvalidaError("La reserva requiere un Cliente válido.")  # Error si no lo es
        if not isinstance(servicio, Servicio):  # El servicio debe ser un objeto de una clase hija de Servicio
            raise ReservaInvalidaError("La reserva requiere un Servicio válido.")  # Error si no lo es
        super().__init__()  # Sin identificador: Entidad genera el id con el PREFIJO de la clase (RES-0001...)
        # Cada servicio valida a su manera (polimorfismo); el error original se encadena
        try:  # Intenta validar la solicitud con las reglas del servicio elegido
            servicio.validar_solicitud(duracion, **extras)  # Cada servicio aplica su propia validación (polimorfismo)
        except Exception as e:  # Si ocurre cualquier error de validación...
            registrar_error(f"{self.id}: solicitud inválida - {e}")  # ...lo registra en el archivo de logs
            raise ReservaInvalidaError("Los datos de la reserva no son válidos.") from e  # Lanza una excepción propia conservando la causa original (encadenamiento)
        self._cliente = cliente  # Guarda el cliente (atributo privado)
        self._servicio = servicio  # Guarda el servicio (atributo privado)
        self._duracion = duracion  # Guarda la duración (horas, días o sesiones según el servicio)
        self._extras = extras                  # Guarda los datos opcionales, ej.: asistentes, cantidad
        self._estado = Reserva.PENDIENTE  # Toda reserva nueva empieza como pendiente

    @property  # Propiedad de solo lectura
    def cliente(self):  # Getter del cliente
        return self._cliente  # Devuelve el cliente de la reserva

    @property  # Propiedad de solo lectura
    def servicio(self):  # Getter del servicio
        return self._servicio  # Devuelve el servicio reservado

    @property  # Propiedad de solo lectura
    def duracion(self):  # Getter de la duración
        return self._duracion  # Devuelve la duración reservada

    @property  # Propiedad de solo lectura
    def estado(self):  # Getter del estado
        return self._estado  # Devuelve el estado actual

    def calcular_total(self, impuesto=0, descuento=0):  # Calcula el total; parámetros opcionales simulan la sobrecarga
        """Total de la reserva. Variantes: calcular_total() | (impuesto) | (impuesto, descuento)."""
        return self._servicio.calcular_costo(  # Delega el cálculo al servicio (polimorfismo)
            self._duracion, impuesto, descuento, **self._extras)  # Pasa duración, impuesto, descuento y los extras guardados

    def confirmar(self):  # Pasa la reserva de PENDIENTE a CONFIRMADA
        """Confirma la reserva si está pendiente y el servicio está disponible."""
        try:  # Bloque donde se hacen las comprobaciones
            if self._estado != Reserva.PENDIENTE:  # Solo se puede confirmar si está pendiente
                raise OperacionNoPermitidaError(  # Si no, lanza la excepción de operación no permitida
                    f"No se puede confirmar una reserva en estado {self._estado}.")  # Mensaje con el estado actual
            self._servicio.verificar_disponibilidad()   # Puede lanzar ServicioNoDisponibleError si el servicio está desactivado
        except Exception as e:  # Captura cualquier error de las comprobaciones
            registrar_error(f"{self.id}: confirmación rechazada - {e}")  # Lo registra en el log
            raise                                       # Relanza la misma excepción para que quien llamó decida qué hacer
        else:  # Se ejecuta solo si el bloque try terminó sin errores
            self._estado = Reserva.CONFIRMADA           # Cambia el estado a confirmada
            registrar_evento(f"{self.id}: confirmada para {self._cliente.nombre}.")  # Registra el evento en el log
        finally:  # Se ejecuta siempre, haya o no error
            registrar_evento(f"{self.id}: intento de confirmación finalizado.")  # Deja constancia de que el intento terminó

    def cancelar(self):  # Pasa la reserva a CANCELADA
        """Cancela la reserva (no aplica si ya está cancelada, fallida o procesada)."""
        try:  # Bloque donde se hace la comprobación
            if self._estado in (Reserva.CANCELADA, Reserva.FALLIDA, Reserva.PROCESADA):  # No se puede cancelar lo que ya está cancelado, fallido o procesado
                raise OperacionNoPermitidaError(  # Lanza excepción de operación no permitida
                    f"No se puede cancelar una reserva en estado {self._estado}.")  # Mensaje con el estado actual
        except OperacionNoPermitidaError as e:  # Captura solo ese tipo de error
            registrar_error(f"{self.id}: cancelación rechazada - {e}")  # Lo registra en el log
            raise  # Relanza la excepción
        else:  # Solo si no hubo error
            self._estado = Reserva.CANCELADA  # Cambia el estado a cancelada
            registrar_evento(f"{self.id}: cancelada.")  # Registra el evento
        finally:  # Se ejecuta siempre
            registrar_evento(f"{self.id}: intento de cancelación finalizado.")  # Deja constancia del intento

    def procesar(self, impuesto=0.19, descuento=0):  # Confirma la reserva y calcula el total (impuesto por defecto 19 %)
        """Confirma (si hace falta) y calcula el total. Si todo sale bien queda PROCESADA;
        si algo falla, marca FALLIDA y encadena la causa."""
        try:  # Bloque principal del procesamiento
            if self._estado == Reserva.PENDIENTE:  # Si aún no está confirmada...
                self.confirmar()  # Paso 1: ...se confirma primero
            elif self._estado != Reserva.CONFIRMADA:  # Solo se procesan reservas pendientes o confirmadas
                raise OperacionNoPermitidaError(  # Cualquier otro estado (cancelada, fallida, procesada) no se puede procesar
                    f"No se puede procesar una reserva en estado {self._estado}.")  # Mensaje con el estado actual
            total = self.calcular_total(impuesto, descuento)  # Paso 2: calcular el total con impuesto y descuento
        except Exception as e:  # Si falla cualquiera de los dos pasos...
            if self._estado == Reserva.PENDIENTE:       # Solo se marca como fallida si seguía pendiente
                self._estado = Reserva.FALLIDA  # Cambia el estado a fallida
            registrar_error(f"{self.id}: procesamiento fallido - {e}")  # Registra el error en el log
            raise ReservaError(f"No se pudo procesar la reserva {self.id}.") from e  # Lanza un error general conservando la causa original
        else:  # Si todo salió bien
            self._estado = Reserva.PROCESADA  # Cambia el estado a procesada (ya no se puede cancelar)
            registrar_evento(f"{self.id}: procesada. Total ${total:,.2f}")  # Registra el total procesado
            return total  # Devuelve el total al llamador
        finally:  # Se ejecuta siempre
            registrar_evento(f"{self.id}: fin de procesamiento (estado {self._estado}).")  # Registra el fin del proceso y el estado final

    def describir(self):  # Descripción de la reserva
        return (f"{self.id} | {self._cliente.nombre} | {self._servicio.nombre} | "  # Primera parte: id, cliente y servicio
                f"{self._duracion} | {self._estado}")  # Segunda parte: duración y estado
