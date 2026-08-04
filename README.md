# Sistema de Presença por Código Morse — Raspberry Pi 3

**Grupo R** — Laboratório de Processadores — Escola Politécnica da USP

| Integrante | NUSP |
|---|---|
| Caique Granja Maia | 12555572 |
| João Ricardo Rodrigues Ribeiro | 14582802 |
| Stephanie Pedrazza Grunwald | 11233522 |

Sistema embarcado para controle de presença em sala de aula: cada aluno digita uma senha numérica de 4 dígitos em **código Morse** usando um botão físico. O sistema decodifica, valida contra uma base local, registra a presença com data/hora, sinaliza por LEDs/buzzer/LCD e exibe o resultado em uma interface web acessível pela rede local.

---

## Hardware necessário (Freenove FNK0054)

Pinagem BCM conforme a documentação Freenove ([Buttons & LEDs](https://docs.freenove.com/projects/fnk0054/en/latest/fnk0054/codes/c%26py/3_Buttons_%26_LEDs.html), [RGB LED](https://docs.freenove.com/projects/fnk0054/en/latest/fnk0054/codes/c%26py/5_RGB_LED.html)):

| Componente | Pino BCM | Observação |
|---|---|---|
| Botão Morse | GPIO 26 | Botão **S4** da placa Freenove |
| Botão Confirmar | GPIO 16 | Botão externo na protoboard |
| Botão Limpa | GPIO 20 | Apaga só o **último dígito** da senha |
| Botão Cancelar | GPIO 21 | Zera senha + buffer por completo |
| RGB LED Red | GPIO 5 | LED RGB da placa (`active_high=False`) |
| RGB LED Green | GPIO 6 | LED RGB da placa |
| RGB LED Blue | GPIO 13 | LED RGB da placa |
| Buzzer passivo | GPIO 12 | Conector Buzzer da placa Freenove |
| Display LCD 1602 (I2C) | SDA=GPIO 2, SCL=GPIO 3 | Conector I2C da placa Freenove |

> **Uma única biblioteca GPIO:** apenas `gpiozero` (+ `lgpio`). Não misturar com `RPi.GPIO` (conflito de driver na Aula 10). LCD usa `smbus2` (I2C), sem GPIO digital.

> LCD e buzzer são opcionais: se não estiverem conectados, o sistema continua funcionando. O LCD cai em modo console e o buzzer é ignorado com aviso no log.

---

## Instalação

```bash
# No Raspberry Pi OS
sudo apt-get update
sudo apt-get install -y python3-pip i2c-tools

# Habilitar barramento I2C (se ainda não estiver ativo)
sudo raspi-config nonint do_i2c 0

# Clonar o repositório e instalar dependências
git clone https://github.com/CaiqueG/LabProcGrupoR-ProjetoFinal.git
cd LabProcGrupoR-ProjetoFinal
pip3 install -r requirements.txt --break-system-packages
```

Verifique se o LCD está visível no barramento (opcional):

```bash
i2cdetect -y 1
```

---

## Como rodar

### Semana 1 — só Morse + RGB

```bash
python3 src/demo_morse.py
```

### Semana 2 — Morse + LCD + validação + buzzer

```bash
python3 src/demo_validacao.py
```

(Interface web Flask — Semana 4.)

Para encerrar: `Ctrl+C` — o programa libera os pinos GPIO antes de sair.

---

## Como usar (Semana 2)

1. **Digitar a senha**: toque **curto** (< 0,3s) = `.`, **longo** (≥ 0,3s) = `-`. Exatamente 5 símbolos por dígito. Pausa no meio do dígito **preserva** o buffer; só após 5 símbolos + pausa ≥ 1s o dígito fecha (lição Semana 1).
2. **Limpa** (GPIO 20): apaga só o **último dígito** já guardado (ex.: `55__` → `5___`).
3. **Cancelar** (GPIO 21): zera senha e buffer por completo.
4. **Confirmar** (GPIO 16): com 4 dígitos, valida e registra; com buffer incompleto, **não apaga** — só avisa.

### Tabela Morse numérica (ITU-R M.1677)

| Dígito | Código | Dígito | Código |
|---|---|---|---|
| 0 | `-----` | 5 | `.....` |
| 1 | `.----` | 6 | `-....` |
| 2 | `..---` | 7 | `--...` |
| 3 | `...--` | 8 | `---..` |
| 4 | `....-` | 9 | `----.` |

### Senhas de teste (`src/data/alunos.json`)

| Senha | Aluno |
|---|---|
| 1234 | Caique Granja Maia |
| 5678 | Joao Ricardo Rodrigues Ribeiro |
| 0192 | Stephanie Pedrazza Grunwald |
| 5555 | Aluno Teste Pontos (`.....` × 4 — só pontos) |

---

## Rodando os testes (sem hardware)

```bash
python3 -m unittest tests/test_morse_decoder.py -v
```

---

## Documentação

O relatório completo do projeto está em [`docs/relatorio.md`](docs/relatorio.md).
