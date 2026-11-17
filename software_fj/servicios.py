"""
servicios.py - Jerarquía de servicios de Software FJ.

Contiene la clase abstracta Servicio y tres servicios especializados:
ReservaSala, AlquilerEquipo y Asesoria. Aplica abstracción, herencia,
polimorfismo, encapsulación y manejo de excepciones personalizadas.
"""
from abc import ABC, abstractmethod   # ABC permite crear clases abstractas; abstractmethod marca métodos que los hijos deben implementar
from numbers import Real              # Real es el tipo base de los números reales (int y float), útil para validar tipos

from .entidad import Entidad          # Importa la clase abstracta base del sistema (la desarrolla un compañero)
from .excepciones import (            # Importa las excepciones personalizadas del proyecto (las desarrolla un compañero)
    ServicioInvalidoError,            # Se lanza cuando los datos con que se define un servicio son incorrectos
    ServicioNoDisponibleError,        # Se lanza cuando el servicio está desactivado o no hay stock suficiente
    CalculoInconsistenteError,        # Se lanza cuando la duración, el impuesto o el descuento no son válidos
)


def _es_numero(valor):
    """True si es un número real positivo o cero y no es un booleano."""
    return isinstance(valor, Real) and not isinstance(valor, bool)  # En Python True/False cuentan como números, por eso se excluyen los booleanos


def _es_entero(valor):
    """True si es un entero y no es un booleano (True/False cuentan como int)."""
    return isinstance(valor, int) and not isinstance(valor, bool)  # Verifica que sea int y descarta True/False


class Servicio(Entidad, ABC):  # Clase abstracta: hereda de Entidad y de ABC, por lo que no se puede instanciar directamente
    """Clase abstracta que representa un servicio de Software FJ."""

    def __init__(self, identificador, nombre, disponible=True):  # Constructor: recibe id, nombre y si está disponible (por defecto True)
        super().__init__(identificador)   # Llama al constructor de Entidad para que guarde el identificador
        # Validamos el nombre antes de guardarlo
        if not isinstance(nombre, str) or not nombre.strip():  # Comprueba que sea texto y que no esté vacío ni solo con espacios
            raise ServicioInvalidoError("El nombre del servicio es obligatorio.")  # Si falla, lanza la excepción personalizada con un mensaje claro
        self._nombre = nombre.strip()     # Guarda el nombre sin espacios sobrantes; el guion bajo indica atributo privado (encapsulación)
        self._disponible = bool(disponible)  # Guarda el estado como booleano para evitar valores raros

    @property  # Convierte el método en una propiedad: se usa como servicio.nombre, sin paréntesis
    def nombre(self):  # Getter del nombre
        """Nombre del servicio (solo lectura)."""
        return self._nombre  # Devuelve el atributo privado; no hay setter, así que no se puede modificar desde fuera

    @property  # Propiedad de solo lectura
    def disponible(self):  # Getter del estado de disponibilidad
        """Indica si el servicio está activo (solo lectura)."""
        return self._disponible  # Devuelve True si el servicio está activo

    def cambiar_disponibilidad(self, estado):  # Método controlado para activar o desactivar el servicio
        """Activa o desactiva el servicio."""
        self._disponible = bool(estado)  # Convierte el valor recibido a booleano y lo guarda

    def verificar_disponibilidad(self):  # Comprueba si el servicio se puede usar
        """Lanza excepción si el servicio no está disponible."""
        if not self._disponible:  # Si el servicio está desactivado...
            raise ServicioNoDisponibleError(  # ...se lanza la excepción de servicio no disponible
                f"El servicio {self._nombre} no está disponible.")  # Mensaje que incluye el nombre del servicio

    # ---------- Métodos abstractos: cada hijo los sobrescribe (polimorfismo) ----------
    @abstractmethod  # Obliga a que cada clase hija implemente este método
    def validar_parametros(self):  # Valida los datos propios del servicio
        """Valida los datos propios del servicio (se llama al crearlo)."""

    @abstractmethod  # Método abstracto: sin implementación en la clase base
    def validar_solicitud(self, duracion, **extras):  # Valida los datos de una reserva concreta; **extras recibe datos opcionales (asistentes, cantidad...)
        """Valida los datos de una solicitud concreta (duración, asistentes, cantidad...)."""

    @abstractmethod  # Método abstracto que cada servicio implementa según su fórmula de costo
    def calcular_costo(self, duracion, impuesto=0, descuento=0, **extras):  # Parámetros opcionales: así se simula la sobrecarga de métodos
        """Calcula el costo. Sobrecarga simulada con parámetros opcionales:
        calcular_costo(d) | calcular_costo(d, impuesto) | calcular_costo(d, impuesto, descuento)."""

    @abstractmethod  # Cada servicio se describe a su manera
    def describir(self):  # Devuelve un texto con la información del servicio
        """Devuelve una descripción en texto del servicio."""

    # ---------- Utilidad compartida por los hijos ----------
    def _calcular_total(self, costo_base, impuesto, descuento):  # Método auxiliar (privado) que usan todos los hijos
        """Aplica impuesto y descuento al costo base y valida que sean coherentes."""
        if not _es_numero(impuesto):  # El impuesto debe ser un número
            raise CalculoInconsistenteError("El impuesto debe ser numérico.")  # Error si no lo es
        if not _es_numero(descuento):  # El descuento debe ser un número
            raise CalculoInconsistenteError("El descuento debe ser numérico.")  # Error si no lo es
        if impuesto < 0:  # Un impuesto negativo no tiene sentido
            raise CalculoInconsistenteError("El impuesto no puede ser negativo.")  # Error por impuesto negativo
        if descuento < 0 or descuento > 1:  # El descuento se expresa como fracción: 0 (nada) a 1 (100 %)
            raise CalculoInconsistenteError("El descuento debe estar entre 0 y 1.")  # Error por descuento fuera de rango
        total = costo_base * (1 - descuento) * (1 + impuesto)  # Primero resta el descuento y luego suma el impuesto
        return round(total, 2)                                  # Redondea a 2 decimales y devuelve el total


