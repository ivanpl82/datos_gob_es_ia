"""Comando publisher: consulta publicadores de datos.gob.es.

Uso: datosgob publisher list
     datosgob publisher get <id>
"""

from __future__ import annotations

import click

from datosgob_cli.client import APIClient
from datosgob_cli.commands.dataset import _emit_output
from datosgob_cli.formatters import format_json


@click.group(name="publisher")
def publisher_group() -> None:
    """Comandos para consultar publicadores."""


@publisher_group.command(name="list")
@click.pass_context
def publisher_list(ctx: click.Context) -> None:
    """Lista todos los publicadores."""
    client: APIClient = ctx.obj["client"]
    output_format: str = ctx.obj.get("format", "json")
    use_pandas: bool = ctx.obj.get("pandas", False)

    try:
        all_items: list[dict] = []
        for page in client.paginate("catalog/publisher"):
            all_items.extend(page)
    except Exception as exc:
        click.echo(f"Error al consultar publicadores: {exc}", err=True)
        raise click.Abort() from exc

    _emit_output(all_items, output_format, use_pandas)


@publisher_group.command(name="get")
@click.argument("publisher_id")
@click.pass_context
def publisher_get(ctx: click.Context, publisher_id: str) -> None:
    """Obtiene un publicador por su ID.

    Realiza una unica peticion ``_fetch_page`` y extrae el
    primer item de ``result["items"]``. No itera paginacion
    porque busca un solo resultado.

    Si ``result`` no tiene ``items`` o esta vacio, devuelve ``{}``.
    """
    client: APIClient = ctx.obj["client"]

    try:
        response = client._fetch_page(
            f"catalog/publisher/{publisher_id.lstrip('/')}",
            {},
        )
        page_data = response.get("result", {})
        items = page_data.get("items", [])
        item = items[0] if items else {}
        click.echo(format_json(item))
    except Exception as exc:
        click.echo(f"Error al obtener publicador: {exc}", err=True)
        raise click.Abort() from exc
