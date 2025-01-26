
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
db.reserva_trilha.aggregate([
    {
        $lookup: {
            from: "trilha",
            localField: "id_trilha",
            foreignField: "id_trilha",
            as: "trilha"
        }
    },
    {
        $lookup: {
            from: "reserva",
            localField: "id_reserva",
            foreignField: "id_reserva",
            as: "reserva"
        }
    },
    { $unwind: "$trilha" },
    { $unwind: "$reserva" },
    { $match: { "reserva.status_reserva": "Confirmado" } },
    {
        $project: {
            "trilha.nome": 1,
            "reserva.data": 1,
            "reserva.turno": 1,
            _id: 0
        }
    }
]);

//6.Total de reservas por trilha:
db.reserva_trilha.aggregate([
    {
        $lookup: {
            from: "trilha",
            localField: "id_trilha",
            foreignField: "id_trilha",
            as: "trilha"
        }
    },
    { $unwind: "$trilha" },
    {
        $group: {
            _id: "$trilha.nome",
            total_reservas: { $sum: 1 }
        }
    },
    {
        $project: {
            nome: "$_id",
            total_reservas: 1,
            _id: 0
        }
    }
]);


//7. Visitantes com reservas canceladas
db.reserva.aggregate([
    {
        $match: { status_reserva: "Cancelado" }
    },
    {
        $lookup: {
            from: "visitante",
            localField: "id_visitante",
            foreignField: "id_visitante",
            as: "visitante"
        }
    },
    { $unwind: "$visitante" },
    {
        $project: {
            "visitante.nome": 1,
            "visitante.contato": 1,
            _id: 0
        }
    }
]);

//8. Visitante com mais reservas em um ano
db.reserva.aggregate([
    {
        $match: {
            data: { $gte: new Date("2024-01-01"), $lte: new Date("2024-12-31") }
        }
    },
    {
        $lookup: {
            from: "visitante",
            localField: "id_visitante",
            foreignField: "id_visitante",
            as: "visitante"
        }
    },
    {
        $lookup: {
            from: "reserva_trilha",
            localField: "id_reserva",
            foreignField: "id_reserva",
            as: "reserva_trilha"
        }
    },
    { $unwind: "$visitante" },
    { $unwind: "$reserva_trilha" },
    {
        $lookup: {
            from: "trilha",
            localField: "reserva_trilha.id_trilha",
            foreignField: "id_trilha",
            as: "trilha"
        }
    },
    { $unwind: "$trilha" },
    {
        $group: {
            _id: "$id_visitante",
            nome: { $first: "$visitante.nome" },
            total_reservas: { $sum: 1 },
            trilhas_reservadas: { $addToSet: "$trilha.nome" }
        }
    },
    {
        $project: {
            nome: 1,
            total_reservas: 1,
            trilhas_reservadas: { $reduce: { input: "$trilhas_reservadas", initialValue: "", in: { $concat: ["$$value", ", ", "$$this"] } } }
        }
    },
    { $sort: { total_reservas: -1 } },
    { $limit: 1 }
]);

//9. Trilhas com maior média de reservas por guia nos últimos 2 anos
db.trilha.aggregate([
    {
        $lookup: {
            from: "guia_trilha",
            localField: "id_trilha",
            foreignField: "id_trilha",
            as: "guia_trilha"
        }
    },
    { $unwind: "$guia_trilha" },
    {
        $lookup: {
            from: "guia",
            localField: "guia_trilha.id_guia",
            foreignField: "id_guia",
            as: "guia"
        }
    },
    { $unwind: "$guia" },
    {
        $lookup: {
            from: "reserva_trilha",
            localField: "id_trilha",
            foreignField: "id_trilha",
            as: "reserva_trilha"
        }
    },
    { $unwind: "$reserva_trilha" },
    {
        $lookup: {
            from: "reserva",
            localField: "reserva_trilha.id_reserva",
            foreignField: "id_reserva",
            as: "reserva"
        }
    },
    { $unwind: "$reserva" },
    {
        $match: {
            "reserva.status_reserva": "Confirmado",
            "reserva.data": { $gte: new Date(new Date().setFullYear(new Date().getFullYear() - 2)) }
        }
    },
    {
        $group: {
            _id: "$id_trilha",
            nome: { $first: "$nome" },
            total_reservas: { $sum: 1 },
            total_guias: { $addToSet: "$guia.id_guia" }
        }
    },
    {
        $project: {
            nome: 1,
            media_reservas_por_guia: {
                $cond: {
                    if: { $size: "$total_guias" },
                    then: { $divide: ["$total_reservas", { $size: "$total_guias" }] },
                    else: 0
                }
            }
        }
    },
    { $sort: { media_reservas_por_guia: -1 } },
    { $limit: 5 }
]);




