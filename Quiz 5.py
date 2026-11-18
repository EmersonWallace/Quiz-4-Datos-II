"""
Quiz #4 - NoSQL (CE 2103 - Algoritmos y Estructuras de Datos II)
"""

import os
from datetime import datetime, timezone

from pymongo import ASCENDING, MongoClient
from pymongo.errors import PyMongoError

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "tienda_camisas"
COLECCION = "pedidos"


def titulo(texto):
    print(f"\n=== {texto} ===")


def conectar():
    """Se conecta a MongoDB y devuelve la colección de pedidos."""
    cliente = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    cliente.admin.command("ping")  # falla si el servidor no está disponible
    return cliente[DB_NAME][COLECCION]


def pedidos_de_ejemplo():
    ahora = datetime.now(timezone.utc)
    return [
        {
            "cliente": {"nombre": "Ana Mora", "correo": "ana@example.com"},
            "camisa": {"talla": "M", "color": "#1e88e5", "cuello": "redondo"},
            "disenos": [
                {"tipo": "imagen", "archivo": "logo_tec.png", "x": 120, "y": 80, "escala": 0.8},
                {"tipo": "texto", "contenido": "Ingeniería", "fuente": "Arial", "x": 100, "y": 220},
            ],
            "cantidad": 2,
            "precio_unitario": 9500,
            "estado": "pendiente",
            "creado": ahora,
        },
        {
            "cliente": {"nombre": "Luis Rojas", "correo": "luis@example.com"},
            "camisa": {"talla": "L", "color": "#e53935"},
            "disenos": [
                {"tipo": "imagen", "archivo": "dragon.png", "x": 90, "y": 60, "escala": 1.2},
            ],
            "cantidad": 1,
            "precio_unitario": 11000,
            "estado": "pendiente",
            "notas": "Entregar en Cartago centro",  # campo que otros pedidos no tienen
            "creado": ahora,
        },
        {
            "cliente": {"nombre": "Sofía Vargas", "correo": "sofia@example.com"},
            "camisa": {"talla": "S", "color": "#43a047", "cuello": "V"},
            "disenos": [],  # camisa lisa
            "cantidad": 5,
            "precio_unitario": 8000,
            "estado": "pendiente",
            "creado": ahora,
        },
    ]


def main():
    try:
        pedidos = conectar()
    except PyMongoError as e:
        print("No se pudo conectar a MongoDB. ¿Está corriendo (docker compose up -d)?")
        print(f"Detalle: {e}")
        return

    # Se limpia la colección para que la demo sea repetible.
    pedidos.drop()

    titulo("1. CREATE: insertar pedidos (insert_many)")
    resultado = pedidos.insert_many(pedidos_de_ejemplo())
    print(f"Pedidos insertados: {len(resultado.inserted_ids)}")

    # Índice para acelerar búsquedas por correo del cliente.
    pedidos.create_index([("cliente.correo", ASCENDING)], unique=False)

    titulo("2. READ: buscar por campo anidado (cliente.correo)")
    ana = pedidos.find_one({"cliente.correo": "ana@example.com"})
    print(f"Pedido de {ana['cliente']['nombre']}: {len(ana['disenos'])} diseños")

    titulo("3. READ: pedidos con al menos un diseño de tipo 'imagen'")
    for p in pedidos.find({"disenos.tipo": "imagen"}, {"cliente.nombre": 1, "cantidad": 1}):
        print(f"- {p['cliente']['nombre']} (cantidad: {p['cantidad']})")

    titulo("4. READ: pedidos de 2 o más camisas, ordenados por cantidad")
    for p in pedidos.find({"cantidad": {"$gte": 2}}).sort("cantidad", -1):
        print(f"- {p['cliente']['nombre']}: {p['cantidad']} camisas")

    titulo("5. UPDATE: cambiar estado y agregar un diseño con $push")
    pedidos.update_one(
        {"cliente.correo": "luis@example.com"},
        {
            "$set": {"estado": "en_produccion"},
            "$push": {"disenos": {"tipo": "texto", "contenido": "Dragón", "fuente": "Impact", "x": 110, "y": 250}},
        },
    )
    luis = pedidos.find_one({"cliente.correo": "luis@example.com"})
    print(f"Luis -> estado: {luis['estado']}, diseños: {len(luis['disenos'])}")

    pedidos.update_many({"estado": "pendiente"}, {"$set": {"estado": "confirmado"}})
    print("Pedidos pendientes pasados a 'confirmado'.")


    titulo("6. AGGREGATE: total vendido por estado")
    pipeline = [
        {"$project": {"estado": 1, "total": {"$multiply": ["$cantidad", "$precio_unitario"]}}},
        {"$group": {"_id": "$estado", "pedidos": {"$sum": 1}, "ingresos": {"$sum": "$total"}}},
        {"$sort": {"ingresos": -1}},
    ]
    for fila in pedidos.aggregate(pipeline):
        print(f"- {fila['_id']}: {fila['pedidos']} pedido(s), ₡{fila['ingresos']:,}")


    titulo("7. DELETE: eliminar el pedido de Sofía")
    borrado = pedidos.delete_one({"cliente.correo": "sofia@example.com"})
    print(f"Documentos eliminados: {borrado.deleted_count}")
    print(f"Pedidos restantes: {pedidos.count_documents({})}")


if __name__ == "__main__":
    main()
