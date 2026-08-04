#!/usr/bin/env python3
import sys

from lcd1602_driver import CharLCD1602


class LCDDisplay:
    def __init__(self):
        self.disponivel = False
        self._lcd = None
        try:
            self._lcd = CharLCD1602()
            self.disponivel = bool(self._lcd.init_lcd(addr=None, bl=1))
        except Exception as exc:
            print(
                f"[LCD] Indisponível, usando modo console. Motivo: {exc}",
                file=sys.stderr,
            )

    def mostrar(self, linha1, linha2=""):
        linha1 = (linha1 or "")[:16]
        linha2 = (linha2 or "")[:16]
        if self.disponivel:
            try:
                self._lcd.clear()
                self._lcd.write(0, 0, linha1)
                if linha2:
                    self._lcd.write(0, 1, linha2)
                return
            except Exception as exc:
                print(
                    f"[LCD] Falha ao escrever, voltando ao modo console: {exc}",
                    file=sys.stderr,
                )
                self.disponivel = False
        print(f"[LCD] {linha1} | {linha2}")
