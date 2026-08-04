#!/usr/bin/env python3
"""
database.py — Persistência local (RF2) — Semana 2.

- data/alunos.json  : cadastro {"senha_4_digitos": "nome do aluno"}
- data/presencas.csv: histórico (nome, data, hora)
"""

import csv
import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ALUNOS_PATH = os.path.join(DATA_DIR, "alunos.json")
PRESENCAS_PATH = os.path.join(DATA_DIR, "presencas.csv")


def carregar_alunos():
    """Lê o cadastro. Retorna {} se o arquivo não existir (RNF4)."""
    if not os.path.exists(ALUNOS_PATH):
        return {}
    with open(ALUNOS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def validar_senha(senha):
    """Retorna o nome do aluno se a senha existir, ou None."""
    return carregar_alunos().get(senha)


def registrar_presenca(nome):
    """Grava uma linha de presença com data e hora atuais."""
    os.makedirs(DATA_DIR, exist_ok=True)
    novo_arquivo = not os.path.exists(PRESENCAS_PATH)
    with open(PRESENCAS_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if novo_arquivo:
            writer.writerow(["nome", "data", "hora"])
        agora = datetime.now()
        writer.writerow([
            nome,
            agora.strftime("%Y-%m-%d"),
            agora.strftime("%H:%M:%S"),
        ])


def ler_historico(limite=10):
    """Retorna as últimas `limite` presenças, mais recente primeiro."""
    if not os.path.exists(PRESENCAS_PATH):
        return []
    with open(PRESENCAS_PATH, "r", encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    return list(reversed(linhas))[:limite]
