# Desafio Fundamentos de la Programacion — Mesa de Partes Digital

Prototipo de **mesa de partes digital** desarrollado en Python como desafio final
del curso **Fundamentos de Programacion (CIIN1205P)**.

El sistema permite registrar expedientes (documentos que ingresan a una entidad),
validarlos, almacenarlos en un archivo de texto plano y consultarlos posteriormente.

## Estructura del proyecto

| Archivo            | Responsabilidad                                                     |
|--------------------|---------------------------------------------------------------------|
| `expediente.py`    | Estructura del expediente y generacion de codigos correlativos       |
| `persistencia.py`  | Punto de entrada para guardar y cargar: elige texto o SQLite         |
| `persistencia_db.py` | Lectura y escritura en la base SQLite `mesa_partes.db`           |
| `validaciones.py`  | Normalizacion y validacion de los datos ingresados por el usuario    |
| `registro.py`      | Registro y modificacion de expedientes (con validacion en bucle)     |
| `procesamiento.py` | Busquedas (codigo y texto), tabla, ordenamiento burbuja, eliminacion |
| `autenticacion.py` | Login con usuarios.txt: hash SHA-256, retorna True/False y el rol    |
| `main.py`          | Menu principal e integracion de todos los modulos                    |

## Convencion de codigo

Se separa la **logica** de la **consola**:

- Las funciones de logica (`expediente.py`, `persistencia.py`, `autenticacion.py`,
  `validaciones.py`) solo reciben parametros y **retornan valores**: no usan `print` ni `input`.
- Los `input` y `print` van en la capa de consola (`main.py` y las funciones de menu).

Ejemplo:

```python
# logica (autenticacion.py): retorna una tupla, no imprime
valido, rol = verificar_login(usuario, clave)

# consola (main.py): decide que mostrar
if valido:
    print("Bienvenido, " + usuario + " (" + rol + ")")
```

Asi la misma logica se puede reutilizar desde la interfaz grafica y probar con `unittest`.

## Formato de almacenamiento

Los expedientes se guardan en `expedientes.txt`, un registro por linea, con los
campos separados por el caracter `|`:

```
codigo|nombre|dni|asunto|fecha|estado|dependencia|historial
EXP-0001|Juan Perez|12345678|Tramite X|2026-10-22|Recibido|Licencias|2026-10-22,Recibido,admin
```

- `estado`: uno de `Recibido`, `En proceso`, `Atendido`.
- `dependencia`: una de `Mesa de Partes`, `Licencias`, `Rentas`, `Obras`, `Secretaria General`.
- `historial`: entradas `fecha,estado,usuario` separadas por `;`
  (ej. `2026-10-22,Recibido,admin;2026-10-23,En proceso,jmesa`).

El programa tambien lee el formato anterior de 5 campos (`codigo|nombre|dni|asunto|fecha`):
esos expedientes quedan como `Recibido`, en `Mesa de Partes`, con historial a nombre de `sistema`,
y se guardan con 8 campos la proxima vez.

## Almacenamiento: texto o SQLite

El programa puede guardar los expedientes en el archivo de texto `expedientes.txt`
o en la base de datos SQLite `mesa_partes.db` (modulo `sqlite3` de la biblioteca estandar).
Se elige con la constante `ALMACENAMIENTO` al inicio de `persistencia.py`:

```python
ALMACENAMIENTO = "txt"      # archivo de texto (valor por defecto)
ALMACENAMIENTO = "sqlite"   # base de datos mesa_partes.db
```

El resto del programa no cambia: todos los modulos llaman a `cargar_desde_archivo()` y
`guardar_en_archivo()`, y `persistencia.py` decide a donde van los datos.

La base tiene dos tablas:

```sql
CREATE TABLE IF NOT EXISTS expedientes (
    codigo      TEXT PRIMARY KEY,
    nombre      TEXT NOT NULL,
    dni         TEXT NOT NULL,
    asunto      TEXT NOT NULL,
    fecha       TEXT NOT NULL,
    estado      TEXT NOT NULL,
    dependencia TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS historial (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo  TEXT NOT NULL REFERENCES expedientes(codigo),
    fecha   TEXT NOT NULL,
    estado  TEXT NOT NULL,
    usuario TEXT NOT NULL
);
```

- `expedientes`: un expediente por fila.
- `historial`: una fila por cada cambio de estado; `codigo` indica a que expediente
  pertenece y `id` conserva el orden de las entradas.

**Migracion automatica:** con `"sqlite"`, si `mesa_partes.db` todavia no existe y
`expedientes.txt` si, al iniciar el programa se copian los expedientes del texto a la base
(se aceptan los formatos de 5 y 8 campos). El `.txt` no se borra.