class ReservaSala(Servicio):  # Servicio concreto: hereda de Servicio e implementa todos sus métodos abstractos
    """Servicio de alquiler de salas, cobrado por horas."""

    def __init__(self, identificador, nombre, costo_hora, capacidad, disponible=True):  # Constructor de la sala
        super().__init__(identificador, nombre, disponible)  # Reutiliza el constructor de Servicio (id, nombre, disponibilidad)
        self._costo_hora = costo_hora     # Precio por hora (atributo privado)
        self._capacidad = capacidad       # Máximo de personas que admite la sala (atributo privado)
        self.validar_parametros()         # Falla al crear el objeto si los datos son inválidos

    def validar_parametros(self):  # Implementación propia de la validación de la sala
        if not _es_numero(self._costo_hora) or self._costo_hora <= 0:  # El costo debe ser un número mayor que cero
            raise ServicioInvalidoError("El costo por hora debe ser positivo.")  # Error si el costo es inválido
        if not _es_entero(self._capacidad) or self._capacidad <= 0:  # La capacidad debe ser un entero mayor que cero
            raise ServicioInvalidoError("La capacidad debe ser un entero positivo.")  # Error si la capacidad es inválida

    def validar_solicitud(self, duracion, **extras):  # Valida una reserva concreta de la sala
        if not _es_numero(duracion) or duracion <= 0:  # Las horas deben ser un número positivo
            raise CalculoInconsistenteError("Las horas deben ser positivas.")  # Error por horas inválidas
        if duracion > 12:                 # Regla de negocio: máximo 12 horas
            raise CalculoInconsistenteError("Una sala no se reserva por más de 12 horas.")  # Error por exceder el máximo
        asistentes = extras.get("asistentes", 1)   # Dato opcional de la reserva; si no se envía, se asume 1 persona
        if not _es_entero(asistentes) or asistentes <= 0 or asistentes > self._capacidad:  # Debe ser entero, positivo y no superar la capacidad
            raise CalculoInconsistenteError(  # Lanza la excepción si algo falla
                f"Asistentes inválidos: la sala admite hasta {self._capacidad} personas.")  # Mensaje con la capacidad real de la sala

    def calcular_costo(self, duracion, impuesto=0, descuento=0, **extras):  # Cálculo del costo de la sala
        self.verificar_disponibilidad()              # 1. Comprueba que la sala esté activa
        self.validar_solicitud(duracion, **extras)   # 2. Valida horas y asistentes
        costo_base = self._costo_hora * duracion     # 3. Costo = tarifa por hora x horas
        return self._calcular_total(costo_base, impuesto, descuento)  # 4. Aplica descuento e impuesto y devuelve el total

    def describir(self):  # Descripción de la sala
        return (f"Sala: {self._nombre}. Costo por hora: ${self._costo_hora}. "  # Primera parte: nombre y tarifa
                f"Capacidad: {self._capacidad} personas.")  # Segunda parte: capacidad


