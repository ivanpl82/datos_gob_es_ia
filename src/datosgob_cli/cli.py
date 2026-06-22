"""Entry point CLI para datosgob-cli.

Agrupa todos los subcomandos bajo un @click.group().
Expone opciones globales:
  --format (json|csv)
  --pandas
  --page-size

Uso: datosgob [GLOBALES] <comando> [OPCIONES]
"""

from __future__ import annotations

import sys

import click

from datosgob_cli.client import APIClient
from datosgob_cli.commands.dataset import dataset_group
from datosgob_cli.commands.distribution import distribution_group
from datosgob_cli.commands.nti import nti_group
from datosgob_cli.commands.publisher import publisher_group
from datosgob_cli.commands.spatial import spatial_group
from datosgob_cli.commands.theme import theme_group


@click.group()
@click.option("--format", type=click.Choice(["json", "csv"]), default="json", help="Formato de salida")
@click.option("--pandas", is_flag=True, default=False, help="Salida como DataFrame pandas (JSON)")
@click.option("--page-size", default=10, type=click.IntRange(1, 50), help="Numero de items por pagina (max 50)")
@click.pass_context
def cli(ctx: click.Context, format: str, pandas: bool, page_size: int) -> None:
    """Herramienta CLI para consultar datos abiertos de datos.gob.es.

    Expone los verbos del catalogo de datos.gob.es como subcomandos.

    Ejemplos:

      datosgob dataset list --theme salud

      datosgob dataset list --theme salud --format csv

      datosgob publisher list --format json
    """
    ctx.ensure_object(dict)
    ctx.obj["format"] = format
    ctx.obj["pandas"] = pandas
    ctx.obj["page_size"] = page_size
    ctx.obj["client"] = APIClient(page_size=page_size)


# Registrar subcomandos
cli.add_command(dataset_group)
cli.add_command(distribution_group)
cli.add_command(publisher_group)
cli.add_command(theme_group)
cli.add_command(spatial_group)
cli.add_command(nti_group)


def main() -> None:
    """Entry point del script."""
    cli()  # pylint: disable=no-value-for-parameter


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(1)
