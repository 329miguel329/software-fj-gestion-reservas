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
| `Entidad`        | Abstracta                      | Base común: `id`, fecha de creación, métodos abstractos `validar()` y `describir()`.                        |
| `Cliente`        | Hereda de `Entidad`            | Datos personales encapsulados (`nombre`, `documento`, `correo`, `telefono`) con propiedades y validaciones. |
| `Servicio`       | Abstracta, hereda de `Entidad` | Define `calcular_costo()`, `describir()` y `validar_parametros()`.                                          |
| `ReservaSala`    | Hereda de `Servicio`           | Costo por hora y capacidad de la sala.                                                                      |
| `AlquilerEquipo` | Hereda de `Servicio`           | Costo por día y cantidad de equipos.                                                                        |
| `Asesoria`       | Hereda de `Servicio`           | Costo por sesión según especialidad y nivel.                                                                |
| `Reserva`        | Hereda de `Entidad`            | Integra cliente, servicio, duración y estado (`PENDIENTE`, `CONFIRMADA`, `CANCELADA`, `PROCESADA`).         |
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
├── ClienteInvalidoError
├── ServicioInvalidoError
├── ServicioNoDisponibleError
├── ReservaInvalidaError
├── OperacionNoPermitidaError
└── CalculoInconsistenteError
```

Se usan los siguientes bloques:

- `try/except`: captura de errores de validación.
- `try/except/else`: ejecuta la confirmación solo si no hubo errores.
- `try/except/finally`: registra siempre el resultado de la operación en el log.
- Encadenamiento: `raise ReservaInvalidaError("...") from error_original`.

Todos los errores y eventos relevantes quedan en `logs/eventos.log` con fecha, nivel y mensaje.

---

## Operaciones simuladas

`main.py` ejecuta al menos estas operaciones:

1. Registro válido de un cliente.
2. Registro de un cliente con correo inválido (error controlado).
3. Registro de un cliente con datos faltantes (error controlado).
4. Creación válida de una `ReservaSala`.
5. Creación válida de un `AlquilerEquipo`.
6. Creación de una `Asesoria` con parámetros inválidos (error controlado).
7. Reserva exitosa y confirmada.
8. Reserva con duración negativa (error controlado).
9. Reserva sobre un servicio no disponible (error controlado).
10. Cancelación de una reserva ya procesada (operación no permitida).
11. Cálculo de costo con impuesto y descuento.
12. Procesamiento exitoso de una reserva.

El programa termina sin interrupciones y muestra un resumen al final.

---

## Requisitos

- Python 3.10 o superior.
- No requiere librerías externas (solo la biblioteca estándar: `abc`, `logging`, `datetime`, `re`).

## Ejecución

```bash
git clone https://github.com/<usuario>/software-fj-gestion-reservas.git
cd software-fj-gestion-reservas
python main.py
```

Después de ejecutar, revisa el archivo `logs/eventos.log`.
