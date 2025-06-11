import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="smiduser",
        password="smid",
        database="smid"
    )

def buscar_docas():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM docas")
    docas = cursor.fetchall()
    cursor.close()
    conn.close()
    return docas

def buscar_clientes():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE tipo='cliente'")
    clientes = cursor.fetchall()
    cursor.close()
    conn.close()
    return clientes

def buscar_alocacoes_docas():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT d.id as doca_id, d.nome as doca_nome, u.id as usuario_id, u.nome as usuario_nome
        FROM docas_usuarios du
        JOIN docas d ON du.doca_id = d.id
        JOIN usuarios u ON du.usuario_id = u.id
    """)
    alocacoes = cursor.fetchall()
    cursor.close()
    conn.close()
    return alocacoes

def alocar_doca_cliente(doca_id, usuario_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO docas_usuarios (doca_id, usuario_id) VALUES (%s, %s)",
        (doca_id, usuario_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

def desalocar_doca_cliente(doca_id, usuario_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM docas_usuarios WHERE doca_id=%s AND usuario_id=%s",
        (doca_id, usuario_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

def buscar_agendamentos_por_usuario(usuario_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT a.*, d.nome as doca_nome FROM agendamentos a JOIN docas d ON a.doca_id = d.id WHERE a.usuario_id = %s",
        (usuario_id,)
    )
    ags = cursor.fetchall()
    cursor.close()
    conn.close()
    return ags

def criar_agendamento(usuario_id, doca_id, data, hora):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO agendamentos (usuario_id, doca_id, data, hora, status) VALUES (%s, %s, %s, %s, 'Pendente')",
        (usuario_id, doca_id, data, hora)
    )
    conn.commit()
    cursor.close()
    conn.close()

def buscar_agendamentos():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.*, d.nome as doca_nome, u.nome as usuario_nome
        FROM agendamentos a
        JOIN docas d ON a.doca_id = d.id
        JOIN usuarios u ON a.usuario_id = u.id
        ORDER BY a.data DESC, a.hora DESC
    """)
    ags = cursor.fetchall()
    cursor.close()
    conn.close()
    return ags

def atualizar_agendamento_status(agendamento_id, novo_status, confirmado_em=None, finalizado_em=None):
    conn = get_connection()
    cursor = conn.cursor()
    if confirmado_em:
        cursor.execute(
            "UPDATE agendamentos SET status=%s, confirmado_em=%s WHERE id=%s",
            (novo_status, confirmado_em, agendamento_id)
        )
    elif finalizado_em:
        cursor.execute(
            "UPDATE agendamentos SET status=%s, finalizado_em=%s WHERE id=%s",
            (novo_status, finalizado_em, agendamento_id)
        )
    else:
        cursor.execute(
            "UPDATE agendamentos SET status=%s WHERE id=%s",
            (novo_status, agendamento_id)
        )
    conn.commit()
    cursor.close()
    conn.close()

def atualizar_agendamento_doca_data_hora(agendamento_id, nova_doca_id, nova_data, nova_hora):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE agendamentos SET doca_id=%s, data=%s, hora=%s, status='Pendente' WHERE id=%s",
        (nova_doca_id, nova_data, nova_hora, agendamento_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

def buscar_alertas():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.*, d.nome as doca_nome
        FROM alertas a
        LEFT JOIN docas d ON a.doca_id = d.id
        ORDER BY a.timestamp DESC
    """)
    alertas = cursor.fetchall()
    cursor.close()
    conn.close()
    return alertas

def criar_alerta(mensagem, doca_id, tipo, agendamento_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO alertas (mensagem, doca_id, timestamp, status, tipo, agendamento_id) VALUES (%s, %s, NOW(), 'Ativo', %s, %s)",
        (mensagem, doca_id, tipo, agendamento_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

def resolver_alerta(alerta_id, usuario):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE alertas SET status='Resolvido', resolvido_por=%s, resolvido_em=NOW() WHERE id=%s",
        (usuario, alerta_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

def buscar_encomendas():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM encomendas ORDER BY id DESC")
    encomendas = cursor.fetchall()
    cursor.close()
    conn.close()
    return encomendas

def cancelar_encomenda(encomenda_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE encomendas SET status='Cancelada' WHERE id=%s",
        (encomenda_id,)
    )
    conn.commit()
    cursor.close()
    conn.close()

def alocar_encomenda_agendamento(encomenda_id, agendamento_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE encomendas SET agendamento_id=%s, status='Em Processamento' WHERE id=%s",
        (agendamento_id, encomenda_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

def atualizar_encomenda_status(encomenda_id, novo_status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE encomendas SET status=%s WHERE id=%s",
        (novo_status, encomenda_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

def atualizar_status_doca(doca_id, novo_status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE docas SET status=%s WHERE id=%s",
        (novo_status, doca_id)
    )
    conn.commit()
    cursor.close()
    conn.close()