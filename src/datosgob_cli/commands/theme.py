"""Comando theme: consulta temas de datos.gob.es.

Uso: datosgob theme list
"""

from __future__ import annotations

import click

from datosgob_cli.client import APIClient
from datosgob_cli.commands.dataset import _emit_output


@click.group(name="theme")
def theme_group() -> None:
    """Comandos para consultar temas."""


@theme_group.command(name="list")
@click.pass_context
def theme_list(ctx: click.Context) -> None:
    """Lista todos los temas disponibles."""
    client: APIClient = ctx.obj["client"]
    output_format: str = ctx.obj.get("format", "json")
    use_pandas: bool = ctx.obj.get("pandas", False)

    try:
        all_items: list[dict] = []
        for page in client.paginate("catalog/theme"):
            all_items.extend(page)
    except Exception as exc:
        click.echo(f"Error al consultar temas: {exc}", err=True)
        raise click.Abort() from exc

    _emit_output(all_items, output_format, use_pandas)
