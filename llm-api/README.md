# APIs

A API principal expoe `POST /chat`. A API de CEP expoe `GET /cep?cep=01001000`
e a ferramenta `get_address_by_cep` via MCP HTTP em `/mcp`.

Inicie a API de CEP em um terminal, a partir deste diretorio:

```bash
cd tools/cep-tool-api
uv run uvicorn server:app --reload --port 8001
```

Em outro terminal, inicie a API principal a partir deste diretorio:

```bash
uv sync --no-install-project
uv run --no-project --python .venv/bin/python uvicorn server:app --reload --port 8000
```

Configure `GOOGLE_API_KEY` no `.env` da API principal. `CEP_MCP_URL` e opcional
e usa `http://localhost:8001/mcp` por padrao. Inicie a API de CEP antes de enviar
mensagens para `/chat`.
