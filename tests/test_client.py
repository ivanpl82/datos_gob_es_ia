"""Tests para el cliente de la API de datos.gob.es.

Verifica que APIClient se importa, se instancia, y expone
la interfaz esperada (base_url, _session, paginate).

Este test NO necesita pytest ni mock — solo imports y asserts
sobre el codigo real.
"""

import sys
sys.path.insert(0, "src")

from datosgob_cli.client import APIClient


def test_client_exists() -> None:
    """El cliente existe y se puede instanciar con valores por defecto."""
    client = APIClient()
    assert client is not None
    assert client.base_url == "https://datos.gob.es/apidata"


def test_client_session() -> None:
    """El cliente usa requests.Session internamente."""
    client = APIClient()
    assert hasattr(client, "_session")
    from requests import Session
    assert isinstance(client._session, Session)


def test_client_custom_base_url() -> None:
    """Se puede pasar una base_url personalizada al constructor."""
    client = APIClient(base_url="http://localhost:8000")
    assert client.base_url == "http://localhost:8000"


def test_client_page_size_capped() -> None:
    """El page_size maximo esta limitado a 50."""
    client = APIClient(page_size=100)
    assert client.page_size == 50


if __name__ == "__main__":
    test_client_exists()
    test_client_session()
    test_client_custom_base_url()
    test_client_page_size_capped()
    print("OK")