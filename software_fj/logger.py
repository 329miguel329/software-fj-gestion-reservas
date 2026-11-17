"""
logger.py - Registro de eventos y errores de Software FJ.

Escribe en logs/eventos.log (en la raíz del proyecto) con fecha, nivel y
mensaje. Si el archivo no se puede abrir, el registro pasa a la salida de
error estándar para que la aplicación nunca se detenga por culpa del log.
"""
import logging
import sys
from pathlib import Path

RUTA_LOGS = Path(__file__).resolve().parent.parent / "logs"
ARCHIVO_LOG = RUTA_LOGS / "eventos.log"

_FORMATO = "%(asctime)s | %(levelname)-7s | %(message)s"
_FORMATO_FECHA = "%Y-%m-%d %H:%M:%S"


def _configurar_logger() -> logging.Logger:
    """Crea (una sola vez) el logger del sistema con su manejador de archivo."""
    logger = logging.getLogger("software_fj")
    if logger.handlers:  # Ya configurado: evita duplicar líneas en el archivo
        return logger

    try:
        RUTA_LOGS.mkdir(exist_ok=True)
        manejador = logging.FileHandler(ARCHIVO_LOG, encoding="utf-8")
    except OSError as e:
        # Sin permisos o disco lleno: se registra en consola y se sigue adelante
        manejador = logging.StreamHandler(sys.stderr)
        print(f"Aviso: no se pudo abrir {ARCHIVO_LOG} ({e}). "
              "Los eventos se mostrarán en consola.", file=sys.stderr)
    else:
        manejador.setLevel(logging.INFO)

    manejador.setFormatter(logging.Formatter(_FORMATO, _FORMATO_FECHA))
    logger.addHandler(manejador)
    logger.setLevel(logging.INFO)
    logger.propagate = False  # No reenviar al logger raíz (evita duplicados)
    return logger


_logger = _configurar_logger()


def registrar_evento(mensaje: str) -> None:
    """Registra un evento normal del sistema (nivel INFO)."""
    _logger.info(mensaje)


def registrar_error(mensaje: str) -> None:
    """Registra un error controlado del sistema (nivel ERROR)."""
    _logger.error(mensaje)
