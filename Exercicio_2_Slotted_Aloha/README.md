# Exercício 2 — Slotted Aloha com probabilidade adaptativa

**Disciplina:** Avaliação de Desempenho de Sistemas — IFSC  
**Modelo:** cadeia de Markov em tempo discreto (DTMC), com cinco estações.

Este guia reúne a modelagem matemática, a implementação em Python, os testes, os resultados de referência e as instruções de execução. Para evitar problemas de exibição, as fórmulas estão escritas em blocos de texto simples, em vez de depender de um renderizador de LaTeX.

## 1. O que o exercício pede

O enunciado considera um sistema Slotted Aloha com cinco estações e probabilidade de transmissão adaptativa. O trabalho pede:

1. Definir uma DTMC e justificar o espaço de estados.
2. Construir o diagrama de transições e a matriz de transição P.
3. Determinar a distribuição estacionária.
4. Calcular a vazão média, em pacotes entregues por slot.
5. Determinar a proporção de slots ociosos.
6. Apresentar exemplos numéricos que respeitem 0 < b < a < 1.

O programa calcula os resultados teóricos para os valores escolhidos de a e b e executa uma simulação de Monte Carlo para comparação.

## 2. Regras do sistema

- Existem cinco estações, identificadas de 1 a 5.
- Uma estação que não está em adaptação transmite com probabilidade a em cada slot.
- Se uma estação participou de uma colisão no slot anterior, ela utiliza a probabilidade b no slot atual, com 0 < b < a < 1.
- Se exatamente uma estação transmitir, o pacote é entregue com sucesso.
- Se nenhuma estação transmitir, o slot fica ocioso.
- Se duas ou mais estações transmitirem, ocorre colisão e os pacotes envolvidos são descartados.
- As estações que colidem no slot atual usarão b no slot seguinte. As demais usarão a no slot seguinte.
- Cada estação usa a probabilidade reduzida por apenas um slot. Não há fila persistente nem retransmissão dos pacotes descartados neste exercício.

As decisões de transmissão são consideradas independentes entre as estações, condicionadas ao estado atual.

## 3. Definição da DTMC

### 3.1 Espaço de estados

O estado guarda o conjunto de estações que participaram da colisão no slot imediatamente anterior. O estado vazio significa que nenhuma estação precisa usar a probabilidade reduzida.

Definição do espaço de estados:

~~~text
S = {∅} ∪ { A : A é subconjunto de {1, 2, 3, 4, 5} e |A| ≥ 2 }
~~~

Exemplos:

- ∅: todas as estações usam a probabilidade a.
- {1, 3}: as estações 1 e 3 colidiram no slot anterior e usam b no slot atual; as outras usam a.
- {1, 2, 3, 4, 5}: as cinco estações colidiram no slot anterior e usam b no slot atual.

Um estado não vazio deve conter pelo menos duas estações, pois uma colisão exige duas ou mais transmissões. Um conjunto com apenas uma estação não é estado: nesse caso houve sucesso, e nenhuma estação precisa usar b no slot seguinte.

Quantidade de estados:

~~~text
Número de estados = 1 + C(5,2) + C(5,3) + C(5,4) + C(5,5)
                  = 1 + 10 + 10 + 5 + 1
                  = 27
~~~

Essa representação registra a informação necessária para saber quais estações usam a probabilidade b no slot atual. Portanto, as probabilidades do próximo estado dependem somente do estado atual, como exige uma DTMC.

### 3.2 Probabilidade de transmissão por estação

Para um estado atual A, a probabilidade de transmissão da estação i é:

~~~text
p_i(A) = b, se i pertence a A
p_i(A) = a, se i não pertence a A
~~~

Se T for exatamente o conjunto de estações que transmitem no slot atual, então a probabilidade desse conjunto de transmissões é:

~~~text
Pr(T | A) =
    produto de p_i(A) para todas as estações i em T
    multiplicado por
    produto de [1 - p_j(A)] para todas as estações j fora de T
~~~

Em outras palavras, as estações em T transmitem e todas as outras ficam em silêncio.

### 3.3 Matriz de transição P