**Consultas parametrizadas:** todas las consultas usan `?` en lugar de armar el SQL
uniendo texto:

```python
# correcto: sqlite3 separa el dato del codigo SQL
conexion.execute("INSERT INTO expedientes (codigo, nombre, ...) VALUES (?, ?, ...)",
                 (codigo, nombre, ...))

# incorrecto: un nombre como O'Brien rompe la consulta, y un texto malicioso
# podria ejecutar otro SQL (inyeccion SQL)
conexion.execute("INSERT INTO expedientes VALUES ('" + codigo + "', '" + nombre + "', ...)")
```

Con `?`, el dato nunca se interpreta como parte del SQL: se guarda tal cual,
aunque tenga comillas.

## Autenticacion

El acceso al sistema se valida con `autenticacion.py`, que lee `usuarios.txt`
(un usuario por linea, campos separados por `|`):

```
usuario|sal|hash|rol
admin|340787702d2d7f27|7e45cc7c...|administrador
```

La `sal` es un valor aleatorio de 16 caracteres hexadecimales generado con
`secrets.token_hex(8)`; el `hash` es el resumen **SHA-256** de `sal + contrasena`
(nunca se guarda la clave ni su hash sin sal).

Las funciones del modulo solo retornan valores, sin `print` ni `input`:

| Funcion                          | Retorno                                     |
|----------------------------------|---------------------------------------------|
| `verificar_login(usuario, clave)`| tupla `(True, rol)` o `(False, "")`         |
| `usuario_existe(usuario)`        | `True` / `False`                            |
| `agregar_usuario(usuario, clave, rol)` | `True` si registro, `False` si invalido o ya existia |
| `hash_contrasena(clave, sal)`    | hash SHA-256 en hexadecimal                |
| `leer_usuarios()`                | lista de diccionarios `usuario`, `hash`, `rol` |

Usuarios de prueba (el nombre no distingue mayusculas, la contrasena si):

| Usuario | Contrasena | Rol            |
|---------|------------|----------------|
| `admin` | `admin123` | `administrador`|
| `jmesa` | `mesa2026` | `usuario`      |

## Ejecucion

Requiere Python 3 (sin dependencias externas):

```bash
python main.py
```

Al iniciar se pide usuario y contrasena (la contrasena no se muestra al escribir).
Hay **3 intentos**: al tercer error el programa muestra "Acceso bloqueado" y termina.
El rol `administrador` puede usar todas las opciones; el rol `usuario` no puede eliminar.

Menu principal:

1. Registrar expediente (pide nombre, DNI y asunto; repite hasta que sean validos)
2. Buscar expediente por codigo (ej. `EXP-0001`)
3. Buscar por texto en nombre o asunto (sin distinguir mayusculas, ej. `licencia`)
4. Modificar expediente
5. Eliminar expediente
6. Ordenar expedientes (codigo, nombre, dni, asunto o fecha) y mostrarlos en tabla
7. Listar expedientes en tabla
8. Salir (guarda en el almacenamiento configurado: `expedientes.txt` o `mesa_partes.db`)

Las opciones 2 a 7 avisan "No hay expedientes registrados." si la lista esta vacia.

Los listados se muestran como tabla alineada a partir de un **arreglo bidimensional**
(lista de listas): la fila 0 son los encabezados y cada fila siguiente es un expediente.
Los asuntos de mas de 25 caracteres se recortan con `...`.

## Normalizacion y validacion de entradas

Antes de validar, cada dato se normaliza con metodos de cadenas:

| Campo  | Normalizacion                                                  | Ejemplo                              |
|--------|----------------------------------------------------------------|--------------------------------------|
| Nombre | `strip()`, espacios dobles a uno con `replace()`, y `title()`  | `"  juan   perez "` -> `"Juan Perez"` |
| DNI    | se quitan los espacios con `replace(" ", "")`                  | `"1234 5678"` -> `"12345678"`         |
| Asunto | `strip()` y espacios dobles a uno con `replace()`              | `" Reclamo  de  agua"` -> `"Reclamo de agua"` |

Reglas de validacion (se repite la captura hasta que se cumplan):

- Nombre y asunto no vacios y sin el caracter separador `|`.
- DNI de exactamente 8 digitos numericos.

## Equipo

| Integrante | Usuario en Git | Modulos                                         |
|------------|----------------|-------------------------------------------------|
| Fabrizio   | `Angel`        | `expediente.py`, `persistencia.py`, `main.py`    |
| Cristobal  | `Crizzz3`      | `validaciones.py`, `registro.py`, `procesamiento.py`, `autenticacion.py` |

> Nota: los commits de Fabrizio aparecen con el nombre de usuario `Angel`.
