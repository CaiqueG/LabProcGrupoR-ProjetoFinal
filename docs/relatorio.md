# Relatório — Sistema de Presença por Código Morse com Raspberry Pi 3

**Grupo R** — Laboratório de Processadores — Escola Politécnica da USP


| Integrante                     | NUSP     |
| ------------------------------ | -------- |
| Caique Granja Maia             | 12555572 |
| João Ricardo Rodrigues Ribeiro | 14582802 |
| Stephanie Pedrazza Grunwald    | 11233522 |


**Repositório:** [https://github.com/CaiqueG/LabProcGrupoR-ProjetoFinal](https://github.com/CaiqueG/LabProcGrupoR-ProjetoFinal)

---

## 1. Motivação e Justificativa

O controle de presença manual em sala de aula é um processo lento, sujeito a erros humanos e suscetível a fraudes (um aluno assinando por outro, por exemplo). Soluções digitais existentes geralmente dependem de conectividade à internet ou de hardware proprietário (leitores de crachá, biometria), o que aumenta o custo e a complexidade de implantação.

Este projeto propõe uma alternativa de baixo custo, autônoma e educativa: um sistema embarcado no **Raspberry Pi 3** que realiza o controle de presença por meio de **código Morse numérico**. Cada aluno possui uma senha de 4 dígitos que é inserida pressionando um único botão físico, combinando toques curtos (pontos) e longos (traços).

Além do aspecto prático, o projeto consolida diretamente os conceitos trabalhados ao longo do laboratório:

- **Decodificação por temporização** (Aula 2 e Aula 9): o sistema distingue ponto de traço pela duração do toque.
- **Especificação formal de requisitos** (Aulas anteriores): projeto orientado a RF e RNF desde o início.
- **PWM e temporização não-bloqueante** (Aula 9): arquitetura orientada a eventos, sem busy-waiting.
- **Integração de periféricos via GPIO e I2C** (Aula 10): LCD, botões, LEDs, buzzer e máquina de estados integrados.

Projetos similares de controle de acesso embarcado em Raspberry Pi podem ser encontrados em:

- Raspberry Pi Foundation — *Physical computing with Python*. Disponível em: [https://projects.raspberrypi.org/en/projects/physical-computing](https://projects.raspberrypi.org/en/projects/physical-computing)
- Freenove — *Freenove Ultimate Starter Kit for Raspberry Pi*. Disponível em: [https://docs.freenove.com](https://docs.freenove.com)

---



## 2. Objetivos



### 2.1 Objetivo Geral

Desenvolver um sistema embarcado de controle de presença em sala de aula, executado no Raspberry Pi 3, que permita a identificação de alunos por meio de senha numérica inserida em código Morse, com registro local e interface web de monitoramento.

### 2.2 Objetivos Específicos

1. Implementar um decodificador de código Morse numérico (dígitos 0–9, padrão ITU-R M.1677) capaz de distinguir pontos e traços pela duração do toque em um botão físico.
2. Integrar uma base de dados local (arquivo JSON) para validação de senhas e um histórico de presenças (arquivo CSV) com registro de data e hora.
3. Fornecer feedback multimodal ao usuário: LED verde/vermelho, bipe no buzzer e mensagem no display LCD 1602 via I2C.
4. Desenvolver uma interface web (Flask) acessível pela rede local, atualizada em tempo real, exibindo o estado do sistema e o histórico de presenças.
5. Garantir uma arquitetura não-bloqueante, baseada em eventos (callbacks de GPIO), para que a leitura de botões e o servidor web operem simultaneamente sem interferência.

---



## 3. Requisitos Funcionais

**RF1** — O sistema deve decodificar dígitos em código Morse numérico (0–9), distinguindo pontos e traços pela duração do toque e utilizando o padrão ITU-R M.1677.  
*Critério:* a sequência correspondente a um dígito válido é decodificada corretamente e exibida ao usuário.

**RF1b** — O sistema deve considerar um dígito concluído apenas quando houver cinco símbolos válidos digitados, preservando o buffer caso a sequência ainda esteja incompleta.  
*Critério:* pausas durante a digitação de um dígito incompleto não descartam os símbolos já inseridos.

**RF2** — O sistema deve validar uma senha composta por quatro dígitos contra o cadastro local e, quando válida, registrar a presença do aluno.  
*Critério:* senhas cadastradas são reconhecidas e registradas corretamente.

**RF2b** — O sistema deve informar quando uma senha digitada for inválida e retornar ao estado inicial de espera.  
*Critério:* senhas não cadastradas não geram registro de presença.

**RF3** — O sistema deve permitir que o usuário cancele a digitação da senha, limpando o buffer de entrada.  
*Critério:* após o cancelamento, o sistema retorna ao estado inicial aguardando uma nova senha.

**RF4** — O sistema deve fornecer feedback ao usuário durante a interação por meio do display LCD, LEDs e buzzer.  
*Critério:* os dispositivos de saída refletem o estado atual do sistema e o resultado da validação da senha.

**RF5** — O sistema deve disponibilizar uma interface web que exiba o estado atual do sistema e o histórico das últimas presenças registradas.  
*Critério:* a interface apresenta corretamente as informações de estado e histórico armazenadas pelo sistema.

---



## 4. Requisitos Não Funcionais

**RNF1** — Tempo de resposta da interface web inferior a 1 segundo. *Critério:* latência do endpoint `/status` < 1s (medido com DevTools).

**RNF2** — Debounce de ~50ms; sequências inválidas descartadas sem travar o sistema. *Critério:* toques rápidos não geram múltiplos eventos; sistema retorna ao estado de espera após sequência inválida.

**RNF3** — Arquitetura orientada a eventos (sem busy-waiting): botões via callbacks, Flask em thread separada, buzzer em thread própria. *Critério:* digitar a senha e acessar a interface web simultaneamente não causa travamento.

**RNF4** — Resiliência: ausência de LCD ou buzzer não impede o funcionamento. *Critério:* sem LCD, mensagens aparecem no console; sem buzzer, sistema continua sem erro fatal.


---



## 5. Arquitetura da Solução



### 5.1 Arquitetura Física

O sistema é executado inteiramente no **Raspberry Pi 3 Model B** (SoC Broadcom BCM2837, ARM Cortex-A53 quad-core 1,2 GHz, 1 GB RAM, Raspberry Pi OS). Os periféricos são conectados diretamente aos pinos GPIO:


| Componente       | Interface     | Pino BCM        | Função                                      |
| ---------------- | ------------- | --------------- | ------------------------------------------- |
| Botão Morse      | GPIO digital  | 26              | Botão S4 da placa Freenove (doc Ch. 3)      |
| Botão Confirmar  | GPIO digital  | 16              | Botão externo na protoboard                 |
| Botão Limpa      | GPIO digital  | 20              | Apaga só o último dígito da senha           |
| Botão Cancelar   | GPIO digital  | 21              | Zera senha + buffer                         |
| RGB LED R/G/B    | GPIO digital  | 5 / 6 / 13      | LED RGB Freenove (`active_high=False`, Ch. 5) |
| Buzzer passivo   | GPIO digital  | 12              | Conector Buzzer da placa Freenove           |
| Display LCD 1602 | I2C (SDA/SCL) | GPIO 2 / GPIO 3 | Conector I2C da placa Freenove              |


> **Nota sobre GPIO:** a decisão de usar `gpiozero` como biblioteca padrão em todos os módulos foi tomada a partir do conflito de drivers relatado na Aula 10, onde o uso simultâneo de `RPi.GPIO` e outra biblioteca causava falha na inicialização dos pinos.



### 5.2 Arquitetura de Software

O sistema é composto por seis módulos Python com responsabilidades bem definidas:


| Módulo             | Responsabilidade                                                                |
| ------------------ | ------------------------------------------------------------------------------- |
| `app.py`           | Inicializa a FSM em thread separada e serve a interface web via Flask           |
| `fsm.py`           | Máquina de estados não-bloqueante: gerencia entrada Morse, timeouts e validação |
| `morse_decoder.py` | Lógica pura de decodificação: recebe durações de toque e retorna dígitos        |
| `hardware.py`      | Abstração dos periféricos GPIO (botões via callbacks, LEDs, buzzer)             |
| `database.py`      | Leitura do cadastro JSON e gravação do histórico CSV                            |
| `lcd_driver.py`    | Wrapper do LCD com fallback para console se I2C não estiver disponível          |


**Fluxo de estados da FSM:**

![Diagrama FSM](diagramas/fsm.png)


> O botão **Cancelar** retorna a FSM a IDLE a partir de qualquer estado (transição omitida do diagrama para legibilidade).

**Mecanismo de concorrência:**

- **Thread da FSM** (`loop_temporizador`): verifica timeouts a cada 100ms usando `threading.Thread`.
- **Thread do Flask**: serve as requisições HTTP de forma independente da FSM.
- **Thread do buzzer**: toca o bipe sem bloquear a leitura dos botões.
- `threading.Lock`: protege o estado compartilhado (`status`) acessado pelas três threads.



### 5.3 Interface Web

A interface web (Semana 4) será servida pelo Flask na porta 5000 com polling a cada 1 segundo no endpoint `/status`, retornando estado do sistema e histórico de presenças em JSON.

---



## 6. Ferramentas Utilizadas

| Categoria | Ferramenta / Componente | Uso |
| --------- | ----------------------- | --- |
| Hardware  | Raspberry Pi 3 Model B (ARM Cortex-A53, 1,2 GHz) | Plataforma de execução |
| Hardware  | LCD 1602 + módulo I2C PCF8574 | Display de feedback |
| Hardware  | Botões push-button, LEDs, buzzer passivo | Entrada e feedback físico |
| Software  | Python 3.11+ | Linguagem principal |
| Software  | Flask 3.x | Servidor web e API REST |
| Software  | gpiozero 2.x + lgpio | Abstração GPIO |
| Software  | smbus2 | Comunicação I2C com LCD |
| Dev       | Git / GitHub + unittest | Versionamento e testes unitários |


---



## 7. Metodologia de Desenvolvimento

O projeto seguiu a mesma metodologia incremental adotada nas aulas práticas anteriores (Aulas 8, 9 e 10):

1. **Especificação de requisitos**: levantamento de RF e RNF antes da implementação, com casos de teste associados a cada requisito.
2. **Desenvolvimento modular**: cada componente (`morse_decoder`, `hardware`, `database`, `lcd_driver`) foi implementado e testado isoladamente antes da integração.
3. **Regra de ouro (Aula 10)**: nenhum componente foi integrado sem ter passado em seu próprio teste unitário ou teste isolado de hardware.
4. **Integração incremental**: módulos foram integrados um a um na FSM, verificando a ausência de conflitos de GPIO (lição aprendida na Aula 10 com o conflito `RPi.GPIO` × `gpiozero`).
5. **Controle de versão**: commits incrementais no GitHub para rastreabilidade da evolução do projeto.

---



## 8. Cronograma de Desenvolvimento

O projeto é desenvolvido de forma incremental ao longo de quatro semanas. A cada entrega, uma nova camada funcional é adicionada ao sistema, garantindo que sempre haja algo testável na placa ao final de cada semana.


| Semana | Foco                           | Componentes entregues                                                    | Demonstrável na placa                                                                     |
| ------ | ------------------------------ | ------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------- |
| 1      | Base e decodificação Morse     | `morse_decoder.py`, `hardware.py` (botão + LEDs), `demo_morse.py`        | Pressionar botão → `.`/`-` no terminal, LED pisca, dígito exibido ao completar 5 símbolos |
| 2      | Feedback visual e persistência | `lcd_driver.py`, `lcd1602_driver.py`, `database.py`, `demo_validacao.py` | Digitar 4 dígitos em Morse → LCD mostra resultado, LED verde/vermelho, buzzer             |
| 3      | Integração via FSM             | `fsm.py` — máquina de estados completa                                   | Sistema completo funcionando na placa (sem interface web)                                 |
| 4      | Interface web e entrega final  | `app.py`, `templates/`, `static/`                                        | Sistema completo com monitoramento via browser                                            |




### 8.1 Entrega da Semana 1 — Base e Decodificação Morse

**Objetivo:** validar a lógica central do sistema (decodificação Morse) de forma isolada — primeiro sem hardware (testes unitários), depois na placa com botão e LED RGB.

**Artefatos entregues:** `src/morse_decoder.py`, `src/hardware.py`, `src/demo_morse.py`, `tests/test_morse_decoder.py`, `docs/relatorio.md`, `docs/diagramas/`.

**Demo no Raspberry Pi** (`python3 src/demo_morse.py`): toque curto → `.` + LED verde; toque longo → `-` + LED vermelho; 5 símbolos completos → dígito decodificado no terminal; sequência inválida → LED azul + buffer limpo.

**Requisitos cobertos:**

| Requisito | Cobertura |
| --------- | --------- |
| RF1 — Decodificação Morse | Completo (lógica + demo física) |
| RF1b — Fechamento por pausa | Completo (testado em TU-07 e no demo) |
| RNF2 — Sequências inválidas descartadas | Completo (TU-03, TU-04) |
| RF2, RF3, RF4, RF5 | Planejados — implementados nas Semanas 2–4 |

### 8.2 Resultados Obtidos — Semana 1

Os testes unitários foram executados na máquina de desenvolvimento antes da sessão de laboratório, com todos os 7 casos passando:

```
test_cancelar_limpa_buffer_e_senha ... ok
test_senha_completa_com_4_digitos ... ok
test_sequencia_de_5_simbolos_sem_mapeamento_retorna_erro ... ok
test_sequencia_incompleta_retorna_erro_e_nao_trava ... ok
test_todos_os_digitos_0_a_9 ... ok
test_toques_extras_apos_senha_completa_sao_ignorados ... ok
test_verificar_timeout_nao_fecha_antes_do_prazo ... ok

Ran 7 tests in 0.001s — OK
```

O demo `src/demo_morse.py` foi executado no Raspberry Pi com a placa Freenove. O botão S4 (GPIO 26) e o LED RGB (GPIO 5/6/13) responderam corretamente: toque curto acendeu o LED verde, toque longo acendeu o LED vermelho, e sequências inválidas acenderam o LED azul.

### 8.3 Lições Aprendidas — Semana 1

Dois problemas de usabilidade foram identificados durante o teste prático na placa:

**1. Ausência de botão para limpar o buffer**

Não há como o usuário desfazer uma digitação incorreta sem reiniciar o programa. Qualquer erro de toque obriga o usuário a aguardar 5 símbolos e depois tratar o erro. A adição de um **botão físico dedicado a cancelar/limpar** é essencial para a usabilidade do sistema e será implementada na Semana 2.

**2. Comportamento indesejado do timeout intra-dígito**

O comportamento atual do `morse_decoder.py` fecha o dígito (e o descarta como inválido) sempre que a pausa entre toques atinge 1 segundo, independentemente de quantos símbolos já foram registrados. Na prática, isso penaliza o usuário por demorar entre dois toques dentro do mesmo dígito, algo natural para iniciantes em Morse.

O comportamento desejado é:
- A pausa entre toques **não** deve fechar o dígito se ele ainda estiver incompleto (< 5 símbolos).
- O sistema deve continuar aguardando o próximo toque indefinidamente, preservando os símbolos já digitados.
- O dígito só deve ser validado após exatamente **5 símbolos** serem inseridos.
- O timeout de 1 segundo deve ser aplicado apenas ao **intervalo entre dígitos** (após o 5º símbolo), não dentro de um dígito.

Essa mudança requer revisão da lógica de `verificar_timeout()` em `morse_decoder.py` e será implementada na Semana 2.

### 8.4 Entrega da Semana 2 — Feedback visual e persistência

**Objetivo:** aplicar as correções de usabilidade descobertas na Semana 1 e integrar LCD, buzzer, botões Confirmar/Cancelar e validação de senha com registro em CSV.

**A Semana 2 parte das conclusões da Semana 1** — não apenas de novos requisitos. As duas limitações identificadas no teste físico mudaram a implementação:

| Lição Semana 1 | Mudança na implementação (Semana 2) |
| -------------- | ----------------------------------- |
| Sem botão para limpar o buffer | Botão **Cancelar** (GPIO 21): única forma de descartar digitação em andamento (`decoder.limpar()`). Confirmar **não** apaga buffer incompleto. |
| Timeout intra-dígito descartava símbolos | `verificar_timeout()` ignora buffer com < 5 símbolos (espera indefinida). Só fecha após exatamente 5 símbolos + pausa ≥ 1s (intervalo **entre** dígitos). Demos não fecham mais no 5º toque imediato. |
| `fechar_digito_se_completo` limpava incompleto | Agora retorna `None` e **preserva** o buffer se houver < 5 símbolos (só Cancelar limpa). |

**Artefatos entregues:** `src/lcd_driver.py`, `src/lcd1602_driver.py`, `src/database.py`, `src/data/alunos.json`, `src/demo_validacao.py`; atualizações em `src/hardware.py` e `src/morse_decoder.py`.

**Demais integrações desta semana:**

| Item | Descrição |
| ---- | --------- |
| Botão Confirmar | GPIO 16 — valida senha de 4 dígitos; se houver 5 símbolos pendentes, fecha o dígito sem esperar o gap |
| LCD 1602 I2C | Feedback em duas linhas; fallback para console se I2C ausente (RNF4) |
| Buzzer | GPIO 12 via `TonalBuzzer` (gpiozero), em thread própria (RNF3) |
| `database.py` | Valida senha em JSON e grava presença em CSV |
| Biblioteca GPIO | Apenas `gpiozero` — sem `RPi.GPIO` |

**Pinagem Freenove (BCM):** Morse S4=26; RGB=5/6/13 (`active_high=False`); Buzzer=12; Confirmar=16; Limpa=20; Cancelar=21; LCD I2C SDA/SCL=2/3.

**Demo:** `python3 src/demo_validacao.py`

**Requisitos cobertos nesta semana:** RF2, RF2b, RF3, RF4 (parcial — LCD+LED+buzzer), RNF2 (timeout revisado), RNF4 (LCD/buzzer opcionais).

### 8.5 Resultados Obtidos — Semana 2

Testes unitários (máquina de desenvolvimento), incluindo os novos casos de timeout e database — **12 testes OK**:

```
test_timeout_nao_descarta_digito_incompleto ... ok
test_timeout_fecha_apenas_digito_completo ... ok
test_validar_senha_conhecida ... ok
test_validar_senha_desconhecida ... ok
test_registrar_e_ler_historico ... ok
(+ 7 testes da Semana 1)

Ran 12 tests in 0.012s — OK
```

Testes de hardware previstos na placa: TH-03 (senha válida), TH-04 (cancelar), TH-05 (debounce).

---



## 9. Testes Planejados

A estratégia de validação é dividida em dois tipos: testes **unitários** (executáveis sem hardware, em qualquer máquina) e testes **de hardware** (executados no Raspberry Pi com os periféricos conectados).

### 9.1 Testes Unitários — `tests/test_morse_decoder.py`

Testam exclusivamente `morse_decoder.py`, sem dependência de GPIO. Executar com: `python3 -m unittest tests/test_morse_decoder.py -v`

| ID    | Descrição                                           | Status |
| ----- | --------------------------------------------------- | ------ |
| TU-01 | Todos os 10 dígitos (0–9) decodificados corretamente | S1 OK  |
| TU-02 | Senha de 4 dígitos montada corretamente             | S1 OK  |
| TU-03 | Fechar incompleto preserva buffer (não apaga)       | S2 OK  |
| TU-04 | Sequência de 5 símbolos sem mapeamento retorna ERRO | S1 OK  |
| TU-05 | Cancelar limpa buffer e senha                       | S1 OK  |
| TU-06 | Toques extras após senha completa são ignorados     | S1 OK  |
| TU-07 | Timeout não fecha dígito antes do prazo             | S1 OK  |
| TU-08 | Timeout não descarta dígito incompleto (< 5)        | S2 OK  |
| TU-09 | Timeout fecha apenas dígito completo (5 + pausa)    | S2 OK  |

### 9.2 Testes de Hardware — Executados no Raspberry Pi

| ID    | Req.  | Procedimento                                      | Resultado Esperado                           | Status   |
| ----- | ----- | ------------------------------------------------- | -------------------------------------------- | -------- |
| TH-01 | RF1   | `.----`: 1 toque curto + 4 longos                | Dígito "1" no terminal; LED pisca            | S1: OK   |
| TH-02 | RF1   | Sequência inválida `.-.-.` de 5 símbolos         | Mensagem de erro; LED azul; buffer limpo     | S1: OK   |
| TH-03 | RF2   | Digitar senha cadastrada e confirmar             | LED verde, buzzer sucesso, presença no CSV   | A validar na placa |
| TH-04 | RF3   | Digitar 2 dígitos e pressionar Cancelar          | Buffer zerado, sistema volta ao estado IDLE  | A validar na placa |
| TH-05 | RNF2  | Pressionar botão rapidamente (debounce)          | Apenas eventos com intervalo > 50ms contam  | A validar na placa |
| TH-06 | RNF4  | Iniciar sem LCD conectado                        | Sistema inicia; mensagens no console         | Semana 3 |

---



## 10. Conclusões

### 10.1 Conclusão da Semana 1

A primeira semana de desenvolvimento estabeleceu com sucesso a base do sistema de controle de acesso por código Morse. Os objetivos propostos foram cumpridos: a lógica de decodificação Morse foi implementada, validada por 7 testes unitários e demonstrada em funcionamento no Raspberry Pi com a placa Freenove, utilizando o botão S4 (GPIO 26) e o LED RGB integrado (GPIO 5/6/13).

A abordagem de validar a lógica isoladamente, antes de qualquer integração com hardware, mostrou-se eficiente: todos os testes unitários passaram sem necessidade de ajustes, e os problemas identificados no teste físico foram de usabilidade, não de lógica.

**Pontos positivos:**
- A separação entre lógica (`morse_decoder.py`) e hardware (`hardware.py`) facilitou o teste isolado e a depuração.
- O uso de componentes integrados da placa Freenove eliminou a necessidade de fiação externa na Semana 1, acelerando o setup.
- A metodologia TDD, escrever testes antes de integrar ao hardware, provou seu valor ao garantir confiança no módulo central antes da sessão prática.

**Limitações identificadas:**
- A ausência de um botão físico para cancelar/limpar o buffer torna o sistema difícil de usar quando o usuário comete um erro de digitação, pois não há forma de desfazer um toque incorreto sem aguardar o fim do processo.
- O mecanismo de timeout intra-dígito penaliza usuários iniciantes em Morse: uma pausa natural entre dois toques do mesmo dígito invalida toda a sequência acumulada até aquele momento, causando frustração e perda de dados já inseridos.

**Encaminhamentos para a Semana 2:**
Ambas as limitações identificadas serão corrigidas na próxima entrega. Será adicionado um botão físico de cancelamento e a lógica de timeout será revisada para aguardar indefinidamente até a inserção do 5º símbolo, aplicando o timeout de intervalo apenas entre dígitos completos. Essas mudanças tornarão o sistema mais robusto e adequado ao uso prático na placa.

*(A conclusão final do projeto será elaborada na Semana 4, após a execução completa de todos os requisitos e testes de integração.)*

---



## Referências

RASPBERRY PI FOUNDATION. **Physical computing with Python**. Disponível em: [https://projects.raspberrypi.org/en/projects/physical-computing](https://projects.raspberrypi.org/en/projects/physical-computing). Acesso em: 27 jul. 2026.

GPIOZERO CONTRIBUTORS. **gpiozero Documentation**. Disponível em: [https://gpiozero.readthedocs.io](https://gpiozero.readthedocs.io). Acesso em: 27 jul. 2026.

FREENOVE. **Freenove Ultimate Starter Kit for Raspberry Pi — Tutorial**. Disponível em: [https://docs.freenove.com/projects/fnk0054/en/latest](https://docs.freenove.com/projects/fnk0054/en/latest). Acesso em: 27 jul. 2026.

INTERNATIONAL TELECOMMUNICATION UNION. **ITU-R M.1677-1: International Morse code**. Genebra: ITU, 2009. Disponível em: [https://www.itu.int/rec/R-REC-M.1677/en](https://www.itu.int/rec/R-REC-M.1677/en). Acesso em: 27 jul. 2026.

FLASK CONTRIBUTORS. **Flask Documentation (3.x)**. Disponível em: [https://flask.palletsprojects.com](https://flask.palletsprojects.com). Acesso em: 27 jul. 2026.

PYTHON SOFTWARE FOUNDATION. **threading — Thread-based parallelism**. Disponível em: [https://docs.python.org/3/library/threading.html](https://docs.python.org/3/library/threading.html). Acesso em: 27 jul. 2026.
