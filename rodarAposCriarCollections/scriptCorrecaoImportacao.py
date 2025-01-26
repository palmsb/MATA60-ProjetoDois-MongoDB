from pymongo import MongoClient

# Conexão com o MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["Projetov2"]

# --------------> Função para corrigir tabelas (collections) de relacionamento
def corrigir_colecao(nome_colecao, id_campos):
    colecao = db[nome_colecao].find()
    for doc in colecao:
        # Cria o novo _id composto
        composite_id = "_".join(str(doc[campo]) for campo in id_campos)
        
        # Cria um novo documento com o _id composto
        novo_doc = doc.copy()  # Copia o documento original
        novo_doc["_id"] = composite_id
        
        # Remove o documento antigo e insere o novo
        db[nome_colecao].delete_one({"_id": doc["_id"]})  # Remove o documento original
        db[nome_colecao].insert_one(novo_doc)  # Insere o documento com o _id corrigido


corrigir_colecao("guia_trilha", ["id_guia", "id_trilha"])

corrigir_colecao("reserva_trilha", ["id_reserva", "id_trilha"])




#-------------> Função para converter o campo `data` para o tipo Date

# Conexão com o MongoDB
reserva_collection = db["reserva"]  

def atualizar_datas():
    # Localizar todos os documentos que possuem o campo `data`
    reservas = reserva_collection.find({"data": {"$exists": True}})
    for reserva in reservas:
        try:
            # Tenta converter a data para um formato válido
            data_string = reserva["data"]
            nova_data = datetime.strptime(data_string, "%Y-%m-%d")  # Ajuste o formato conforme necessário
            reserva_collection.update_one(
                {"_id": reserva["_id"]},  # Localiza pelo ID
                {"$set": {"data": nova_data}}  # Atualiza o campo `data` com o tipo Date
            )
            print(f"Atualizado: {reserva['_id']} -> {nova_data}")
        except Exception as e:
            print(f"Erro ao atualizar reserva {reserva['_id']}: {e}")

# Chamada da função
atualizar_datas()


