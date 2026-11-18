# Miniprojeto CTMC — Controle de Admissão

Disciplina: **ADS29009 — Avaliação de Desempenho de Sistemas**

Modelagem e análise de uma rede com duas classes de tráfego por meio de uma Cadeia de Markov a Tempo Contínuo (CTMC).

## Parâmetros do sistema

- Capacidade total: \(C = 5\) unidades.
- Reserva mínima para tráfego prioritário T1: \(R = 2\) unidades.
- Taxas de chegada: \(\lambda_1 = 10\) req/min e \(\lambda_2 = 15\) req/min.
- Taxas de serviço: \(\mu_1 = 15\) req/min e \(\mu_2 = 25\) req/min.

O estado é representado por \((n_1,n_2)\), em que \(n_1\) e \(n_2\) são as quantidades de conexões T1 e T2. Os estados válidos respeitam:

\[
n_1+n_2 \leq 5, \qquad n_2 \leq C-R=3.
\]

## Estrutura dos arquivos

```text
Exercicio_3_CTMC_Controle_Admissao/
├── README.md
├── MODELAGEM_ETAPA_1.md
├── ETAPA_2_RESULTADOS.md
├── modelagem_ctmc.py
├── analise_ctmc.py
├── test_modelagem_ctmc.py
├── test_analise_ctmc.py
├── requirements.txt
└── resultados/
    ├── estados.csv
    ├── matriz_Q.csv
    ├── distribuicao_estacionaria.csv
    └── indicadores_etapa2.csv
```

## Preparação do ambiente

**Requisitos:** Python 3.10 ou superior e pip.

Abra o terminal dentro da pasta `Exercicio_3_CTMC_Controle_Admissao`.

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Etapa 1 — Estados e matriz Q

Execute:

```bash
python modelagem_ctmc.py
```

O programa gera os 18 estados válidos, constrói a matriz infinitesimal Q (18 × 18), verifica se cada linha soma zero e exporta os arquivos `estados.csv` e `matriz_Q.csv` para a pasta `resultados/`.

## Etapa 2 — Equilíbrio e indicadores

Execute:

```bash
python analise_ctmc.py
```

O programa resolve o sistema estacionário \(\pi Q = 0\), com \(\sum_s \pi(s)=1\), confere a solução pela forma-produto e calcula os indicadores de desempenho. Os resultados são exportados para:

- `resultados/distribuicao_estacionaria.csv`
- `resultados/indicadores_etapa2.csv`

A análise apresenta duas interpretações para o bloqueio de T2: a expressão literal da página 14 (\(n_2=R\)) e a regra compatível com os estados e a matriz Q (\(n_2=C-R\)). A divergência está explicada em [ETAPA_2_RESULTADOS.md](ETAPA_2_RESULTADOS.md) e precisa ser confirmada com o professor.

## Testes automatizados

Para executar os testes das Etapas 1 e 2:

```bash
python -m unittest -v
```

## Observação sobre o bloqueio de T2

A página 11 do material limita \(n_2\) a \(C-R=3\), e a matriz Q segue essa regra. Já a página 14 utiliza \(n_2=R=2\) na definição do bloqueio de T2. Como as condições divergem, o programa apresenta os dois cálculos separadamente, sem escolher silenciosamente uma das interpretações.

## Próxima etapa

A Etapa 3 será a simulação da CTMC durante \(T=10.000\) minutos, seguida da comparação entre a distribuição e os indicadores simulados e os resultados analíticos desta etapa.
