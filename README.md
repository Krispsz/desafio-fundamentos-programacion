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
| `registro.py`      | Registro y modificacion de expedientes (con validacion en bucle)     |
| `procesamiento.py` | Busqueda por codigo, ordenamiento burbuja y eliminacion              |
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

Menu principal:

1. Registrar expediente (pide nombre, DNI y asunto; repite hasta que sean validos)
2. Buscar expediente por codigo (ej. `EXP-0001`)
3. Modificar expediente
4. Eliminar expediente
5. Ordenar expedientes (codigo, nombre, dni, asunto o fecha)
6. Salir (guarda en `expedientes.txt`)

Reglas de validacion: nombre y asunto no vacios, DNI de exactamente 8 caracteres.

## Equipo

| Integrante | Usuario en Git | Modulos                                         |
|------------|----------------|-------------------------------------------------|
| Fabrizio   | `Angel`        | `expediente.py`, `persistencia.py`, `main.py`    |
| Cristobal  | `Crizzz3`      | `validaciones.py`, `registro.py`                 |
| Alex       | `Alexander`    | `procesamiento.py`                               |

> Nota: los commits de Fabrizio aparecen con el nombre de usuario `Angel`.
