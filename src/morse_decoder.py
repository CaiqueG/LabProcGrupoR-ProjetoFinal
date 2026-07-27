#!/usr/bin/env python3
"""
morse_decoder.py — Decodificação de código Morse numérico (0–9).

Responsável apenas pela LÓGICA de tradução: recebe durações de toque
(em segundos) e devolve dígitos. Não conhece GPIO, LCD, Flask ou banco
de dados — isso é o que permite testá-lo isoladamente (tests/test_morse_decoder.py),
seguindo a "Regra de Ouro" registrada na Aula 10: nunca integrar um componente
que não passou no seu próprio teste unitário.

Tabela Morse numérica (padrão internacional ITU-R M.1677 — 5 símbolos/dígito):
    0 -----   5 .....
    1 .----   6 -....
    2 ..---   7 --...
    3 ...--   8 ---..
    4 ....-   9 ----.
"""

import time

# ── Parâmetros de tempo (RF1 / RNF2) ────────────────────────────────
DOT_MAX_DURATION = 0.3      # toque < 0.3s  -> ponto (.)
DIGIT_GAP_TIMEOUT = 1.0     # pausa >= 1.0s -> fecha o dígito atual
SYMBOLS_PER_DIGIT = 5
MAX_DIGITS = 4

MORSE_TO_DIGIT = {
    "-----": "0",
    ".----": "1",
    "..---": "2",
    "...--": "3",
    "....-": "4",
    ".....": "5",
    "-....": "6",
    "--...": "7",
    "---..": "8",
    "----.": "9",
}

ERRO = "ERRO"  # sinalizador de sequência inválida/incompleta descartada


class MorseDecoder:
    def __init__(self):
        self.reset()

    def reset(self):
        self.buffer_simbolos = ""   # símbolos (.  / -) do dígito em digitação
        self.senha = ""              # dígitos já fechados e validados
        self.ultimo_evento = time.monotonic()

    # Alias mais descritivo para uso externo (RF3 — Cancelamento)
    def limpar(self):
        self.reset()

    def senha_completa(self):
        return len(self.senha) >= MAX_DIGITS

    def registrar_toque(self, duracao_s):
        """Chamado quando o botão Morse é SOLTO, com a duração da pressão.
        Retorna o símbolo adicionado ('.' ou '-'), ou None se ignorado
        (buffer cheio ou senha já completa)."""
        self.ultimo_evento = time.monotonic()
        if self.senha_completa():
            return None
        if len(self.buffer_simbolos) >= SYMBOLS_PER_DIGIT:
            return None
        simbolo = "." if duracao_s < DOT_MAX_DURATION else "-"
        self.buffer_simbolos += simbolo
        return simbolo

    def verificar_timeout(self):
        """Deve ser chamado periodicamente (ex.: a cada 100ms) pela FSM.
        Fecha automaticamente o dígito atual quando o usuário faz uma
        pausa >= DIGIT_GAP_TIMEOUT depois do último toque.
        Retorna: dígito fechado ('0'..'9'), ERRO (sequência inválida
        descartada) ou None (nada aconteceu)."""
        if not self.buffer_simbolos:
            return None
        ocioso = time.monotonic() - self.ultimo_evento
        if ocioso < DIGIT_GAP_TIMEOUT:
            return None
        return self._fechar_buffer()

    def fechar_digito_se_completo(self):
        """Chamado pelo botão Confirmar: fecha imediatamente o buffer
        atual, sem esperar o timeout, desde que ele já tenha os 5
        símbolos. Se o buffer estiver incompleto (mas não vazio), é
        descartado como sequência inválida (RNF2 — não trava o sistema)."""
        if not self.buffer_simbolos:
            return None
        return self._fechar_buffer()

    def _fechar_buffer(self):
        completo = len(self.buffer_simbolos) == SYMBOLS_PER_DIGIT
        digito = MORSE_TO_DIGIT.get(self.buffer_simbolos) if completo else None
        self.buffer_simbolos = ""
        self.ultimo_evento = time.monotonic()
        if digito is None:
            return ERRO
        if not self.senha_completa():
            self.senha += digito
        return digito
