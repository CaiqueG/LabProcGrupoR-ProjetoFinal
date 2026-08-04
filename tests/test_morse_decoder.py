#!/usr/bin/env python3
"""
tests/test_morse_decoder.py — Testes unitários do decodificador Morse.

Não depende de GPIO, LCD ou Raspberry Pi.

Executar:  python3 -m unittest tests/test_morse_decoder.py -v
"""

import os
import sys
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from morse_decoder import ERRO, DOT_MAX_DURATION, DIGIT_GAP_TIMEOUT, MorseDecoder


def digitar(decoder, simbolos):
    """Simula toques a partir de uma string de '.'/'-'."""
    for s in simbolos:
        duracao = (DOT_MAX_DURATION / 2) if s == "." else (DOT_MAX_DURATION * 2)
        decoder.registrar_toque(duracao)


class TestMorseDecoder(unittest.TestCase):
    def test_todos_os_digitos_0_a_9(self):
        tabela = {
            "-----": "0", ".----": "1", "..---": "2", "...--": "3", "....-": "4",
            ".....": "5", "-....": "6", "--...": "7", "---..": "8", "----.": "9",
        }
        for codigo, esperado in tabela.items():
            decoder = MorseDecoder()
            digitar(decoder, codigo)
            resultado = decoder.fechar_digito_se_completo()
            self.assertEqual(resultado, esperado)
            self.assertEqual(decoder.senha, esperado)

    def test_senha_completa_com_4_digitos(self):
        decoder = MorseDecoder()
        for codigo in ["-----", ".----", "..---", "...--"]:  # 0123
            digitar(decoder, codigo)
            decoder.fechar_digito_se_completo()
        self.assertTrue(decoder.senha_completa())
        self.assertEqual(decoder.senha, "0123")

    def test_fechar_incompleto_preserva_buffer(self):
        """Lição S1: fechar prematuro NÃO apaga símbolos (< 5)."""
        decoder = MorseDecoder()
        digitar(decoder, "..-")  # 3 símbolos
        resultado = decoder.fechar_digito_se_completo()
        self.assertIsNone(resultado)
        self.assertEqual(decoder.senha, "")
        self.assertEqual(decoder.buffer_simbolos, "..-")  # preservado

    def test_sequencia_de_5_simbolos_sem_mapeamento_retorna_erro(self):
        decoder = MorseDecoder()
        digitar(decoder, ".-.-.")  # 5 símbolos sem mapeamento
        resultado = decoder.fechar_digito_se_completo()
        self.assertEqual(resultado, ERRO)

    def test_cancelar_limpa_buffer_e_senha(self):
        decoder = MorseDecoder()
        digitar(decoder, "-----")
        decoder.fechar_digito_se_completo()
        digitar(decoder, "..")
        decoder.limpar()
        self.assertEqual(decoder.senha, "")
        self.assertEqual(decoder.buffer_simbolos, "")

    def test_toques_extras_apos_senha_completa_sao_ignorados(self):
        decoder = MorseDecoder()
        for codigo in ["-----", "-----", "-----", "-----"]:  # 0000
            digitar(decoder, codigo)
            decoder.fechar_digito_se_completo()
        self.assertTrue(decoder.senha_completa())
        resultado = decoder.registrar_toque(DOT_MAX_DURATION / 2)
        self.assertIsNone(resultado)
        self.assertEqual(decoder.senha, "0000")

    def test_verificar_timeout_nao_fecha_antes_do_prazo(self):
        decoder = MorseDecoder()
        digitar(decoder, "-----")
        self.assertIsNone(decoder.verificar_timeout())

    def test_timeout_nao_descarta_digito_incompleto(self):
        """Semana 2: pausa intra-dígito preserva símbolos (< 5)."""
        decoder = MorseDecoder()
        digitar(decoder, "..-")  # 3 símbolos
        # Simula ocioso > DIGIT_GAP_TIMEOUT sem fechar
        decoder.ultimo_evento = time.monotonic() - (DIGIT_GAP_TIMEOUT + 0.5)
        self.assertIsNone(decoder.verificar_timeout())
        self.assertEqual(decoder.buffer_simbolos, "..-")

    def test_timeout_fecha_apenas_digito_completo(self):
        """Semana 2: após 5 símbolos + pausa, fecha o dígito."""
        decoder = MorseDecoder()
        digitar(decoder, ".----")  # dígito 1
        decoder.ultimo_evento = time.monotonic() - (DIGIT_GAP_TIMEOUT + 0.5)
        self.assertEqual(decoder.verificar_timeout(), "1")
        self.assertEqual(decoder.senha, "1")
        self.assertEqual(decoder.buffer_simbolos, "")


class TestDatabase(unittest.TestCase):
    """Testes de validação / CSV sem hardware."""

    def setUp(self):
        import database
        self.db = database
        self._alunos_orig = self.db.ALUNOS_PATH
        self._presencas_orig = self.db.PRESENCAS_PATH

    def tearDown(self):
        self.db.ALUNOS_PATH = self._alunos_orig
        self.db.PRESENCAS_PATH = self._presencas_orig

    def test_validar_senha_conhecida(self):
        nome = self.db.validar_senha("1234")
        self.assertEqual(nome, "Caique Granja Maia")

    def test_validar_senha_desconhecida(self):
        self.assertIsNone(self.db.validar_senha("9999"))

    def test_registrar_e_ler_historico(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            self.db.PRESENCAS_PATH = os.path.join(tmp, "presencas.csv")
            self.db.DATA_DIR = tmp
            self.db.registrar_presenca("Aluno Teste")
            hist = self.db.ler_historico(limite=5)
            self.assertEqual(len(hist), 1)
            self.assertEqual(hist[0]["nome"], "Aluno Teste")
            self.assertIn("data", hist[0])
            self.assertIn("hora", hist[0])


if __name__ == "__main__":
    unittest.main()
