# Software FJ – Sistema Integral de Gestión de Clientes, Servicios y Reservas

Sistema orientado a objetos en Python para gestionar clientes, servicios y reservas de la empresa **Software FJ**, que ofrece reservas de salas, alquiler de equipos y asesorías especializadas. No usa bases de datos: toda la información se gestiona con objetos y listas en memoria. Los archivos solo se usan para registrar eventos y errores en un log.

> Curso **Programación (213023)** – Universidad Nacional Abierta y a Distancia (UNAD) – Fase 4.

---

## Objetivos

- Aplicar **abstracción, herencia, polimorfismo y encapsulación**.
- Implementar **manejo avanzado de excepciones**: excepciones personalizadas, `try/except`, `try/except/else`, `try/except/finally` y encadenamiento (`raise ... from ...`).
- Mantener la aplicación **estable** aunque ocurran errores, registrándolos en un archivo de logs.
- Simular **al menos 10 operaciones completas** (válidas e inválidas).

---

## Estructura del proyecto

```
software-fj-gestion-reservas/
├── README.md
├── .gitignore
├── main.py                  # Punto de entrada: simulación de las operaciones
├── software_fj/
│   ├── __init__.py
│   ├── entidad.py           # Clase abstracta Entidad (base de todo el sistema)
│   ├── cliente.py           # Clase Cliente con validaciones y encapsulación
│   ├── servicios.py         # Clase abstracta Servicio + servicios especializados
│   ├── reserva.py           # Clase Reserva (confirmar, cancelar, procesar)
│   ├── excepciones.py       # Excepciones personalizadas del sistema
│   ├── gestor.py            # SistemaGestion: listas internas de clientes, servicios y reservas
│   └── logger.py            # Configuración del registro de eventos y errores
└── logs/
    └── .gitkeep             # Aquí se genera eventos.log al ejecutar
```

---

## Diseño de clases

| Clase            | Tipo                           | Responsabilidad                                                                                             |
| ---------------- | ------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| `Entidad`        | Abstracta                      | Base común: `id`, fecha de creación y estado activo. `describir()` es abstracto; `validar()` es un método base que las subclases pueden sobrescribir. |
| `Cliente`        | Hereda de `Entidad`            | Datos personales encapsulados (`nombre`, `documento`, `correo`, `telefono`) con propiedades y validaciones. |
| `Servicio`       | Abstracta, hereda de `Entidad` | Define `calcular_costo()`, `describir()` y `validar_parametros()`.                                          |
| `ReservaSala`    | Hereda de `Servicio`           | Costo por hora y capacidad de la sala.                                                                      |
| `AlquilerEquipo` | Hereda de `Servicio`           | Costo por día y cantidad de equipos.                                                                        |
| `Asesoria`       | Hereda de `Servicio`           | Costo por sesión según especialidad y nivel.                                                                |
| `Reserva`        | Hereda de `Entidad`            | Integra cliente, servicio, duración y estado (`PENDIENTE`, `CONFIRMADA`, `PROCESADA`, `CANCELADA`, `FALLIDA`). |
| `SistemaGestion` | Gestor                         | Mantiene las listas internas y coordina las operaciones.                                                    |

### Polimorfismo

Cada servicio sobrescribe `calcular_costo()`, `describir()` y `validar_parametros()`, así que el sistema puede tratar cualquier servicio como un `Servicio` genérico.

### Métodos "sobrecargados"

Python no admite sobrecarga tradicional, así que la simulamos con **parámetros opcionales**:

```python
servicio.calcular_costo(duracion)                          # costo base
servicio.calcular_costo(duracion, impuesto=0.19)           # con IVA
servicio.calcular_costo(duracion, impuesto=0.19, descuento=0.10)  # con IVA y descuento
```

---

## Manejo de excepciones

Excepciones personalizadas definidas en `excepciones.py`:

```
SoftwareFJError (base)
├── ClienteError
│   ├── ClienteInvalidoError
│   └── ClienteParametroFaltanteError
├── ServicioInvalidoError
├── ServicioNoDisponibleError
├── ReservaError
│   └── ReservaInvalidaError
├── OperacionNoPermitidaError
└── CalculoInconsistenteError
```

### Ciclo de vida de una reserva

```
PENDIENTE ──confirmar()──► CONFIRMADA ──procesar()──► PROCESADA (no se puede cancelar)
    │                          │
    └──────cancelar()──────────┴──► CANCELADA
PENDIENTE ──procesar() falla al confirmar──► FALLIDA
```

`procesar()` confirma automáticamente una reserva `PENDIENTE` antes de calcular el total.

Se usan los siguientes bloques:

- `try/except`: captura de errores de validación.
- `try/except/else`: ejecuta la confirmación solo si no hubo errores.
- `try/except/finally`: registra siempre el resultado de la operación en el log.
- Encadenamiento: `raise ReservaInvalidaError("...") from error_original`.