O próximo estado é o conjunto exato de estações que colidiram no slot atual.

Para qualquer conjunto T com pelo menos duas estações:

~~~text
P(A, T) = Pr(T | A)
~~~

O próximo estado será vazio quando nenhuma estação transmitir ou quando exatamente uma estação transmitir. Logo:

~~~text
P(A, ∅) =
    probabilidade de nenhuma estação transmitir
    +
    probabilidade de exatamente uma estação transmitir
~~~

Escrevendo os dois termos por meio das probabilidades individuais:

~~~text
P(A, ∅) =
    produto de [1 - p_i(A)] para i = 1, ..., 5
    +
    soma, para cada estação i, de:
        p_i(A) × produto de [1 - p_j(A)] para todas as estações j diferentes de i
~~~

O primeiro termo representa um slot ocioso. O segundo representa um slot com uma única transmissão bem-sucedida. Ambos levam ao estado vazio porque não houve colisão.

A matriz P tem dimensão 27 × 27. Cada linha representa o estado atual e cada coluna representa o próximo estado. A soma dos elementos de cada linha deve ser igual a 1:

~~~text
Soma de P(A, T) para todos os possíveis estados T = 1
~~~

O programa calcula a matriz e informa o maior erro numérico encontrado nessa verificação.

#### Exemplo: transições a partir do estado vazio

No estado vazio, todas as cinco estações usam a probabilidade a. A probabilidade de nenhuma estação transmitir ou de exatamente uma transmitir é:

~~~text
P(∅, ∅) = (1 - a)^5 + 5 × a × (1 - a)^4
~~~

Para um estado T com k estações, em que k é pelo menos 2:

~~~text
P(∅, T) = a^k × (1 - a)^(5-k)
~~~

Com a = 0,30, os valores dessa linha são:

| Próximo estado | Probabilidade |
|---|---:|
| Estado vazio | 0,52822 |
| Cada estado com 2 estações em colisão | 0,03087 |
| Cada estado com 3 estações em colisão | 0,01323 |
| Cada estado com 4 estações em colisão | 0,00567 |
| Estado com as 5 estações em colisão | 0,00243 |

Existem 10 estados com duas estações, 10 com três, 5 com quatro e 1 com cinco. Somando as probabilidades de todos os 27 destinos, o resultado é 1.

O programa exporta a matriz completa para o arquivo resultados/matriz_transicao_P.csv. A primeira coluna indica o estado de origem; as demais colunas representam os estados de destino.

### 3.4 Diagrama de transições

O diagrama completo contém 27 estados e muitas transições. A regra geral é:

1. Considere o estado atual A e as probabilidades de transmissão correspondentes.
2. Se zero ou uma estação transmitir, a transição vai para o estado vazio.
3. Se duas ou mais estações transmitirem, a transição vai para o conjunto T formado por exatamente essas estações.
4. A probabilidade de cada transição é a probabilidade de ocorrer aquele conjunto de transmissões.

Esquema simplificado:

~~~mermaid
flowchart TD
    A["Estado atual A"] -->|"Nenhuma ou uma transmissão"| E["Próximo estado: vazio"]
    A -->|"Duas ou mais transmissões"| T["Próximo estado: conjunto T que colidiu"]
~~~

Esse esquema apresenta a regra geral. O programa calcula individualmente as probabilidades para todos os estados e destinos possíveis.

### 3.5 Distribuição estacionária

A distribuição estacionária, indicada por pi, representa a proporção de longo prazo em que a cadeia permanece em cada estado.

O sistema a resolver é:

~~~text
pi × P = pi
Soma de pi(A) para todos os estados A = 1
~~~

O programa resolve esse sistema numericamente com NumPy. Como 0 < b < a < 1, os padrões possíveis de transmissão têm probabilidades positivas. A cadeia é comunicante e possui uma distribuição estacionária única.

### 3.6 Vazão média

A vazão é o número médio de pacotes entregues com sucesso por slot. Para haver sucesso, exatamente uma das cinco estações deve transmitir.

A probabilidade de sucesso, dado o estado atual A, é:

