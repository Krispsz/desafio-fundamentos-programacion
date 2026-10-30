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
| `integridad.py`    | Revision de los datos leidos del archivo (avisa sin descartar)        |
| `validaciones.py`  | Normalizacion y validacion de los datos ingresados por el usuario    |
| `registro.py`      | Registro y modificacion de expedientes (con validacion en bucle)     |
| `procesamiento.py` | Busquedas (codigo y texto), tabla, ordenamiento burbuja, eliminacion |
| `autenticacion.py` | Login con usuarios.txt: hash SHA-256, retorna True/False y el rol    |
| `main.py`          | Menu principal e integracion de todos los modulos                    |
| `gui.py`           | Interfaz grafica (tkinter): login, ventana principal, registro, detalle y modificacion |

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

## Validacion de integridad al cargar

`integridad.py` revisa cada expediente reconstruido. Si un expediente tiene
problemas se **conserva** en la lista y se informa el motivo: descartarlo haria
que el siguiente guardado lo borre del archivo, porque `guardar_en_txt()`
sobrescribe el archivo completo. Se reporta cuando:

- el codigo no tiene la forma `EXP-####`;
- el nombre o el asunto estan vacios o contienen el separador `|`;
- el DNI no tiene exactamente 8 digitos;
- la fecha no es una fecha real con formato `AAAA-MM-DD` (por ejemplo, `2026-02-30`);
- el estado no esta en `Recibido`, `En proceso`, `Atendido`;
- la dependencia no esta en el catalogo de `expediente.py`;
- el historial esta vacio o tiene entradas con fecha, estado o usuario invalidos;
- el codigo ya aparecio en una linea anterior (codigo repetido).

La revision deja intactos los formatos validos: una linea de 5 campos sigue
cargandose con sus valores por defecto. La lectura usa `encoding="utf-8-sig"`
para aceptar el archivo con y sin BOM: el BOM pegado al primer codigo lo sacaba
de formato y ese expediente se perdia al guardar.

| Funcion | Retorno |
|---|---|
| `fecha_valida(texto)` | `True` si es una fecha real `AAAA-MM-DD` |
| `revisar_expediente(expediente)` | lista de motivos; vacia si esta integro |
| `revisar_lista(expedientes)` | tupla `(validos, rechazos)`, cada rechazo `{"codigo", "motivo"}` |
| `resumir_rechazos(rechazos)` | texto corto con los codigos a corregir y su motivo |

`persistencia.cargar_con_informe(ruta)` retorna `(expedientes, rechazos)` con
**todos** los expedientes leidos; `cargar_desde_archivo()` tambien devuelve la
lista completa, asi que la ventana y las pruebas anteriores no cambian. La
consola y la ventana avisan al iniciar:

```
Expedientes cargados: 6
4 expedientes tienen datos invalidos y deben corregirse: EXP-0002 (dni invalido); ...
```

El aviso es informativo: el expediente sigue en la lista y se puede corregir
con la opcion Modificar o con la ventana. Solo las lineas que no se pueden
convertir en expediente (otro numero de campos) se saltan, y desde la version
1.0 se saltaban igual.

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

## Interfaz grafica

Ademas de la consola (`python main.py`, sin cambios), el sistema tiene una interfaz
grafica hecha con `tkinter` (biblioteca estandar):

```bash
python gui.py
```

- **Inicio de sesion:** usuario y contrasena (oculta con `*`), boton "Ingresar" o tecla Enter.
  Usa `verificar_login()` de `autenticacion.py`. Hay **3 intentos**: se muestran los intentos
  restantes y al tercer error aparece "Acceso bloqueado" y la ventana se cierra.
- **Ventana principal:** arriba `Usuario: <usuario> (<rol>)`; a la izquierda los botones
  Registrar, Listar / Buscar, Ver expediente y Salir; a la derecha el marco `area_contenido`,
  donde se dibuja cada vista. Al abrir carga los expedientes con `cargar_desde_archivo()` y al salir (boton
  Salir o la X de la ventana) guarda con `guardar_en_archivo()`.
- **Registrar:** formulario con Nombre, DNI, Asunto y una lista de solo lectura con las
  dependencias. Usa `preparar_datos()` y `crear_registro()` de `registro.py`, las mismas
  funciones que la consola.
- **Ver expediente:** campo Codigo y boton "Buscar" (el codigo se pasa a mayusculas, asi
  `exp-0001` tambien sirve). Muestra los datos del expediente (codigo, nombre, DNI, asunto,
  fecha, estado y dependencia) y su **historial** en una tabla de solo lectura con las columnas
  Fecha, Estado y Usuario, en el orden guardado. Si el codigo no existe muestra
  "Expediente no encontrado". La vista la dibuja `mostrar_detalle(contenedor, expedientes,
  codigo, usuario, rol)`, que tambien puede llamar la tabla de expedientes.
