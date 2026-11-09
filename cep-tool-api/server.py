from fastapi import FastAPI
from fastmcp import FastMCP
from tools.cep_tool import get_address_by_cep
from services.cepservice import CepService

mcp = FastMCP("cep-tool-api")
mcp.tool(get_address_by_cep)
mcp_app = mcp.http_app(path="/")
app = FastAPI(lifespan=mcp_app.lifespan)
app.mount("/mcp", mcp_app)


@app.get("/cep/{cep}")
def get_cep(cep: str):
    service = CepService()
    return service.get_address_by_cep(cep)