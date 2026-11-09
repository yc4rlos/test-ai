from typing import Any, Dict, Optional
from services.cepservice import CepService

cep_service = CepService()


def get_address_by_cep(cep: str) -> Optional[Dict[str, Any]]:
    """Consulta o endereco completo no Brasil a partir de um CEP.

    Args:
        cep: O CEP com ou sem formatacao (ex: '01001-000' ou '01001000').
    """
    try:
        return cep_service.get_address_by_cep(cep)
    except ValueError as error:
        return {"error": str(error)}
    except Exception as error:
        return {"error": f"Erro ao consultar CEP: {str(error)}"}