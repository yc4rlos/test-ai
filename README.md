# Where is this AI

Aplicação composta por duas APIs que permitem conversar com o Gemini e consultar
endereços brasileiros a partir de um CEP. Quando uma mensagem contém uma
solicitação de endereço, o modelo pode chamar automaticamente a ferramenta de
consulta de CEP exposta via MCP.

## Funcionalidades

- Chat com o modelo Gemini por meio de uma API REST.
- Identificação, pelo modelo, de mensagens que exigem uma consulta de CEP.
- Consulta de CEP com ou sem formatação usando o serviço ViaCEP.
- Exposição da consulta de CEP como endpoint REST e como ferramenta MCP.
- Hot reload das duas APIs durante o desenvolvimento.
- Documentação OpenAPI interativa gerada pelo FastAPI.

## Arquitetura

O projeto é dividido em dois serviços:

### `llm-api`

API principal, disponível na porta `8000`. Recebe uma mensagem em `POST /chat`,
envia o conteúdo ao Gemini e disponibiliza ao modelo as ferramentas encontradas
no servidor MCP. Quando necessário, executa a ferramenta de CEP e usa o resultado
para produzir a resposta final.

### `cep-tool-api`

API de consulta de CEP. Internamente, ela consulta o ViaCEP e expõe a mesma
funcionalidade de duas formas:

- `GET /cep/{cep}`: endpoint REST para consulta direta.
- `/mcp`: servidor MCP consumido pela `llm-api`.

Com Docker Compose, os serviços compartilham a rede `api-network`. O endereço
interno do MCP é `http://cep-tool-api:8000/mcp`. A porta `8001` é usada somente
para acessar a API de CEP a partir da máquina host.

```text
Cliente -> llm-api:8000 -> Gemini
                     |
                     +-> MCP -> cep-tool-api:8000 -> ViaCEP

Cliente ----------------> localhost:8001/cep/{cep}
```

## Bibliotecas

### Compartilhadas

- **FastAPI**: criação das APIs REST e documentação OpenAPI.
- **FastMCP**: servidor e cliente do protocolo MCP.
- **Uvicorn**: servidor ASGI com suporte a hot reload.

### `llm-api`

- **LangChain**: integração do modelo com ferramentas.
- **langchain-google-genai**: integração do LangChain com o Gemini.
- **Pydantic**: validação dos dados das requisições.
- **python-dotenv**: carregamento das variáveis de ambiente.

### `cep-tool-api`

- **HTTPX**: requisições HTTP ao ViaCEP.

O gerenciamento de dependências e ambientes Python é feito com o **uv**.

## Executando com Docker Compose

### Pré-requisitos

- Docker com o plugin Docker Compose.
- Uma chave de API do Google Gemini.

Na raiz do projeto, crie o arquivo de variáveis de ambiente:

```bash
cp example.env .env
```

Preencha a chave em `.env` e mantenha a URL interna do MCP:

```dotenv
GOOGLE_API_KEY=sua_chave_aqui
CEP_MCP_URL=http://cep-tool-api:8000/mcp
```

Construa e inicie os dois serviços:

```bash
docker compose up --build
```

Para executar em segundo plano:

```bash
docker compose up --build -d
```

Os volumes configurados no Compose refletem alterações no código local e o
Uvicorn reinicia automaticamente o serviço correspondente.

Para acompanhar os logs ou encerrar os serviços:

```bash
docker compose logs -f
docker compose down
```

Endereços disponíveis:

- API principal: `http://localhost:8000`
- Swagger da API principal: `http://localhost:8000/docs`
- API de CEP: `http://localhost:8001`
- Swagger da API de CEP: `http://localhost:8001/docs`

## Executando sem Docker

### Pré-requisitos

- Python 3.14 ou superior.
- [uv](https://docs.astral.sh/uv/).
- Uma chave de API do Google Gemini.

Crie o arquivo de ambiente da API principal:

```bash
cp example.env llm-api/.env
```

Preencha a chave e altere o endereço do MCP para `localhost`, pois os processos
serão executados diretamente na máquina:

```dotenv
GOOGLE_API_KEY=sua_chave_aqui
CEP_MCP_URL=http://localhost:8001/mcp
```

Em um terminal, instale as dependências e inicie a API de CEP:

```bash
cd cep-tool-api
uv sync
uv run uvicorn server:app --reload --port 8001
```

Em outro terminal, instale as dependências e inicie a API principal:

```bash
cd llm-api
uv sync
uv run uvicorn server:app --reload --port 8000
```

## Testando

Consulte diretamente um CEP:

```bash
curl http://localhost:8001/cep/01001000
```

Envie uma mensagem para o chat:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Qual e o endereco do CEP 01001-000?"}'
```

A resposta do chat possui o formato:

```json
{
  "response": "Resposta gerada pelo modelo"
}
```