~~~text
Q(A) =
    soma, para cada estação i, de:
        p_i(A) × produto de [1 - p_j(A)] para todas as estações j diferentes de i
~~~

A vazão média pondera essa probabilidade pela distribuição estacionária:

~~~text
Q = soma, para todos os estados A, de pi(A) × Q(A)
~~~

A unidade de Q é pacotes entregues por slot.

### 3.7 Proporção de slots ociosos

Um slot fica ocioso quando nenhuma estação transmite. Dado o estado A, essa probabilidade é:

~~~text
I(A) = produto de [1 - p_i(A)] para i = 1, ..., 5
~~~

A proporção média de slots ociosos é:

~~~text
I = soma, para todos os estados A, de pi(A) × I(A)
~~~

A proporção de slots com colisão pode ser obtida por diferença:

~~~text
C = 1 - Q - I
~~~

A vazão Q, a proporção de slots ociosos I e a proporção de slots com colisão C devem somar 1, salvo pequenas diferenças de arredondamento.

## 4. Arquivos do projeto

~~~text
Exercicio_2_Slotted_Aloha/
├── README.md
├── slotted_aloha.py
├── test_model.py
├── requirements.txt
├── .gitignore
└── resultados/                  (criada ao executar)
    ├── resumo_resultados.json
    ├── distribuicao_estacionaria.csv
    └── matriz_transicao_P.csv
~~~

- **slotted_aloha.py:** cria os 27 estados, monta P, calcula a distribuição estacionária e as métricas, executa a simulação e grava os resultados.
- **test_model.py:** contém cinco testes automatizados das propriedades matemáticas do modelo.
- **requirements.txt:** lista a dependência NumPy.
- **resultados/resumo_resultados.json:** reúne os resultados teóricos e simulados.
- **resultados/distribuicao_estacionaria.csv:** mostra a probabilidade estacionária de cada estado e as métricas condicionais.
- **resultados/matriz_transicao_P.csv:** contém a matriz de transição completa, de dimensão 27 × 27.

A pasta resultados é criada automaticamente. Os arquivos CSV e JSON gerados são ignorados pelo Git para que as execuções não alterem o repositório.

## 5. Requisitos

- Python 3.9 ou superior.
- pip.
- NumPy.

Para conferir se Python e pip estão disponíveis, execute:

    python3 --version
    python3 -m pip --version

## 6. Como executar no Linux

### Passo 1 — Clonar o repositório

Execute no terminal:

    git clone https://github.com/BeatrizPAbreu/ADS.git
    cd ADS/Exercicio_2_Slotted_Aloha

Se o repositório já estiver no computador, entre diretamente na pasta do exercício.

### Passo 2 — Criar e ativar um ambiente virtual

    python3 -m venv .venv
    source .venv/bin/activate

O ambiente virtual mantém as bibliotecas deste projeto separadas das demais instalações Python.

### Passo 3 — Instalar a dependência

    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt

### Passo 4 — Executar o programa

O exemplo usa a = 0,30 e b = 0,10, com 100.000 slots na simulação:

    python slotted_aloha.py --a 0.30 --b 0.10 --simulate 100000 --seed 2026

O terminal apresenta os resultados teóricos e simulados. Os arquivos são salvos na pasta resultados.

### Passo 5 — Abrir os resultados

- Abra resultados/resumo_resultados.json em um editor de texto.
- Abra resultados/distribuicao_estacionaria.csv no LibreOffice Calc, Excel ou outro leitor de CSV.
- Abra resultados/matriz_transicao_P.csv no Calc ou Excel para inspecionar a matriz de transição.

### Passo 6 — Executar os testes

Com o ambiente virtual ativado:

    python -m unittest -v

Os testes verificam a quantidade de estados, as somas das linhas da matriz P, a distribuição estacionária e a soma das probabilidades de sucesso, ociosidade e colisão.

### Windows (PowerShell)

Depois de entrar na pasta do exercício, execute:

    py -m venv .venv
    .\.venv\Scripts\Activate.ps1
    py -m pip install -r requirements.txt
    py slotted_aloha.py --a 0.30 --b 0.10 --simulate 100000 --seed 2026
    py -m unittest -v

