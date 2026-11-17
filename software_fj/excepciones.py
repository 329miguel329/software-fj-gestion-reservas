"""
excepciones.py - Excepciones personalizadas de Software FJ.

Todas heredan de SoftwareFJError, de modo que un solo
`except SoftwareFJError` captura cualquier error controlado del sistema.

SoftwareFJError
├── ClienteError
│   ├── ClienteInvalidoError
│   └── ClienteParametroFaltanteError
├── ServicioInvalidoError
├── ServicioNoDisponibleError
├── ReservaError
│   └── ReservaInvalidaError
├── OperacionNoPermitidaError
└── CalculoInconsistenteError
"""


class SoftwareFJError(Exception):
    """Excepción base de todo el sistema Software FJ."""


# ---------------- Clientes ----------------
class ClienteError(SoftwareFJError):
    """Error general relacionado con un cliente."""


class ClienteInvalidoError(ClienteError):
    """Un dato del cliente no cumple el formato esperado."""

    def __init__(self, campo: str, mensaje: str):
        self.campo = campo  # Campo que falló, útil para mostrar o depurar
        super().__init__(f"[{campo}] {mensaje}")


class ClienteParametroFaltanteError(ClienteError):
    """Falta un dato obligatorio del cliente."""

    def __init__(self, campo: str):
        self.campo = campo
        super().__init__(f"Parámetro obligatorio faltante: '{campo}'")


# ---------------- Servicios ----------------
class ServicioInvalidoError(SoftwareFJError):
    """Los datos con que se define un servicio son incorrectos."""


class ServicioNoDisponibleError(SoftwareFJError):
    """El servicio está desactivado, no existe o no tiene stock suficiente."""


# ---------------- Reservas ----------------
class ReservaError(SoftwareFJError):
    """Error general al crear o procesar una reserva."""


class ReservaInvalidaError(ReservaError):
    """Los datos de la reserva no son válidos."""


# ---------------- Generales ----------------
class OperacionNoPermitidaError(SoftwareFJError):
    """La operación no está permitida en el estado actual del objeto."""


class CalculoInconsistenteError(SoftwareFJError):
    """La duración, el impuesto o el descuento no permiten un cálculo coherente."""
