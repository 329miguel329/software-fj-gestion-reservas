"""
entidad.py - Clase abstracta Entidad de Software FJ.

Base común de clientes, servicios y reservas. Aporta el identificador
(generado automáticamente con un prefijo por clase), la fecha de creación,
el estado activo/inactivo, la igualdad por id y la representación en texto.
Las subclases deben implementar describir().
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from .excepciones import OperacionNoPermitidaError
from .logger import registrar_evento


class Entidad(ABC):
    """Entidad abstracta del sistema con id, fecha de creación y estado activo."""

    PREFIJO = "ENT"
    _contadores: dict = {}

    def __init__(self, identificador: Optional[str] = None) -> None:
        """Crea la entidad con el id indicado o, si no se pasa, con uno automático."""
        if identificador is None:
            self._id = self._generar_id()
        else:
            if not isinstance(identificador, str) or not identificador.strip():
                raise ValueError("El identificador debe ser un texto no vacío.")
            self._id = identificador.strip()
        self._fecha_creacion = datetime.now()
        self._activo = True

    # ---------- Generación de ID ----------
    @classmethod
    def _generar_id(cls) -> str:
        actual = Entidad._contadores.get(cls.PREFIJO, 0) + 1
        Entidad._contadores[cls.PREFIJO] = actual
        return f"{cls.PREFIJO}-{actual:04d}"

    # ---------- Propiedades (encapsulación: solo lectura) ----------
    @property
    def id(self) -> str:
        """Identificador único de la entidad."""
        return self._id

    @property
    def fecha_creacion(self) -> datetime:
        """Fecha y hora en que se creó la entidad."""
        return self._fecha_creacion

    @property
    def activo(self) -> bool:
        """Indica si la entidad está activa."""
        return self._activo

    # ---------- Comportamiento común ----------
    def activar(self) -> None:
        """Marca la entidad como activa y lo registra en el log."""
        self._activo = True
        registrar_evento(f"{self.__class__.__name__} {self._id}: activada/o.")

    def desactivar(self) -> None:
        """Marca la entidad como inactiva y lo registra en el log."""
        self._activo = False
        registrar_evento(f"{self.__class__.__name__} {self._id}: desactivada/o.")

    def verificar_activo(self) -> None:
        """Lanza OperacionNoPermitidaError si la entidad está inactiva."""
        if not self._activo:
            raise OperacionNoPermitidaError(
                f"{self.__class__.__name__} {self._id} está inactiva/o.")

    # ---------- Método abstracto ----------
    @abstractmethod
    def describir(self) -> str:
        """Devuelve una descripción en texto de la entidad."""
        pass

    # ---------- Método opcional (las subclases pueden sobrescribirlo) ----------
    def validar(self) -> bool:
        """Comprueba que los datos de la entidad sean válidos (por defecto, siempre True)."""
        return True

    # ---------- Métodos especiales ----------
    def __str__(self) -> str:
        return self.describir()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self._id} activo={self._activo}>"

    def __eq__(self, otro: object) -> bool:
        return isinstance(otro, Entidad) and self._id == otro._id

    def __hash__(self) -> int:
        return hash(self._id)