## 7. Parâmetros do programa

| Parâmetro | Significado | Valor padrão |
|---|---|---:|
| --a | Probabilidade de transmissão normal | 0.30 |
| --b | Probabilidade reduzida depois de uma colisão | 0.10 |
| --simulate | Número de slots da simulação Monte Carlo | 100000 |
| --seed | Semente aleatória para reproduzir a simulação | 2026 |
| --output-dir | Pasta para salvar CSV e JSON | resultados |

Os parâmetros devem respeitar 0 < b < a < 1. O programa informa um erro se os valores não satisfizerem essa condição ou se o número de slots não for positivo.

Exemplos com outras configurações:

    python slotted_aloha.py --a 0.20 --b 0.05 --simulate 200000 --seed 7
    python slotted_aloha.py --a 0.40 --b 0.10 --simulate 200000 --seed 7 --output-dir resultados_a040_b010

O segundo comando grava os resultados em outra pasta e preserva os arquivos da configuração anterior.

## 8. Resultados numéricos de referência

Para a = 0,30, b = 0,10, 100.000 slots simulados e semente 2026, a execução de referência apresentou:

| Métrica | DTMC (teórico) | Monte Carlo (100.000 slots) |
|---|---:|---:|
| Vazão (pacotes/slot) | 0,383423 | 0,381430 |
| Slots ociosos | 22,3211% | 22,2420% |
| Slots com colisão | 39,3366% | 39,6150% |

Verificações numéricas:

- Foram construídos 27 estados.
- A soma das probabilidades da distribuição estacionária é 1.
- A soma de cada linha da matriz P é 1, com erro numérico máximo da ordem de 10⁻¹⁵.
- Vazão + proporção de slots ociosos + proporção de slots com colisão = 1, salvo arredondamento.

Os resultados empíricos variam com a semente e com a quantidade de slots simulados. Para os mesmos valores de a e b, os resultados teóricos devem permanecer iguais.

## 9. Como interpretar os resultados

- **Vazão:** 0,383423 significa que são entregues, em média, cerca de 0,383 pacotes por slot no longo prazo. Não significa que 38,3% das estações transmitem.
- **Slots ociosos:** aproximadamente 22,32% dos slots não têm transmissão.
- **Slots com colisão:** aproximadamente 39,34% dos slots têm duas ou mais transmissões. Os pacotes envolvidos são descartados e não contam para a vazão.
- **Teoria versus simulação:** os resultados devem ser próximos, mas não idênticos, por causa da variação aleatória e do número finito de slots.
- **Efeito de a e b:** a determina a probabilidade normal de transmissão, enquanto b reduz temporariamente a probabilidade das estações que colidiram. A mudança de vazão depende dos dois parâmetros; não se deve concluir que diminuir b sempre aumenta a vazão sem comparar configurações.

Para aprofundar a discussão, execute o programa com diferentes pares de valores de a e b, anote as três métricas e compare os efeitos sobre o desempenho.

## 10. Hipóteses e limites

- São consideradas cinco estações e slots sincronizados.
- Cada estação tenta transmitir no máximo um pacote por slot.
- Um sucesso entrega exatamente um pacote.
- Os pacotes envolvidos em colisões são descartados.
- Não há fila persistente nem retransmissão neste exercício.
- As decisões de transmissão são independentes, condicionadas ao estado atual.
- Os valores da tabela são um exemplo. Se o professor fornecer outros valores, use-os nos argumentos do programa.

## 11. Checklist de entrega

- [x] Definição e justificativa dos estados da DTMC.
- [x] Matriz de transição P construída e exportada em CSV.
- [x] Distribuição estacionária calculada numericamente.
- [x] Vazão média calculada.
- [x] Proporção de slots ociosos calculada.
- [x] Exemplo numérico e comparação com simulação.
- [x] Instruções de instalação, execução e interpretação.
- [x] Testes automatizados.

**Importante:** a = 0,30 e b = 0,10 são valores de exemplo, não valores impostos pelo enunciado. Se o professor determinar outros valores, informe-os pelos argumentos --a e --b e execute o programa novamente.
