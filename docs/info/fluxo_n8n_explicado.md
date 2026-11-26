# Classificador Inteligente de Mensagens de Atendimento

Solução de Inteligência Artificial e Automação desenvolvida como projeto integrador para triagem, classificação e roteamento automático de mensagens de clientes.

---

## Fluxo N8N
1. Um **Webhook** no n8n recebe a mensagem do cliente em formato JSON.
2. O fluxo envia os dados para uma **API REST em Python (FastAPI)**, que aplica engenharia de prompt estruturada e utiliza o modelo **Google Gemini** com *Structured Outputs* (validado via Pydantic) para classificar a mensagem estritamente em JSON (`categoria`, `prioridade`, `setor_destino` e `resumo_curto`).
3. O **n8n** interpreta o retorno da IA e utiliza um roteador condicional (**Switch**) para encaminhar automaticamente o atendimento à fila do departamento correspondente (`Financeiro`, `Suporte Técnico` ou `Comercial`).

## Funcionamento do Sistema

### Arquitetura e Fluxo de Dados
```text
[1. Webhook (POST)] ──▶ [2. HTTP Request (FastAPI + Gemini)] ──▶ [3. Switch (Setor)] ──┬──▶ [4A. Set - Financeiro]
                                                                                        ├──▶ [4B. Set - Suporte Técnico]
                                                                                        └──▶ [4C. Set - Comercial]
```

1. **Recepção (API FastAPI):** O endpoint `POST /classificar` recebe um payload JSON contendo `cliente` e `mensagem`, valida os tipos de entrada com Pydantic e injeta os dados em um prompt com regras estritas de classificação.

2. **Processamento com IA:** O modelo `gemini-2.5-flash` analisa o contexto da mensagem com baixa temperatura (`0.1`) e retorna um objeto JSON garantido pelo schema `ClassificacaoSaida`.

3. **Execução da Automação (n8n):** O fluxo escuta chamadas externas no Webhook `/atendimento`, consulta a API local (`http://localhost:8000/classificar`), avalia o campo `setor_destino` no node *Switch* e registra o encaminhamento na fila do setor específico.

---

### Documentação Visual e Explicação Técnica dos Nodes

#### 1. Visão Geral do Fluxo Completo
![Fluxo Completo](docs/01_fluxo_completo.png)
* **Função:** Demonstra a estrutura completa da automação no n8n, conectando o gatilho de entrada (*Webhook*), a chamada de inteligência (*HTTP Request*), a tomada de decisão (*Switch*) e os destinos finais por departamento (*Edit Fields / Set*).

#### 2. Execução Bem-Sucedida
![Execução Bem-Sucedida](docs/02_execucao_sucesso.png)
* **Função:** Comprova o histórico de execução concluída com sucesso (`Succeeded`), validando a comunicação integrada entre o n8n e a API FastAPI em tempo de execução.

#### 3. Configuração Interna dos Nodes
![Configuração dos Nodes](docs/03_config_nodes.png)
* **Node 1 — Webhook (`n8n-nodes-base.webhook`):** Configurado com método `POST` e path `atendimento` (`http://localhost:5678/webhook-test/atendimento`). Recebe o JSON inicial do cliente e disponibiliza os dados em `$json.body`.
* **Node 2 — HTTP Request - API IA (`n8n-nodes-base.httpRequest`):** Configurado para enviar uma requisição `POST` para `http://localhost:8000/classificar` com *Body Content Type* em `JSON`, mapeando dinamicamente os campos:
  ```json
  {
    "cliente": "{{ $json.body.cliente }}",
    "mensagem": "{{ $json.body.mensagem }}"
  }
  ```
* **Node 3 — Switch - Roteamento Setor (`n8n-nodes-base.switch`):** Configurado no modo *Rules* avaliando a expressão `{{ $json.setor_destino }}` com três regras de igualdade (`equals`): `Financeiro`, `Suporte Técnico` e `Comercial`.
* **Node 4 — Edit Fields / Set (`Set - Fila Financeiro`, `Set - Fila Suporte`, `Set - Fila Comercial`):** Mantém os campos retornados pela IA (*Include Other Input Fields*) e adiciona o campo `status_encaminhamento` com a expressão `Encaminhado para fila do setor: {{ $json.setor_destino }} (Prioridade: {{ $json.prioridade }})`.

#### 4. Resultados e Dados Processados
![Resultados e Dados](docs/04_resultados_dados.png)
* **Função:** Evidencia a transformação dos dados ao longo do fluxo: a entrada em texto livre é convertida pela IA em um JSON estruturado (`categoria: "Reclamação"`, `prioridade: "Alta"`, `setor_destino: "Financeiro"`) e roteada exclusivamente para a saída do setor Financeiro.

---

## 6. Como Executar

### Pré-requisitos
* Python 3.10 ou superior
* Node.js 22 ou abaixo 26 (para execução local do n8n)
* Chave de API gratuita do Google AI Studio (`GEMINI_API_KEY`)

### Passo a Passo para Instalação e Execução

1. **Clone o repositório e acesse a pasta do projeto:**
   ```bash
   git clone <URL_DO_SEU_REPOSITORIO>
   cd <NOME_DA_PASTA>
   ```

2. **Crie e ative o ambiente virtual Python:**
   ```bash
   python -m venv venv
   # No Windows:
   venv\Scripts\activate
   # No Linux/Mac:
   source venv/bin/activate
   ```

3. **Instale as dependências da API:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente:**
   * Copie o arquivo `.env.example` para um novo arquivo chamado `.env`:
     ```bash
     cp .env.example .env
     ```
   * Abra o arquivo `.env` e insira sua chave da API do Gemini:
     ```env
     GEMINI_API_KEY=sua_chave_api_aqui
     ```

5. **Inicie o servidor da API FastAPI:**
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   A API ficará disponível em `http://localhost:8000` (documentação interativa em `http://localhost:8000/docs`).

6. **Inicie o n8n e importe o fluxo:**
   * Em um segundo terminal, execute:
     ```bash
     npx n8n
     ```
   * Acesse `http://localhost:5678` no navegador, crie um novo workflow, clique no menu **`...` > Import from File...** e selecione o arquivo `fluxo_n8n.json` localizado na raiz deste repositório.

7. **Teste a integração:**
   * Clique em **Test Workflow** no n8n e envie uma requisição `POST` para `http://localhost:5678/webhook-test/atendimento` com o seguinte corpo JSON:
     ```json
     {
       "cliente": "João Silva",
       "mensagem": "Minha fatura veio cobrando o dobro esse mês, preciso de estorno urgente!"
     }
     ```