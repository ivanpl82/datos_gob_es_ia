"""Comando spatial: consulta coberturas geograficas de datos.gob.es.

Uso: datosgob spatial list
"""

from __future__ import annotations

import click

from datosgob_cli.client import APIClient
from datosgob_cli.commands.dataset import _emit_output


@click.group(name="spatial")
def spatial_group() -> None:
    """Comandos para consultar coberturas geograficas."""


@spatial_group.command(name="list")
@click.pass_context
def spatial_list(ctx: click.Context) -> None:
    """Lista todas las coberturas geograficas."""
    client: APIClient = ctx.obj["client"]
    output_format: str = ctx.obj.get("format", "json")
    use_pandas: bool = ctx.obj.get("pandas", False)

    try:
        all_items: list[dict] = []
        for page in client.paginate("catalog/spatial"):
            all_items.extend(page)
    except Exception as exc:
        click.echo(f"Error al consultar coberturas: {exc}", err=True)
        raise click.Abort() from exc

    _emit_output(all_items, output_format, use_pandas)