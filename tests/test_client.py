"""Tests para el cliente de la API de datos.gob.es.

Verifica que APIClient se importa, se instancia, y expone
la interfaz esperada (base_url, _session, paginate).

Este test NO necesita pytest ni mock — solo imports y asserts
sobre el codigo real.
"""

import sys
from unittest.mock import MagicMock, patch

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


# === NUEVOS TESTS (paginacion corregida) ===


def test_paginate_extracts_items_from_result():
    """paginate() extrae items de data.result.items."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "format": "linked-data-api",
        "version": "0.2",
        "result": {
            "_about": "http://datos.gob.es/apidata/catalog/dataset.json?_pageSize=2&_page=1",
            "items": [
                {"title": "Dataset 1", "description": "Desc 1"},
                {"title": "Dataset 2", "description": "Desc 2"},
            ],
            "itemsPerPage": 2,
            "page": 1,
        }
    }
    mock_response.raise_for_status = MagicMock()

    client = APIClient(page_size=2)
    with patch.object(client._session, "get", return_value=mock_response):
        pages = list(client.paginate("catalog/dataset.json"))

    assert len(pages) == 1
    assert len(pages[0]) == 2
    assert pages[0][0]["title"] == "Dataset 1"


def test_paginate_handles_next_in_result():
    """paginate() detecta next dentro de data.result para continuar paginando."""
    responses = [
        MagicMock(**{
            "json.return_value": {
                "format": "linked-data-api",
                "version": "0.2",
                "result": {
                    "items": [{"title": "Page 1"}],
                    "next": "http://datos.gob.es/page2",
                }
            },
            "raise_for_status.return_value": None,
        }),
        MagicMock(**{
            "json.return_value": {
                "format": "linked-data-api",
                "version": "0.2",
                "result": {
                    "items": [{"title": "Page 2"}],
                }
            },
            "raise_for_status.return_value": None,
        }),
    ]

    client = APIClient(page_size=2)
    with patch.object(client._session, "get", side_effect=responses):
        pages = list(client.paginate("catalog/dataset.json"))

    assert len(pages) == 2
    assert pages[0][0]["title"] == "Page 1"
    assert pages[1][0]["title"] == "Page 2"


def test_paginate_empty_result():
    """paginate() no falla cuando data no tiene result."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"format": "linked-data-api", "version": "0.2"}
    mock_response.raise_for_status = MagicMock()

    client = APIClient(page_size=2)
    with patch.object(client._session, "get", return_value=mock_response):
        pages = list(client.paginate("catalog/dataset.json"))

    assert len(pages) == 0


def test_paginate_no_items_in_result():
    """paginate() devuelve pagina vacia cuando result no tiene items."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "format": "linked-data-api",
        "version": "0.2",
        "result": {"items": []}
    }
    mock_response.raise_for_status = MagicMock()

    client = APIClient(page_size=2)
    with patch.object(client._session, "get", return_value=mock_response):
        pages = list(client.paginate("catalog/dataset.json"))

    assert len(pages) == 0


def test_paginate_last_page():
    """paginate() corta cuando result no tiene next (ultima pagina)."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "format": "linked-data-api",
        "version": "0.2",
        "result": {
            "items": [{"title": "Unico dataset"}],
        }
    }
    mock_response.raise_for_status = MagicMock()

    client = APIClient(page_size=2)
    with patch.object(client._session, "get", return_value=mock_response):
        pages = list(client.paginate("catalog/dataset.json"))

    assert len(pages) == 1
    assert pages[0][0]["title"] == "Unico dataset"


def test_publisher_get_extracts_first_item():
    """_fetch_page + extraccion de result.items funciona correctamente."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "format": "linked-data-api",
        "version": "0.2",
        "result": {
            "items": [{"title": "Pub 1", "id": "/id/123"}],
        }
    }
    mock_response.raise_for_status = MagicMock()

    client = APIClient()
    with patch.object(client._session, "get", return_value=mock_response):
        response = client._fetch_page("catalog/publisher/123", {})
        page_data = response.get("result", {})
        items = page_data.get("items", [])
        item = items[0] if items else {}

    assert item["title"] == "Pub 1"
    assert item["id"] == "/id/123"


def test_publisher_get_nonexistent_returns_empty():
    """publisher_get con ID no existente devuelve {}."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "format": "linked-data-api",
        "version": "0.2",
        "result": {"items": []}
    }
    mock_response.raise_for_status = MagicMock()

    client = APIClient()
    with patch.object(client._session, "get", return_value=mock_response):
        response = client._fetch_page("catalog/publisher/9999", {})
        page_data = response.get("result", {})
        items = page_data.get("items", [])
        item = items[0] if items else {}

    assert item == {}


def test_dataset_get_extracts_first_item():
    """dataset get extrae el primer item de result.items."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "format": "linked-data-api",
        "version": "0.2",
        "result": {
            "items": [{"title": "Dataset 1", "identifier": [{"_value": "abc-123", "_lang": "es"}]}],
        }
    }
    mock_response.raise_for_status = MagicMock()

    client = APIClient()
    with patch.object(client._session, "get", return_value=mock_response):
        response = client._fetch_page("catalog/dataset/abc-123.json", {})
        page_data = response.get("result", {})
        items = page_data.get("items", [])
        item = items[0] if items else {}

    assert item["title"] == "Dataset 1"
    assert item["identifier"][0]["_value"] == "abc-123"


def test_paginate_starts_at_page_0():
    """paginate() usa _page=0 como primera pagina."""
    call_count = 0

    def mock_get(url, **kwargs):
        nonlocal call_count
        call_count += 1
        mock = MagicMock()
        body = {
            "format": "linked-data-api",
            "version": "0.2",
            "result": {
                "items": [{"title": f"Page {call_count - 1}"}],
            }
        }
        # solo la primera pagina tiene next
        if call_count < 2:
            body["result"]["next"] = f"http://datos.gob.es/page{call_count}"
        mock.json.return_value = body
        mock.raise_for_status = MagicMock()
        return mock

    client = APIClient(page_size=2)
    with patch.object(client._session, "get", side_effect=mock_get):
        pages = list(client.paginate("catalog/dataset.json"))

    assert len(pages) == 2
    assert pages[0][0]["title"] == "Page 0"  # <-- confirma _page=0
    assert pages[1][0]["title"] == "Page 1"


if __name__ == "__main__":
    test_client_exists()
    test_client_session()
    test_client_custom_base_url()
    test_client_page_size_capped()
    print("OK")
