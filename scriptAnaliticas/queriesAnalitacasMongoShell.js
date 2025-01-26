
// Simples
// 1)Qual trilha tem maior número de reservas? 
db.trilha.aggregate([
    { $lookup: { from: "reserva_trilha", localField: "_id", foreignField: "id_trilha", as: "reservas" } },
    { $unwind: "$reservas" },
    { $group: { _id: "$_id", nome: { $first: "$nome" }, total_reservas: { $sum: 1 } } },
    { $sort: { total_reservas: -1 } },
    { $limit: 1 }
]);


// 2)Quantos visitantes únicos já fizeram reservas?
db.reserva.distinct("id_visitante");


// 3)Quais trilhas têm capacidade máxima maior que 20?
db.trilha.find(
    { capacidade_max: { $gt: 20 } },
    { _id: 0, nome: 1, capacidade_max: 1 }
);


//4)Qual o número total de reservas ativas no momento?
db.reserva.countDocuments({ status_reserva: "Confirmado" });


// Intermediárias:

// 5) Qual trilha conduzida por mais de 2 guias tem o maior número de reservas?
db.trilha.aggregate([
    {
        $lookup: {
            from: "guia_trilha",
            localField: "_id",
            foreignField: "id_trilha",
            as: "guias"
        }
    },
    {
        $lookup: {
            from: "reserva_trilha",
            localField: "_id",
            foreignField: "id_trilha",
            as: "reservas"
        }
    },
    { $match: { $expr: { $gt: [ { $size: "$guias" }, 2 ] } } },
    {
        $project: {
            trilha_nome: "$nome",
            total_reservas: { $size: "$reservas" }
        }
    },
    { $sort: { total_reservas: -1 } },
    { $limit: 1 }
]);



// 6)Quantos visitantes reservaram trilhas de nível avançado?
db.trilha.aggregate([
    {
        $lookup: {
            from: "reserva_trilha",
            localField: "_id",
            foreignField: "id_trilha",
            as: "reservas"
        }
    },
    { $match: { nivel_dificuldade: "Avançado" } },
    {
        $group: {
            _id: null,
            total_visitantes: { $addToSet: "$reservas.id_visitante" }
        }
    },
    {
        $project: {
            total_visitantes: { $size: "$total_visitantes" }
        }
    }
]);


// 7)Quais os 5 guias mais ativos?
db.guia.aggregate([
    {
        $lookup: {
            from: "guia_trilha",
            localField: "_id",
            foreignField: "id_guia",
            as: "trilhas"
        }
    },
    { $unwind: "$trilhas" },
    {
        $lookup: {
            from: "reserva_trilha",
            localField: "trilhas.id_trilha",
            foreignField: "id_trilha",
            as: "reservas"
        }
    },
    { $unwind: "$reservas" },
    {
        $group: {
            _id: "$_id",
            nome: { $first: "$nome" },
            total_reservas: { $sum: 1 }
        }
    },
    { $sort: { total_reservas: -1 } },
    { $limit: 5 }
]);


// Avançadas:

// 8)Qual guia conduziu o maior número de visitantes únicos?
db.guia.aggregate([
    {
        $lookup: {
            from: "guia_trilha",
            localField: "_id",
            foreignField: "id_guia",
            as: "trilhas"
        }
    },
    { $unwind: "$trilhas" },
    {
        $lookup: {
            from: "reserva_trilha",
            localField: "trilhas.id_trilha",
            foreignField: "id_trilha",
            as: "reservas"
        }
    },
    { $unwind: "$reservas" },
    {
        $lookup: {
            from: "reserva",
            localField: "reservas.id_reserva",
            foreignField: "_id",
            as: "detalhes_reservas"
        }
    },
    { $unwind: "$detalhes_reservas" },
    {
        $group: {
            _id: "$_id",
            nome: { $first: "$nome" },
            visitantes_unicos: { $addToSet: "$detalhes_reservas.id_visitante" }
        }
    },
    {
        $project: {
            nome: 1,
            total_visitantes: { $size: "$visitantes_unicos" }
        }
    },
    { $sort: { total_visitantes: -1 } },
    { $limit: 1 }
]);
