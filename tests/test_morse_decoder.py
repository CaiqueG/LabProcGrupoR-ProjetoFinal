#!/usr/bin/env python3
"""
tests/test_morse_decoder.py — Testes unitários do decodificador Morse.

Não depende de GPIO, LCD ou Raspberry Pi: pode (e deve) ser rodado em
qualquer máquina antes de integrar com o hardware físico, seguindo a
"Regra de Ouro" da Aula 10 (nunca integrar um componente sem teste
unitário aprovado).

Executar:  python3 -m unittest tests/test_morse_decoder.py -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from morse_decoder import ERRO, DOT_MAX_DURATION, DIGIT_GAP_TIMEOUT, MorseDecoder


def digitar(decoder, simbolos):
    """Simula toques a partir de uma string de '.'/'-' (útil nos testes)."""
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

    def test_sequencia_incompleta_retorna_erro_e_nao_trava(self):
        decoder = MorseDecoder()
        digitar(decoder, "..-")  # apenas 3 símbolos, incompleto
        resultado = decoder.fechar_digito_se_completo()
        self.assertEqual(resultado, ERRO)
        self.assertEqual(decoder.senha, "")  # nada foi adicionado
        self.assertEqual(decoder.buffer_simbolos, "")  # buffer foi limpo, sistema não trava

    def test_sequencia_de_5_simbolos_sem_mapeamento_retorna_erro(self):
        decoder = MorseDecoder()
        digitar(decoder, ".-.-.")  # 5 símbolos, mas não corresponde a nenhum dígito
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
        # ultimo_evento acabou de ser atualizado por registrar_toque -> ainda não passou o timeout
        self.assertIsNone(decoder.verificar_timeout())


if __name__ == "__main__":
    unittest.main()