class AlquilerEquipo(Servicio):  # Servicio concreto de alquiler de equipos
    """Servicio de alquiler de equipos, cobrado por días."""

    def __init__(self, identificador, nombre, costo_dia, stock, disponible=True):  # Constructor del equipo
        super().__init__(identificador, nombre, disponible)  # Reutiliza el constructor de Servicio
        self._costo_dia = costo_dia       # Precio por día y por unidad
        self._stock = stock               # Unidades existentes del equipo
        self.validar_parametros()         # Valida los datos al crear el objeto

    def validar_parametros(self):  # Validación propia del equipo
        if not _es_numero(self._costo_dia) or self._costo_dia <= 0:  # El costo diario debe ser un número positivo
            raise ServicioInvalidoError("El costo por día debe ser positivo.")  # Error si es inválido
        if not _es_entero(self._stock) or self._stock < 0:  # El stock debe ser un entero de cero en adelante
            raise ServicioInvalidoError("El stock debe ser un entero no negativo.")  # Error si es inválido

    def validar_solicitud(self, duracion, **extras):  # Valida una reserva concreta del equipo
        if not _es_entero(duracion) or duracion <= 0:  # Los días deben ser un entero positivo
            raise CalculoInconsistenteError("Los días deben ser un entero positivo.")  # Error por días inválidos
        cantidad = extras.get("cantidad", 1)       # La cantidad la pide la reserva; si no se envía, se asume 1
        if not _es_entero(cantidad) or cantidad <= 0:  # La cantidad debe ser un entero positivo
            raise CalculoInconsistenteError("La cantidad solicitada debe ser positiva.")  # Error por cantidad inválida
        if cantidad > self._stock:  # No se puede pedir más de lo que hay en stock
            raise ServicioNoDisponibleError(  # Lanza error de disponibilidad
                f"Solo hay {self._stock} unidades de {self._nombre}.")  # Mensaje con el stock real

    def calcular_costo(self, duracion, impuesto=0, descuento=0, **extras):  # Cálculo del costo del alquiler
        self.verificar_disponibilidad()  # 1. Comprueba que el servicio esté activo
        self.validar_solicitud(duracion, **extras)  # 2. Valida días y cantidad
        cantidad = extras.get("cantidad", 1)  # 3. Obtiene la cantidad solicitada (1 por defecto)
        costo_base = self._costo_dia * duracion * cantidad   # 4. Costo = tarifa x días x unidades
        return self._calcular_total(costo_base, impuesto, descuento)  # 5. Aplica descuento e impuesto y devuelve el total

    def describir(self):  # Descripción del equipo
        return (f"Equipo: {self._nombre}. Costo por día: ${self._costo_dia}. "  # Primera parte: nombre y tarifa diaria
                f"Unidades en stock: {self._stock}.")  # Segunda parte: unidades disponibles


class Asesoria(Servicio):  # Servicio concreto de asesorías especializadas
    """Servicio de asesorías especializadas, cobrado por sesión."""

    # El nivel del asesor multiplica el precio (así el nivel sí influye en el costo)
    RECARGOS = {"junior": 1.0, "senior": 1.5, "experto": 2.0}  # Atributo de clase: multiplicador de precio según el nivel

    def __init__(self, identificador, nombre, especialidad, nivel, costo_sesion, disponible=True):  # Constructor de la asesoría
        super().__init__(identificador, nombre, disponible)  # Reutiliza el constructor de Servicio
        self._especialidad = especialidad  # Área en la que se da la asesoría
        self._nivel = nivel.lower() if isinstance(nivel, str) else nivel  # Pasa el nivel a minúsculas si es texto, para aceptar "Senior" o "SENIOR"
        self._costo_sesion = costo_sesion  # Precio base por sesión
        self.validar_parametros()  # Valida los datos al crear el objeto

    def validar_parametros(self):  # Validación propia de la asesoría
        if not isinstance(self._especialidad, str) or not self._especialidad.strip():  # La especialidad debe ser texto no vacío
            raise ServicioInvalidoError("Debe indicar una especialidad.")  # Error si falta
        if self._nivel not in self.RECARGOS:  # El nivel debe ser uno de los definidos en RECARGOS
            raise ServicioInvalidoError(  # Lanza error de servicio inválido
                f"Nivel inválido. Use: {', '.join(self.RECARGOS)}.")  # Mensaje que lista los niveles permitidos
        if not _es_numero(self._costo_sesion) or self._costo_sesion <= 0:  # El costo por sesión debe ser un número positivo
            raise ServicioInvalidoError("El costo por sesión debe ser positivo.")  # Error si es inválido

    def validar_solicitud(self, duracion, **extras):  # Valida una reserva concreta de asesoría
        if not _es_entero(duracion) or duracion <= 0:  # Las sesiones deben ser un entero positivo
            raise CalculoInconsistenteError(  # Lanza error de cálculo
                "La cantidad de sesiones debe ser un entero positivo.")  # Mensaje de error

    def calcular_costo(self, duracion, impuesto=0, descuento=0, **extras):  # Cálculo del costo de la asesoría
        self.verificar_disponibilidad()  # 1. Comprueba que el servicio esté activo
        self.validar_solicitud(duracion, **extras)  # 2. Valida la cantidad de sesiones
        costo_base = self._costo_sesion * duracion * self.RECARGOS[self._nivel]  # 3. Costo = tarifa x sesiones x multiplicador del nivel
        return self._calcular_total(costo_base, impuesto, descuento)  # 4. Aplica descuento e impuesto y devuelve el total

    def describir(self):  # Descripción de la asesoría
        return (f"Asesoría: {self._nombre}. Especialidad: {self._especialidad}. "  # Primera parte: nombre y especialidad
                f"Nivel: {self._nivel}. Costo por sesión: ${self._costo_sesion}.")  # Segunda parte: nivel y tarifa
