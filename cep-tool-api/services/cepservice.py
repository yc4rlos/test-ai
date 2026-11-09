import httpx
from typing import Any, Dict, Optional
import re


class CepService:
    BASE_URL = "https://viacep.com.br/ws"

    @classmethod
    def clean_cep(cls, cep: str) -> str:
        """Remove caracteres nao numericos do CEP."""
        return re.sub(r"\D", "", cep or "")

    def get_address_by_cep(self, cep: str) -> Optional[Dict[str, Any]]:
        """Consulta um CEP de oito digitos no ViaCEP; retorna None se inexistente."""
        cleaned_cep = self.clean_cep(cep)
        if len(cleaned_cep) != 8:
            raise ValueError(f"CEP inválido: '{cep}'. Deve conter exatamente 8 dígitos.")

        url = f"{self.BASE_URL}/{cleaned_cep}/json/"
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()

        data: Dict[str, Any] = response.json()
        if data.get("erro") in (True, "true"):
            return None

        return data