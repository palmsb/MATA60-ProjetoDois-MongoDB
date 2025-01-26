-- Visitantes
SELECT 
    id_visitante AS _id, 
    nome, 
    idade, 
    contato 
FROM visitante;


-- Trilhas
SELECT 
    id_trilha AS _id, 
    nome, 
    localizacao, 
    capacidade_max, 
    duracao, 
    nivel_dificuldade 
FROM trilha;


-- Guias
SELECT 
    id_guia AS _id, 
    nome, 
    experiencia, 
    contato 
FROM guia;

-- Guias-Trilhas
SELECT 
    id_guia, 
    id_trilha 
FROM guia_trilha;


-- Reservas
SELECT 
    r.id_reserva AS _id,
    r.data,
    r.turno,
    r.status_reserva,
    r.id_visitante,
    v.nome AS visitante_nome,
    v.idade AS visitante_idade,
    v.contato AS visitante_contato
FROM reserva r
JOIN visitante v ON r.id_visitante = v.id_visitante;

-- Reservas-Trilhas
SELECT 
    rt.id_reserva, 
    rt.id_trilha 
FROM reserva_trilha rt;
