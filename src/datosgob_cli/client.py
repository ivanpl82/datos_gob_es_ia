"""Cliente HTTP para la API de datos.gob.es.

Capa de comunicacion con la API linked-data-api v0.2:
- requests.Session con timeout configurable
- paginacion automatica como generador (recorre next hasta que falte)
- manejo de errores: timeout, HTTP 4xx/5xx, conexion caida
"""

from __future__ import annotations

import time
from typing import Any, Generator

import requests


class APIClient:
    """Cliente sincrono para la API de datos.gob.es."""

    BASE_URL = "https://datos.gob.es/apidata"
    DEFAULT_TIMEOUT = 10
    DEFAULT_PAGE_SIZE = 10

    def __init__(
        self,
        base_url: str | None = None,
        timeout: int = DEFAULT_TIMEOUT,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> None:
        self.base_url = (base_url or self.BASE_URL).rstrip("/")
        self.timeout = timeout
        self.page_size = min(page_size, 50)
        self._session = requests.Session()

    def _fetch_page(self, endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
        """Realiza una peticion GET y devuelve el JSON respuesta.

        Lanza:
            requests.Timeout -- si el servidor no responde en ``timeout`` segundos.
            requests.HTTPError -- si la respuesta es 4xx/5xx.
            requests.ConnectionError -- si no se puede conectar al servidor.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            resp = self._session.get(url, params=params, timeout=self.timeout)
            resp.raise_for_status()
        except requests.Timeout:
            raise
        except requests.HTTPError:
            raise
        except requests.ConnectionError:
            raise
        try:
            return resp.json()
        except requests.exceptions.JSONDecodeError:
            raise

    def paginate(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> Generator[list[dict[str, Any]], None, None]:
        """Generador: recorre las paginas de la API hasta que falte ``next``.

        Cada yield produce una pagina completa (lista de items).
        Espera 0.5s entre peticiones para respetar rate-limiting.
        """
        params = dict(params or {})
        params.setdefault("_pageSize", str(self.page_size))

        page = 1
        while True:
            params["_page"] = str(page)
            data = self._fetch_page(endpoint, params)

            items = data.get("items", data.get("result", []))
            if items:
                yield items

            if "next" not in data:
                break

            time.sleep(0.5)
            page += 1
