# utils/dados.py

# Dicionário de docas com status simulados
DOCAS = {
    "A1": {"status": "Livre"},
    "A2": {"status": "Ocupada"},
    "A5": {"status": "Em preparação"},
    "A6": {"status": "Livre"},
}

# Dicionário de clientes com lista de docas associadas
CLIENTES = {
    "CL99578": {"docas": ["A5", "A6", "A1"]},
    "CL22103": {"docas": ["A2", "A1", "A5"]},
}

# Lista de agendamentos fictícios
AGENDAMENTOS = [
    {"cliente": "CL99578", "doca": "A5", "data": "22/05/2025", "hora": "14:00", "status": "Confirmado"},
    {"cliente": "CL99578", "doca": "A6", "data": "23/05/2025", "hora": "09:00", "status": "Em Processamento"},
    {"cliente": "CL22103", "doca": "A2", "data": "22/05/2025", "hora": "15:30", "status": "Pendente"},
    {"cliente": "CL22103", "doca": "A1", "data": "24/05/2025", "hora": "10:00", "status": "Cancelado"},
]

# Lista de operadores fictícios
OPERADORES = {
    "OP04758": {"nome": "Operador 1"},
}

# Lista de alertas fictícios
ALERTAS = [
    {"id": 1, "tipo": "falha", "doca": "A2", "mensagem": "Sensor Offline", "timestamp": "22/05/2025 13:55", "status": "Ativo"},
    {"id": 2, "tipo": "atraso", "doca": "A2", "mensagem": "Agendamento atrasado - Cliente CL22103", "timestamp": "22/05/2025 15:40", "status": "Ativo"},
]

# Lista de encomendas fictícias
ENCOMENDAS = [
    {
        "id": 1,
        "descricao": "Paletes de eletrônicos",
        "cliente": "CL99578",
        "agendamento_idx": None,  # None = não alocada
        "status": "Pendente",     # Pendente, Em Processamento, Processada, Cancelada
    },
    {
        "id": 2,
        "descricao": "Caixas de peças automotivas",
        "cliente": "CL22103",
        "agendamento_idx": None,
        "status": "Pendente",
    },
    {
        "id": 3,
        "descricao": "Bobinas de papel",
        "cliente": "CL99578",
        "agendamento_idx": None,  # None = não alocada
        "status": "Pendente",
    },
    {
        "id": 4,
        "descricao": "Equipamentos de informática",
        "cliente": "CL22103",
        "agendamento_idx": None,  # None = não alocada
        "status": "Pendente",
    },
    {
        "id": 5,
        "descricao": "Produtos químicos",
        "cliente": "CL22103",
        "agendamento_idx": None,
        "status": "Cancelada",
    },
]
