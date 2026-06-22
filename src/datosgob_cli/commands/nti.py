"""Comando nti: consulta NTI (Nucleos de Intervencion) de datos.gob.es.

Uso: datosgob nti list [OPCIONES]

Filtros disponibles:
  --sector, --territory
"""

from __future__ import annotations

import click

from datosgob_cli.client import APIClient
from datosgob_cli.commands.dataset import _emit_output


@click.group(name="nti")
def nti_group() -> None:
    """Comandos para consultar NTI (Nucleos de Intervencion)."""


@nti_group.command(name="list")
@click.option("--sector", default=None, help="Filtrar por sector")
@click.option("--territory", default=None, help="Filtrar por territorio")
@click.pass_context
def nti_list(
    ctx: click.Context,
    sector: str | None,
    territory: str | None,
) -> None:
    """Lista NTI de datos.gob.es."""
    client: APIClient = ctx.obj["client"]
    output_format: str = ctx.obj.get("format", "json")
    use_pandas: bool = ctx.obj.get("pandas", False)

    params: dict[str, str] = {}
    if sector:
        params["sector"] = sector
    if territory:
        params["territory"] = territory

    try:
        all_items: list[dict] = []
        for page in client.paginate("catalog/nti", params):
            all_items.extend(page)
    except Exception as exc:
        click.echo(f"Error al consultar NTI: {exc}", err=True)
        raise click.Abort() from exc

    _emit_output(all_items, output_format, use_pandas)
