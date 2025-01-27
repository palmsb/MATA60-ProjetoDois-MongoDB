from pymongo import MongoClient
from datetime import datetime, timedelta

# Conectar ao MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["ProjetoDoisDemo"]

# Consultas
def trilha_capacidade_maxima_maior_10():
    trilhas = db.trilha.find({"capacidade_max": {"$gt": 10}}, {"_id": 0, "nome": 1, "capacidade_max": 1})
    print("\nTrilhas com capacidade máxima > 10:")
    for trilha in trilhas:
        print(trilha)

def reservas_confirmadas():
    reservas = db.reserva.find({"status_reserva": "Confirmado"})
    print("\nReservas confirmadas:")
    for reserva in reservas:
        print(reserva)

def visitantes_com_reservas_canceladas():
    pipeline = [
        {"$lookup": {"from": "reserva", "localField": "_id", "foreignField": "id_visitante", "as": "reservas"}},
        {"$unwind": "$reservas"},
        {"$match": {"reservas.status_reserva": "Cancelado"}},
        {"$project": {"_id": 0, "nome": 1, "contato": 1}}
    ]
    resultados = db.visitante.aggregate(pipeline)
    print("\nVisitantes com reservas canceladas:")
    for resultado in resultados:
        print(resultado)

def visitante_com_mais_reservas():
    pipeline = [
        {"$lookup": {"from": "reserva", "localField": "_id", "foreignField": "id_visitante", "as": "reservas"}},
        {"$unwind": "$reservas"},
        {"$match": {"reservas.data": {"$gte": datetime(2024, 1, 1), "$lte": datetime(2024, 12, 31)}}},
        {"$lookup": {"from": "reserva_trilha", "localField": "reservas._id", "foreignField": "id_reserva", "as": "reserva_trilha"}},
        {"$lookup": {"from": "trilha", "localField": "reserva_trilha.id_trilha", "foreignField": "_id", "as": "trilhas"}},
        {"$group": {
            "_id": {"id_visitante": "$_id", "nome": "$nome"},
            "total_reservas": {"$sum": 1},
            "trilhas_reservadas": {"$addToSet": "$trilhas.nome"}
        }},
        {"$sort": {"total_reservas": -1}},
        {"$limit": 1}
    ]
    resultados = db.visitante.aggregate(pipeline)
    print("\nVisitante com mais reservas no ano:")
    for resultado in resultados:
        print(resultado)

def nome_contato_visitantes():
    visitantes = db.visitante.find({}, {"_id": 0, "nome": 1, "contato": 1})
    print("\nNome e Contato dos Visitantes:")
    for visitante in visitantes:
        print(visitante)

def guias_experiencia_maior_que5():
    guias = db.guia.find({"experiencia": {"$gt": 5}}, {"_id": 0, "nome": 1})
    print("\nGuias com experiência > 5 anos:")
    for guia in guias:
        print(guia)

def trilhas_das_reservas_confirmadas():
    pipeline = [
        {"$lookup": {"from": "trilha", "localField": "id_trilha", "foreignField": "_id", "as": "trilha"}},
        {"$lookup": {"from": "reserva", "localField": "id_reserva", "foreignField": "_id", "as": "reserva"}},
        {"$unwind": "$trilha"},
        {"$unwind": "$reserva"},
        {"$match": {"reserva.status_reserva": "Confirmado"}},
        {"$project": {"_id": 0, "trilha.nome": 1, "reserva.data": 1, "reserva.turno": 1}}
    ]
    resultados = db.reserva_trilha.aggregate(pipeline)
    print("\nTrilhas associadas a reservas confirmadas:")
    for resultado in resultados:
        print(resultado)

def total_reserva_por_trilha():
    pipeline = [
        {"$lookup": {"from": "trilha", "localField": "id_trilha", "foreignField": "_id", "as": "trilha"}},
        {"$unwind": "$trilha"},
        {"$group": {"_id": "$trilha.nome", "total_reservas": {"$sum": 1}}},
        {"$project": {"_id": 0, "trilha_nome": "$_id", "total_reservas": 1}}
    ]
    resultados = db.reserva_trilha.aggregate(pipeline)
    print("\nTotal de reservas por trilha:")
    for resultado in resultados:
        print(resultado)

def trilha_maior_reserva_guia():
    two_years_ago = datetime.now() - timedelta(days=2 * 365)  # Últimos 2 anos
    pipeline = [
        {"$lookup": {"from": "reserva_trilha", "localField": "_id", "foreignField": "id_trilha", "as": "reserva_trilha"}},
        {"$unwind": "$reserva_trilha"},
        {"$lookup": {"from": "reserva", "localField": "reserva_trilha.id_reserva", "foreignField": "_id", "as": "reserva"}},
        {"$unwind": "$reserva"},
        {"$match": {"reserva.data": {"$gte": two_years_ago}, "reserva.status_reserva": "Confirmado"}},
        {"$group": {"_id": "$_id", "nome": {"$first": "$nome"}, "total_reservas": {"$sum": 1}}},
        {"$sort": {"total_reservas": -1}},
        {"$limit": 5}
    ]
    resultados = db.trilha.aggregate(pipeline)
    print("\nTrilhas com maior número de reservas nos últimos 2 anos:")
    for resultado in resultados:
        print(resultado)


if __name__ == "__main__":
    print("Escolha a consulta para executar:")
    print("1. Trilhas com capacidade máxima > 10")
    print("2. Reservas confirmadas")
    print("3. Visitantes com reservas canceladas")
    print("4. Visitante com mais reservas (Anual)")
    print("5. Nome e Contato dos Visitantes")
    print("6. Guias com Experiência > 5")
    print("7. Trilhas Associadas a Reservas Confirmadas")
    print("8. Total de Reservas por Trilha")
    print("9. Trilhas com Maior Média de Reservas por Guia (Últimos 2 Anos)")
    print("0. Sair")

    while True:
        escolha = input("Digite o número da consulta: ")
        if escolha == '0':
            print("Encerrando Consultas...")
            break
        elif escolha == "1":
            trilha_capacidade_maxima_maior_10()
        elif escolha == "2":
            reservas_confirmadas()
        elif escolha == "3":
            visitantes_com_reservas_canceladas()
        elif escolha == "4":
            visitante_com_mais_reservas()
        elif escolha == "5":
            nome_contato_visitantes()
        elif escolha == "6":
            guias_experiencia_maior_que5()
        elif escolha == "7":
            trilhas_das_reservas_confirmadas()
        elif escolha == "8":
            total_reserva_por_trilha()
        elif escolha == "9":
            trilha_maior_reserva_guia()
        else:
            print("Opção inválida! Tente outro valor.")