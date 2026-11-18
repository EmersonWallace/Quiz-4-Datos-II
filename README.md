# Quiz-4-Datos-II
# Quiz #4 – NoSQL (Base de datos de documentos)

**Curso:** Algoritmos y Estructuras de Datos II (CE 2103) – II Semestre 2026
**Institución:** Instituto Tecnológico de Costa Rica – Escuela de Ingeniería en Computadores
Emerson Wallace Marin
## Tipo de base de datos seleccionado

**Documentos** – MongoDB, utilizada desde **Python** con la librería `pymongo`.

## Escenario (contexto del problema)

Una tienda de camisas personalizadas permite que cada cliente diseñe su camisa: elige talla y color, agrega
imágenes y textos, y define su posición y escala. Cada pedido es distinto:

- Unos pedidos tienen varias imágenes y textos; otros son camisas lisas sin diseños.
- Algunos incluyen campos extra (por ejemplo, `notas` de entrega) y otros no.
- La estructura de los diseños puede cambiar con el tiempo (nuevos tipos de elementos, fuentes, etc.).

En una base de datos relacional esto implicaría varias tablas (clientes, pedidos, camisas, diseños) con JOINs y
cambios de esquema cada vez que aparezca un atributo nuevo.

## Cómo se resolvió con una base de datos de documentos

Cada pedido se guarda como **un solo documento JSON** que contiene toda su información, con datos anidados y
arreglos:

```json
{
  "cliente": { "nombre": "Ana Mora", "correo": "ana@example.com" },
  "camisa": { "talla": "M", "color": "#1e88e5", "cuello": "redondo" },
  "disenos": [
    { "tipo": "imagen", "archivo": "logo_tec.png", "x": 120, "y": 80, "escala": 0.8 },
    { "tipo": "texto", "contenido": "Ingeniería", "fuente": "Arial", "x": 100, "y": 220 }
  ],
  "cantidad": 2,
  "precio_unitario": 9500,
  "estado": "pendiente"
}
```

Ventajas aprovechadas:

- **Esquema flexible:** los documentos de una misma colección pueden tener campos distintos.
- **Datos anidados y arreglos:** los diseños viven dentro del pedido, sin JOINs.
- **Consultas sobre campos anidados:** por ejemplo `cliente.correo` o `disenos.tipo`.
- **Aggregation pipeline:** cálculo de ingresos por estado directamente en la base de datos.

## Operaciones que muestra el programa (`app.py`)

| # | Operación | Método de pymongo |
|---|-----------|-------------------|
| 1 | Insertar varios pedidos | `insert_many` |
| 2 | Buscar por campo anidado | `find_one({"cliente.correo": ...})` |
| 3 | Buscar dentro de un arreglo | `find({"disenos.tipo": "imagen"})` |
| 4 | Filtrar y ordenar | `find({"cantidad": {"$gte": 2}}).sort(...)` |
| 5 | Actualizar y agregar elementos a un arreglo | `update_one` con `$set` y `$push`; `update_many` |
| 6 | Agregación (total por estado) | `aggregate` con `$project`, `$group`, `$sort` |
| 7 | Eliminar | `delete_one` |
| – | Índice sobre `cliente.correo` | `create_index` |

## Requisitos

- Python 3.9 o superior
- Docker (para levantar MongoDB) o una instalación local de MongoDB

## Cómo ejecutar

```bash
# 1. Levantar MongoDB
docker compose up -d

# 2. Instalar dependencias
python -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Ejecutar el programa
python app.py
```

Si MongoDB corre en otra dirección, se puede definir la variable de entorno `MONGO_URI`
(por defecto `mongodb://localhost:27017`).

Para detener la base de datos: `docker compose down`.

## Estructura del repositorio

```
.
├── app.py               # Programa principal (CRUD + agregación)
├── requirements.txt     # Dependencias de Python
├── docker-compose.yml   # MongoDB listo para usar
└── README.md
```
