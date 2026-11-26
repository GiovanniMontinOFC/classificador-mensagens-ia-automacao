# Classificador Inteligente de Mensagens de Atendimento

> PROJETO KODIE ACADEMY 

> DESAFIO MÓDULO 1 E 2

> AUTOR: Giovanni Montin Barbosa

## 1. Apresentação da Ideia (StoryTelling) 
A ideia surgiu da necessidade de eliminar a triagem manual de mensagens recebidas por equipes de atendimento, utilizando Inteligência Artificial para interpretar textos livres e automação para rotear demandas em tempo real.

## 2. Problema Escolhido
**Caso 4.1 — Classificação de Mensagens:** Pequenas empresas recebem dezenas de mensagens diárias com dúvidas, reclamações e solicitações misturadas. Sem triagem automática, o tempo de resposta aumenta e mensagens urgentes acabam atrasadas.

## 3. Solução Proposta
Uma arquitetura integrada onde um Webhook recebe a mensagem do cliente, envia para uma API em Python que utiliza o modelo Gemini para classificar o texto em formato JSON estrito (categoria, prioridade, setor e resumo) e devolve os dados para o n8n encaminhar automaticamente ao setor responsável.

## 4. Tecnologias Utilizadas
* **Inteligência Artificial:** Google Gemini API (`gemini-2.5-flash`) com Structured Outputs.
* **Back-end:** Python 3, FastAPI, Uvicorn e Pydantic.
* **Automação:** n8n (executado localmente).

## 5. Funcionamento do Sistema
1. **Entrada:** O n8n recebe um payload JSON via Webhook contendo `cliente` e `mensagem`.
2. **Processamento IA:** O n8n faz uma requisição POST para o endpoint `/classificar` da API FastAPI. O back-end aplica um prompt estruturado e força a resposta em JSON validado pelo Pydantic.
3. **Roteamento:** O n8n lê o campo `setor_destino` retornado pela API e utiliza um node *Switch* para direcionar o atendimento ao fluxo do departamento correto.

### Documentação Visual do Fluxo
* **PDF Contendo imagens e explicação**
  ![PDF] (docs/00_etapas_explicadas.pdf)
* **Fluxo Completo:**
  ![Fluxo Completo](docs/01_fluxo_completo.png)
* **Execução Bem-Sucedida:**
  ![Execução](docs/02_execucao_sucesso.png)
* **Configuração Interna dos Nodes (Webhook, HTTP Request e Switch):**
  ![Configuração](docs/03_config_nodes.png)
* **Resultados e Dados Processados (Saída JSON):**
  ![Resultados](docs/04_resultados_dados.png)

## 6. Como Executar
1. Clone o repositório e acesse a pasta do projeto.
2. Crie e ative o ambiente virtual Python: `python -m venv venv`
3. Instale as dependências: `pip install -r requirements.txt`
4. Renomeie `.env.example` para `.env` e insira sua chave gratuita do Google AI Studio.
5. Inicie a API: `uvicorn main:app --reload --port 8000`
6. Em outro terminal, inicie o n8n: `npx n8n`
7. Importe o arquivo `fluxo_n8n.json` no painel do n8n e ative o fluxo.