- **Modificar:** desde el detalle, el boton "Modificar" abre un formulario con Nombre, DNI y
  Asunto ya llenos; estado y dependencia solo se muestran (se cambian en otra tarea).
  "Guardar cambios" usa `preparar_datos()` y `aplicar_modificacion()` de `registro.py`
  (a traves de `procesar_modificacion()`), que conservan fecha, estado, dependencia e
  historial. "Cancelar" vuelve al detalle sin cambiar nada.

Igual que en la consola, `gui.py` solo arma los widgets: la logica sigue en los otros modulos.

### Contrato para la tabla de expedientes (tarea 13)

El boton "Listar / Buscar" limpia `area_contenido` y llama a una funcion de `gui_tabla.py`
con esta firma exacta:

```python
def mostrar_tabla(contenedor, expedientes, usuario, rol):
```

| Parametro     | Que es                                                                 |
|---------------|------------------------------------------------------------------------|
| `contenedor`  | el `Frame` `area_contenido` (ya vacio): la tabla se dibuja **dentro** de el |
| `expedientes` | la lista de diccionarios cargada al iniciar (la misma que usa el resto de la GUI) |
| `usuario`     | nombre del usuario que inicio sesion (ej. `admin`)                     |
| `rol`         | `administrador` o `usuario`                                            |

Lo que se espera de `mostrar_tabla`:

- Dibujar todo dentro de `contenedor` (no crear otra ventana `Tk`).
- Modificar la lista `expedientes` **en el lugar** (por ejemplo con `pop`), sin reemplazarla
  por otra lista, para que la ventana principal guarde los cambios al salir.
- Para eliminar, usar `eliminar_por_codigo(expedientes, codigo)` de `procesamiento.py`, que ya
  guarda y retorna `(eliminado, guardado)`.
- Mostrar o habilitar la opcion de eliminar **solo si `rol == "administrador"`**.
- Para abrir el detalle de una fila (por ejemplo con doble clic), llamar a
  `gui.mostrar_detalle(contenedor, expedientes, codigo, usuario, rol)`. Importar `gui`
  **dentro** de la funcion que lo usa, no al inicio del archivo, para evitar una importacion
  circular (`gui.py` importa `gui_tabla.py`):

  ```python
  def abrir_detalle(contenedor, expedientes, codigo, usuario, rol):
      import gui
      gui.limpiar(contenedor)
      gui.mostrar_detalle(contenedor, expedientes, codigo, usuario, rol)
  ```

Mientras `gui_tabla.py` no exista, el boton muestra "Tabla de expedientes: en desarrollo (tarea 13)".

## Pruebas automaticas

Las pruebas usan `unittest` (biblioteca estandar) y estan en la carpeta `tests/`.
Se ejecutan desde la raiz del repositorio:

```bash
python -m unittest discover -s tests -v
```

| Archivo                       | Que cubre                                                       |
|-------------------------------|-----------------------------------------------------------------|
| `tests/test_expediente.py`    | `crear_expediente` (valores por defecto e historial), ida y vuelta entre `historial_a_texto` y `texto_a_historial`, y `generar_codigo` (mayor + 1, cuatro digitos) |
| `tests/test_persistencia.py`  | Modo `"txt"`: guardar y cargar con historial, formato viejo de 5 campos, lineas vacias o mal formadas, archivo inexistente, bytes invalidos y error al guardar |
| `tests/test_persistencia_db.py` | SQLite: creacion de tablas, guardar y cargar con historial en orden, nombres con apostrofe (`O'Brien`), borrado del historial, base inexistente, `migrar_txt_a_db` y migracion automatica en modo `"sqlite"` |
| `tests/test_integridad.py`    | Rutina de integridad: fechas reales y formatos invalidos, DNI de 8 digitos, nombre y asunto vacios, estado y dependencia fuera del catalogo, historial invalido, codigo repetido, resumen de rechazos y carga real de un archivo con lineas corruptas |

Cada prueba trabaja en una **carpeta temporal** (`tempfile.TemporaryDirectory()`) que se
crea en `setUp` y se borra en `tearDown`: las pruebas nunca tocan los `expedientes.txt`,
`usuarios.txt` ni `mesa_partes.db` reales. Si una prueba cambia `persistencia.ALMACENAMIENTO`
o `persistencia_db.RUTA_DB`, el valor original se restaura al terminar.

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
