"""
cliente.py - Clase Cliente de Software FJ.

Guarda los datos personales del cliente de forma encapsulada (atributos
privados con propiedades) y los valida al crearlo y al modificarlo. Lleva el
historial de ids de sus reservas e incluye una fábrica desde diccionario con
try/except/else/finally y encadenamiento de excepciones.
"""
import re
from typing import Optional

from .entidad import Entidad
from .excepciones import (
    ClienteError,
    ClienteInvalidoError,
    ClienteParametroFaltanteError,
    OperacionNoPermitidaError,
)
from .logger import registrar_error, registrar_evento


_RE_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' ]{3,60}$")
_RE_DOCUMENTO = re.compile(r"^\d{5,12}$")
_RE_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
_RE_TELEFONO = re.compile(r"^3\d{9}$")


class Cliente(Entidad):
    """Cliente de Software FJ con datos personales validados."""

    PREFIJO = "CLI"

    def __init__(self, nombre: Optional[str] = None,
                 documento: Optional[str] = None,
                 correo: Optional[str] = None,
                 telefono: Optional[str] = None) -> None:
        """Valida todos los datos antes de crear el cliente; si alguno falla, no se genera id."""
        nombre = self._validar_nombre(nombre)
        documento = self._validar_documento(documento)
        correo = self._validar_correo(correo)
        telefono = self._validar_telefono(telefono)

        super().__init__()
        self.__nombre = nombre
        self.__documento = documento
        self.__correo = correo
        self.__telefono = telefono
        self.__reservas_ids: list = []
        registrar_evento(f"Cliente creado: {self.id} ({self.__nombre})")

    # ---------- Validadores (estáticos, reutilizables) ----------
    @staticmethod
    def _requerido(valor, campo: str) -> str:
        if valor is None or not str(valor).strip():
            raise ClienteParametroFaltanteError(campo)
        return str(valor).strip()

    @staticmethod
    def _validar_nombre(valor) -> str:
        valor = Cliente._requerido(valor, "nombre")
        if not _RE_NOMBRE.match(valor):
            raise ClienteInvalidoError(
                "nombre", "Solo letras y espacios, entre 3 y 60 caracteres.")
        return " ".join(valor.split()).title()

    @staticmethod
    def _validar_documento(valor) -> str:
        valor = Cliente._requerido(valor, "documento")
        if not _RE_DOCUMENTO.match(valor):
            raise ClienteInvalidoError(
                "documento", "Debe contener solo dígitos (5 a 12).")
        return valor

    @staticmethod
    def _validar_correo(valor) -> str:
        valor = Cliente._requerido(valor, "correo")
        if not _RE_CORREO.match(valor):
            raise ClienteInvalidoError("correo", "Formato de correo inválido.")
        return valor.lower()

    @staticmethod
    def _validar_telefono(valor) -> str:
        valor = Cliente._requerido(valor, "telefono")
        if not _RE_TELEFONO.match(valor):
            raise ClienteInvalidoError(
                "telefono", "Debe tener 10 dígitos y empezar por 3.")
        return valor

    # ---------- Propiedades con validación en el setter ----------
    @property
    def nombre(self) -> str:
        """Nombre completo, normalizado en formato título."""
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self.__nombre = self._validar_nombre(valor)

    @property
    def documento(self) -> str:
        """Número de documento (solo lectura)."""
        return self.__documento

    @property
    def correo(self) -> str:
        """Correo electrónico en minúsculas."""
        return self.__correo

    @correo.setter
    def correo(self, valor: str) -> None:
        self.__correo = self._validar_correo(valor)

    @property
    def telefono(self) -> str:
        """Teléfono celular de 10 dígitos."""
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        self.__telefono = self._validar_telefono(valor)

    @property
    def reservas(self) -> tuple:
        """Ids de las reservas del cliente (copia de solo lectura)."""
        return tuple(self.__reservas_ids)

    # ---------- Método con parámetros opcionales  ----------
    def actualizar_datos(self, nombre: Optional[str] = None,
                         correo: Optional[str] = None,
                         telefono: Optional[str] = None) -> None:
        """Actualiza uno o varios datos; si alguno es inválido, no cambia ninguno."""
        if nombre is None and correo is None and telefono is None:
            raise ClienteParametroFaltanteError("nombre, correo o telefono")
        try:
            nuevo_nombre = self._validar_nombre(nombre) if nombre is not None else self.__nombre
            nuevo_correo = self._validar_correo(correo) if correo is not None else self.__correo
            nuevo_tel = self._validar_telefono(telefono) if telefono is not None else self.__telefono
        except ClienteError as e:
            registrar_error(f"{self.id}: actualización fallida - {e}")
            raise
        else:
            self.__nombre, self.__correo, self.__telefono = nuevo_nombre, nuevo_correo, nuevo_tel
            registrar_evento(f"{self.id}: datos actualizados.")

    # ---------- Historial de reservas ----------
    def registrar_reserva(self, id_reserva: str) -> None:
        """Asocia una reserva al cliente; debe estar activo y no tenerla ya."""
        self.verificar_activo()
        if id_reserva in self.__reservas_ids:
            raise OperacionNoPermitidaError(
                f"La reserva {id_reserva} ya está registrada en {self.id}.")
        self.__reservas_ids.append(id_reserva)
        registrar_evento(f"{self.id}: reserva {id_reserva} asociada.")

    def quitar_reserva(self, id_reserva: str) -> None:
        """Quita una reserva del historial del cliente."""
        try:
            self.__reservas_ids.remove(id_reserva)
        except ValueError as e:
            raise OperacionNoPermitidaError(
                f"{self.id} no tiene la reserva {id_reserva}.") from e
        registrar_evento(f"{self.id}: reserva {id_reserva} retirada.")

    # ---------- Implementación de métodos de Entidad ----------
    def describir(self) -> str:
        """Devuelve una línea con los datos del cliente, su estado y número de reservas."""
        estado = "activo" if self.activo else "inactivo"
        return (f"Cliente {self.id} | {self.__nombre} | Doc: {self.__documento} | "
                f"{self.__correo} | Tel: {self.__telefono} | {estado} | "
                f"Reservas: {len(self.__reservas_ids)}")

    def validar(self) -> bool:
        """Revalida todos los datos guardados; lanza ClienteError si alguno no es válido."""
        self._validar_nombre(self.__nombre)
        self._validar_documento(self.__documento)
        self._validar_correo(self.__correo)
        self._validar_telefono(self.__telefono)
        return True

    # ---------- Fábrica con try/except/else/finally y encadenamiento ----------
    @classmethod
    def desde_diccionario(cls, datos: dict) -> "Cliente":
        """Crea un cliente a partir de un diccionario; encadena el error original si falla."""
        try:
            cliente = cls(
                nombre=datos.get("nombre"),
                documento=datos.get("documento"),
                correo=datos.get("correo"),
                telefono=datos.get("telefono"),
            )
        except ClienteError as e:
            registrar_error(f"No se pudo crear el cliente: {e}")
            raise ClienteError("Registro de cliente rechazado.") from e
        except AttributeError as e:
            registrar_error(f"Datos de cliente con formato incorrecto: {e}")
            raise ClienteInvalidoError("datos", "Se esperaba un diccionario.") from e
        else:
            registrar_evento(f"Cliente registrado correctamente: {cliente.id}")
            return cliente
        finally:
            registrar_evento("Fin del intento de registro de cliente.")

    def a_diccionario(self) -> dict:
        """Devuelve los datos del cliente como diccionario."""
        return {
            "id": self.id,
            "nombre": self.__nombre,
            "documento": self.__documento,
            "correo": self.__correo,
            "telefono": self.__telefono,
            "activo": self.activo,
            "reservas": list(self.__reservas_ids),
        }