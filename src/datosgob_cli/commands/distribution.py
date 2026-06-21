"""Comando distribution: consulta distribuciones de datos.gob.es.

Uso: datosgob distribution list [OPCIONES]

Filtros disponibles:
  --by-dataset, --by-format
"""

from __future__ import annotations

import click

from datosgob_cli.client import APIClient
from datosgob_cli.commands.dataset import _emit_output


@click.group(name="distribution")
def distribution_group() -> None:
    """Comandos para consultar distribuciones."""


@distribution_group.command(name="list")
@click.option("--by-dataset", default=None, help="URI del dataset para filtrar distribuciones")
@click.option("--by-format", default=None, help="Filtrar por formato (ej. text/csv)")
@click.pass_context
def distribution_list(
    ctx: click.Context,
    by_dataset: str | None,
    by_format: str | None,
) -> None:
    """Lista distribuciones de datos.gob.es."""
    client: APIClient = ctx.obj["client"]
    output_format: str = ctx.obj.get("format", "json")
    use_pandas: bool = ctx.obj.get("pandas", False)

    params: dict[str, str] = {}
    if by_dataset:
        params["dataset"] = by_dataset
    if by_format:
        params["format"] = by_format

    try:
        all_items: list[dict] = []
        for page in client.paginate("catalog/distribution", params):
            all_items.extend(page)
    except Exception as exc:
        click.echo(f"Error al consultar distribuciones: {exc}", err=True)
        raise click.Abort() from exc

    _emit_output(all_items, output_format, use_pandas)