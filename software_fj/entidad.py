
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from .excepciones import OperacionNoPermitidaError
from .logger import registrar_evento


class Entidad(ABC):
    
    PREFIJO = "ENT"          
    _contadores: dict = {}  

    def __init__(self, identificador: Optional[str] = None) -> None:
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
        return self._id

    @property
    def fecha_creacion(self) -> datetime:
        return self._fecha_creacion

    @property
    def activo(self) -> bool:
        return self._activo

    # ---------- Comportamiento común ----------
    def activar(self) -> None:
        self._activo = True
        registrar_evento(f"{self.__class__.__name__} {self._id}: activada/o.")

    def desactivar(self) -> None:
        self._activo = False
        registrar_evento(f"{self.__class__.__name__} {self._id}: desactivada/o.")

    def verificar_activo(self) -> None:
        
        if not self._activo:
            raise OperacionNoPermitidaError(
                f"{self.__class__.__name__} {self._id} está inactiva/o.")

 # ---------- Método abstracto ----------
    @abstractmethod
    def describir(self) -> str:
        pass

    # ---------- Método opcional (las subclases pueden sobrescribirlo) ----------
    def validar(self) -> bool:
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