
//1. Trilhas com capacidade máxima > 10
db.trilha.find(
    { capacidade_max: { $gt: 10 } },
    { nome: 1, capacidade_max: 1, _id: 0 }
);

//2. Reservas confirmadas
db.reserva.find(
    { status_reserva: "Confirmado" }
);

//3. Nome e contato dos visitantes
db.visitante.find(
    {},
    { nome: 1, contato: 1, _id: 0 }
);

//4. Guias com experiência > 5
db.guia.find(
    { experiencia: { $gt: 5 } },
    { nome: 1, _id: 0 }
);

//5. Trilhas associadas a reservas confirmadas
ddb.reserva_trilha.aggregate([
    { $lookup: { from: "trilha", localField: "id_trilha", foreignField: "_id", as: "trilha" } },
    { $lookup: { from: "reserva", localField: "id_reserva", foreignField: "_id", as: "reserva" } },
    { $unwind: "$trilha" },
    { $unwind: "$reserva" },
    { $match: { "reserva.status_reserva": "Confirmado" } },
    { $project: { "_id": 0, "trilha.nome": 1, "reserva.data": 1, "reserva.turno": 1 } }
]);


//6.Total de reservas por trilha:
db.reserva_trilha.aggregate([
    { $lookup: { from: "trilha", localField: "id_trilha", foreignField: "_id", as: "trilha" } },
    { $unwind: "$trilha" },
    { $group: { _id: "$trilha.nome", total_reservas: { $sum: 1 } } },
    { $project: { _id: 0, trilha_nome: "$_id", total_reservas: 1 } }
]);



//7. Visitantes com reservas canceladas
db.visitante.aggregate([
    { $lookup: { from: "reserva", localField: "_id", foreignField: "id_visitante", as: "reservas" } },
    { $unwind: "$reservas" },
    { $match: { "reservas.status_reserva": "Cancelado" } },
    { $project: { "_id": 0, "nome": 1, "contato": 1 } }
]);

//8. Visitante com mais reservas em um ano
db.visitante.aggregate([
    { $lookup: { from: "reserva", localField: "_id", foreignField: "id_visitante", as: "reservas" } },
    { $unwind: "$reservas" },
    { $match: { "reservas.data": { $gte: new Date("2024-01-01"), $lte: new Date("2024-12-31") } } },
    { $lookup: { from: "reserva_trilha", localField: "reservas._id", foreignField: "id_reserva", as: "reserva_trilha" } },
    { $lookup: { from: "trilha", localField: "reserva_trilha.id_trilha", foreignField: "_id", as: "trilhas" } },
    { $group: {
        _id: { id_visitante: "$_id", nome: "$nome" },
        total_reservas: { $sum: 1 },
        trilhas_reservadas: { $addToSet: "$trilhas.nome" }
    }},
    { $sort: { total_reservas: -1 } },
    { $limit: 1 }
]);


//9. Trilhas com maior média de reservas por guia nos últimos 2 anos
db.trilha.aggregate([
    { $lookup: { from: "reserva_trilha", localField: "_id", foreignField: "id_trilha", as: "reserva_trilha" } },
    { $unwind: "$reserva_trilha" },
    { $lookup: { from: "reserva", localField: "reserva_trilha.id_reserva", foreignField: "_id", as: "reserva" } },
    { $unwind: "$reserva" },
    { $match: {
        "reserva.data": { $gte: new Date(new Date().setFullYear(new Date().getFullYear() - 2)) },
        "reserva.status_reserva": "Confirmado"
    }},
    { $group: { _id: "$_id", nome: { $first: "$nome" }, total_reservas: { $sum: 1 } } },
    { $sort: { total_reservas: -1 } },
    { $limit: 5 }
]);



