# Desafio Fundamentos de la Programacion — Mesa de Partes Digital

Prototipo de **mesa de partes digital** desarrollado en Python como desafio final
del curso **Fundamentos de Programacion (CIIN1205P)**.

El sistema permite registrar expedientes (documentos que ingresan a una entidad),
validarlos, almacenarlos en un archivo de texto plano y consultarlos posteriormente.

## Estructura del proyecto

| Archivo            | Responsabilidad                                                     |
|--------------------|---------------------------------------------------------------------|
| `expediente.py`    | Estructura del expediente y generacion de codigos correlativos       |
| `persistencia.py`  | Lectura y escritura del archivo de texto `expedientes.txt`           |
| `validaciones.py`  | Validacion de los datos ingresados por el usuario                    |
| `registro.py`      | Flujo de registro y listado de expedientes                           |
| `procesamiento.py` | Busquedas, filtros y estadisticas sobre los expedientes              |
| `main.py`          | Menu principal e integracion de todos los modulos                    |

## Formato de almacenamiento

Los expedientes se guardan en `expedientes.txt`, un registro por linea, con los
campos separados por el caracter `|`:

```
codigo|nombre|dni|asunto|fecha
EXP-0001|Juan Perez|12345678|Tramite X|2026-09-17
```

## Ejecucion

Requiere Python 3 (sin dependencias externas):

```bash
python main.py
```

## Equipo

Trabajo grupal. El desarrollo esta repartido por modulos entre los integrantes.