Todos los errores y eventos relevantes quedan en `logs/eventos.log` con fecha, nivel y mensaje.

---

## Operaciones simuladas

`main.py` ejecuta estas operaciones:

| #  | Operación                                                              | Resultado esperado                                                 |
| -- | ---------------------------------------------------------------------- | ------------------------------------------------------------------ |
| 01 | Registro válido de un cliente                                          | OK: `CLI-0001`                                                     |
| 02 | Registro válido de un segundo cliente                                  | OK: `CLI-0002`                                                     |
| 03 | Registro de un cliente con correo inválido                             | Error controlado: `ClienteError` (causa `ClienteInvalidoError`)    |
| 04 | Registro de un cliente con datos faltantes (sin teléfono)              | Error controlado: `ClienteError` (causa `ClienteParametroFaltanteError`) |
| 05 | Creación válida de una ReservaSala                                     | OK: `SAL-01`                                                       |
| 06 | Creación válida de un AlquilerEquipo                                   | OK: `EQU-01`                                                       |
| 07 | Creación válida de una Asesoria (Ciberseguridad, nivel senior)         | OK: `ASE-01`                                                       |
| 08 | Creación de una Asesoria con parámetros inválidos (nivel 'master')     | Error controlado: `ServicioInvalidoError`                          |
| 09 | Reserva exitosa y confirmada (sala, 3 horas, 8 asistentes)             | OK: `RES-0001` en estado `CONFIRMADA`                              |
| 10 | Reserva exitosa de una Asesoria (senior, 2 sesiones, segundo cliente)  | OK: `RES-0002` en estado `PENDIENTE`, costo con IVA $428,400.00    |
| 11 | Reserva con duración negativa (equipo, -2 días)                        | Error controlado: `ReservaInvalidaError` (causa `CalculoInconsistenteError`) |
| 12 | Reserva sobre un servicio no disponible (equipo desactivado)           | Error controlado: `ServicioNoDisponibleError`                      |
| 13 | Cálculo de costo con impuesto y descuento                              | OK: base $150,000.00, con IVA $178,500.00, con IVA y 10 % de descuento $160,650.00 |
| 14 | Procesamiento exitoso de una reserva                                   | OK: `RES-0001` pasa a `PROCESADA`, total $178,500.00               |
| 15 | Cancelación exitosa de una reserva pendiente (asesoría)                | OK: `RES-0002` pasa de `PENDIENTE` a `CANCELADA`                   |
| 16 | Cancelación de una reserva ya procesada                                | Error controlado: `OperacionNoPermitidaError`                      |

En total son 10 operaciones válidas y 6 inválidas. Las operaciones 09, 10 y 13 muestran el polimorfismo: la sala cobra por hora, mientras que la asesoría cobra por sesión multiplicada por el recargo de su nivel (`senior` = 1.5).

Los ids de clientes y reservas los genera `Entidad` con el prefijo de cada clase (`CLI-0001`, `RES-0001`). Los servicios reciben su id a mano (`SAL-01`, `EQU-01`, `ASE-01`). La reserva de la operación 11 falla después de recibir su id (`RES-0003`), por eso ese id no aparece en el resumen.

Cada operación se ejecuta dentro de `ejecutar_operacion()`, que captura cualquier error, lo muestra (incluida la causa encadenada) y lo registra en el log. El programa termina sin interrupciones y muestra un resumen al final, con el conteo de operaciones exitosas, errores controlados y la verificación `Comportamiento esperado: 16/16`.

---

## Requisitos

- Python 3.10 o superior.
- No requiere librerías externas (solo la biblioteca estándar: `abc`, `logging`, `datetime`, `re`).

## Ejecución

```bash
git clone https://github.com/329miguel329/software-fj-gestion-reservas.git
cd software-fj-gestion-reservas
python main.py
```

Después de ejecutar, revisa el archivo `logs/eventos.log`.

---

## Integrantes

| Nombre                    | Rol / Aporte                                                                  |
| ------------------------- | ----------------------------------------------------------------------------- |
| _Santiago Fernandez Mora_ | Clase abstracta `Entidad` y clase `Cliente` (`entidad.py`, `cliente.py`)      |
| _David Rodriguez_         | Jerarquía de servicios (`servicios.py`)                                       |
| _David Rodriguez_         | Clase `Reserva` y su ciclo de vida (`reserva.py`)                             |
| _Miguel Angel Muñoz_      | Excepciones, logger y `SistemaGestion` (`excepciones.py`, `logger.py`, `gestor.py`) |
| _Miguel Angel Muñoz_      | Simulación (`main.py`) y documentación (`README.md`)                          |

**Grupo:** 213023_624

**Tutor:** EDDUAR YAKSEIR PEREZ PEREZ
