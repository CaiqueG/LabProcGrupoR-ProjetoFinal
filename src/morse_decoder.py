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

Semana 2 — timeout revisado:
    A pausa intra-dígito NÃO descarta símbolos incompletos (< 5).
    O timeout de DIGIT_GAP_TIMEOUT só fecha o dígito após exatamente
    5 símbolos (intervalo entre dígitos completos).
"""

import time

# ── Parâmetros de tempo (RF1 / RNF2) ────────────────────────────────
DOT_MAX_DURATION = 0.3      # toque < 0.3s  -> ponto (.)
DIGIT_GAP_TIMEOUT = 1.0     # pausa >= 1.0s -> fecha dígito completo
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

    # Alias — limpa tudo (após validação / reset completo)
    def limpar(self):
        self.reset()

    def apagar_ultimo_digito(self):
        """Botão Limpa: remove só o dígito mais recente já guardado na senha.

        Também zera o buffer de símbolos em digitação (se houver), para não
        misturar toques parciais com o dígito que acabou de ser apagado.
        Retorna o dígito removido, ou None se a senha estava vazia.
        """
        self.buffer_simbolos = ""
        self.ultimo_evento = time.monotonic()
        if not self.senha:
            return None
        removido = self.senha[-1]
        self.senha = self.senha[:-1]
        return removido

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

        Semana 2: pausa com buffer incompleto (< 5 símbolos) NÃO fecha
        nem descarta — o usuário pode demorar entre toques do mesmo dígito.
        O timeout só fecha quando já há exatamente 5 símbolos (dígito
        completo aguardando o intervalo entre dígitos).

        Retorna: dígito ('0'..'9'), ERRO (5 símbolos sem mapeamento) ou None.
        """
        if len(self.buffer_simbolos) < SYMBOLS_PER_DIGIT:
            return None
        ocioso = time.monotonic() - self.ultimo_evento
        if ocioso < DIGIT_GAP_TIMEOUT:
            return None
        return self._fechar_buffer()

    def fechar_digito_se_completo(self):
        """Fecha o dígito imediatamente se já houver exatamente 5 símbolos.

        Usado pelo botão Confirmar para não esperar o timeout entre dígitos.
        Se o buffer estiver incompleto (< 5), NÃO descarta — preserva os
        símbolos. Para apagar, use o botão Limpa (apagar_ultimo_digito).
        Retorna None se incompleto.
        """
        if len(self.buffer_simbolos) < SYMBOLS_PER_DIGIT:
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
