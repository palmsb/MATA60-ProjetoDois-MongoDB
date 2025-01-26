from pymongo import MongoClient
from datetime import datetime, timedelta

# Conectar ao MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["Projetov2"]

# Consultas
def trilha_com_mais_reservas():
    pipeline = [
        {"$lookup": {"from": "reserva_trilha", "localField": "_id", "foreignField": "id_trilha", "as": "reservas"}},
        {"$unwind": "$reservas"},
        {"$group": {"_id": "$_id", "nome": {"$first": "$nome"}, "total_reservas": {"$sum": 1}}},
        {"$sort": {"total_reservas": -1}},
        {"$limit": 1}
    ]
    resultados = db.trilha.aggregate(pipeline)
    print("\nTrilha com maior número de reservas:")
    for resultado in resultados:
        print(resultado)

def visitantes_unicos_reservas():
    total_visitantes = db.reserva.distinct("id_visitante")
    print(f"\nTotal de visitantes únicos: {len(total_visitantes)}")

def trilhas_capacidade_maior_20():
    trilhas = db.trilha.find(
        {"capacidade_max": {"$gt": 20}},
        {"_id": 0, "nome": 1, "capacidade_max": 1}
    )
    print("\nTrilhas com capacidade máxima > 20:")
    for trilha in trilhas:
        print(trilha)

def reservas_ativas():
    total_ativas = db.reserva.count_documents({"status_reserva": "Confirmado"})
    print(f"\nTotal de reservas ativas: {total_ativas}")

def trilha_guia_maior_reservas():
    pipeline = [
        {
            "$lookup": {
                "from": "guia_trilha",
                "localField": "id_trilha",
                "foreignField": "id_trilha",
                "as": "guias"
            }
        },
        {
            "$lookup": {
                "from": "reserva_trilha",
                "localField": "id_trilha",
                "foreignField": "id_trilha",
                "as": "reservas"
            }
        },
        {
            "$match": {"$expr": {"$gt": [{"$size": "$guias"}, 2]}}
        },
        {
            "$project": {
                "trilha_nome": "$nome",
                "total_reservas": {"$size": "$reservas"}
            }
        },
        {"$sort": {"total_reservas": -1}},
        {"$limit": 1}
    ]
    result = db.trilha.aggregate(pipeline)
    print("\nTrilha conduzida por mais de 2 guias com maior número de reservas:")
    for item in result:
        print(item)

def visitantes_trilhas_avancadas():
    pipeline = [
        {
            "$lookup": {
                "from": "reserva_trilha",
                "localField": "id_trilha",
                "foreignField": "id_trilha",
                "as": "reservas"
            }
        },
        {"$match": {"nivel_dificuldade": "Avançado"}},
        {
            "$group": {
                "_id": None,
                "total_visitantes": {"$addToSet": "$reservas.id_visitante"}
            }
        },
        {
            "$project": {
                "total_visitantes": {"$size": "$total_visitantes"}
            }
        }
    ]
    result = db.trilha.aggregate(pipeline)
    print("\nTotal de visitantes que reservaram trilhas avançadas:")
    for item in result:
        print(item)

def guias_mais_ativos():
    pipeline = [
        {"$lookup": {"from": "guia_trilha", "localField": "_id", "foreignField": "id_guia", "as": "trilhas"}},
        {"$unwind": "$trilhas"},
        {"$lookup": {"from": "reserva_trilha", "localField": "trilhas.id_trilha", "foreignField": "id_trilha", "as": "reservas"}},
        {"$unwind": "$reservas"},
        {"$group": {"_id": "$_id", "nome": {"$first": "$nome"}, "total_reservas": {"$sum": 1}}},
        {"$sort": {"total_reservas": -1}},
        {"$limit": 5}
    ]
    resultados = db.guia.aggregate(pipeline)
    print("\nGuias mais ativos:")
    for resultado in resultados:
        print(resultado)

def guia_maior_numero_visitantes_unicos():
    pipeline = [
        {"$lookup": {"from": "guia_trilha", "localField": "_id", "foreignField": "id_guia", "as": "trilhas"}},
        {"$unwind": "$trilhas"},
        {"$lookup": {"from": "reserva_trilha", "localField": "trilhas.id_trilha", "foreignField": "id_trilha", "as": "reservas"}},
        {"$unwind": "$reservas"},
        {"$lookup": {"from": "reserva", "localField": "reservas.id_reserva", "foreignField": "_id", "as": "detalhes_reservas"}},
        {"$unwind": "$detalhes_reservas"},
        {"$group": {"_id": "$_id", "nome": {"$first": "$nome"}, "visitantes_unicos": {"$addToSet": "$detalhes_reservas.id_visitante"}}},
        {"$project": {"nome": 1, "total_visitantes": {"$size": "$visitantes_unicos"}}},
        {"$sort": {"total_visitantes": -1}},
        {"$limit": 1}
    ]
    resultados = db.guia.aggregate(pipeline)
    print("\nGuia com maior número de visitantes únicos:")
    for resultado in resultados:
        print(resultado)

if __name__ == "__main__":
    print("Escolha a consulta para executar:")
    print("1. Trilha com maior número de reservas")
    print("2. Total de visitantes únicos com reservas")
    print("3. Trilhas com capacidade máxima > 20")
    print("4. Total de reservas ativas")
    print("5. Trilha conduzida por mais de 2 guias com maior número de reservas")
    print("6. Visitantes que reservaram trilhas avançadas")
    print("7. Os 5 guias mais ativos")
    print("8. Guia com maior número de visitantes únicos")
    print("0. Sair")

    while True:
        escolha = input("Digite o número da consulta: ")
        if escolha == '0':
            print("Encerrando Consultas...")
            break
        elif escolha == "1":
            trilha_com_mais_reservas()
        elif escolha == "2":
            visitantes_unicos_reservas()
        elif escolha == "3":
            trilhas_capacidade_maior_20()
        elif escolha == "4":
            reservas_ativas()
        elif escolha == "5":
            trilha_guia_maior_reservas()
        elif escolha == "6":
            visitantes_trilhas_avancadas()
        elif escolha == "7":
            guias_mais_ativos()
        elif escolha == "8":
            guia_maior_numero_visitantes_unicos()
        else:
            print("Opção inválida! Tente outro valor.")
