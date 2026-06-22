"""Comando dataset: consulta datasets de datos.gob.es.

Uso: datosgob dataset list [OPCIONES]
     datosgob dataset get <identifier>

Filtros disponibles en list:
  --theme, --publisher, --keyword, --spatial,
  --resource-format, --modified-begin, --modified-end,
  --issued-begin, --issued-end
"""

from __future__ import annotations

import click

from datosgob_cli.client import APIClient
from datosgob_cli.formatters import format_csv, format_json, format_pandas


@click.group(name="dataset")
def dataset_group() -> None:
    """Comandos para consultar datasets."""


@dataset_group.command(name="list")
@click.option("--theme", default=None, help="Filtrar por tema (URI o etiqueta)")
@click.option("--publisher", default=None, help="Filtrar por publicador")
@click.option("--keyword", default=None, help="Filtrar por palabra clave")
@click.option("--spatial", default=None, help="Filtrar por cobertura geografica")
@click.option(
    "--resource-format",
    default=None,
    help="Filtrar por formato del recurso (ej. text/csv)",
)
@click.option(
    "--modified-begin",
    default=None,
    help="Fecha inicio de modificacion (AAAA-MM-DD)",
)
@click.option(
    "--modified-end",
    default=None,
    help="Fecha fin de modificacion (AAAA-MM-DD)",
)
@click.option(
    "--issued-begin",
    default=None,
    help="Fecha inicio de publicacion (AAAA-MM-DD)",
)
@click.option(
    "--issued-end",
    default=None,
    help="Fecha fin de publicacion (AAAA-MM-DD)",
)
@click.pass_context
def dataset_list(
    ctx: click.Context,
    theme: str | None,
    publisher: str | None,
    keyword: str | None,
    spatial: str | None,
    resource_format: str | None,
    modified_begin: str | None,
    modified_end: str | None,
    issued_begin: str | None,
    issued_end: str | None,
) -> None:
    """Lista datasets de datos.gob.es con los filtros indicados."""
    client: APIClient = ctx.obj["client"]
    output_format: str = ctx.obj.get("format", "json")
    use_pandas: bool = ctx.obj.get("pandas", False)

    params: dict[str, str] = {}
    if theme:
        params["theme"] = theme
    if publisher:
        params["publisher"] = publisher
    if keyword:
        params["keyword"] = keyword
    if spatial:
        params["spatial"] = spatial
    if resource_format:
        params["format"] = resource_format
    if modified_begin:
        params["modified"] = f">={modified_begin}"
    if modified_end:
        modified_end_val = params.get("modified", "")
        params["modified"] = (
            f"{modified_end_val},{modified_end}" if modified_end_val else f"<={modified_end}"
        )
    if issued_begin:
        params["issued"] = f">={issued_begin}"
    if issued_end:
        issued_end_val = params.get("issued", "")
        params["issued"] = (
            f"{issued_end_val},{issued_end}" if issued_end_val else f"<={issued_end}"
        )

    try:
        all_items: list[dict] = []
        for page in client.paginate("catalog/dataset.json", params):
            all_items.extend(page)
    except Exception as exc:
        click.echo(f"Error al consultar datasets: {exc}", err=True)
        raise click.Abort() from exc

    _emit_output(all_items, output_format, use_pandas)


def _emit_output(
    items: list[dict], output_format: str, use_pandas: bool
) -> None:
    """Envia los items formateados a stdout."""
    if not items:
        click.echo("[]" if output_format == "json" else "")
        return

    if use_pandas:
        click.echo(format_pandas(items))
    elif output_format == "csv":
        click.echo(format_csv(items))
    else:
        click.echo(format_json(items))


@dataset_group.command(name="get")
@click.argument("identifier")
@click.pass_context
def dataset_get(ctx: click.Context, identifier: str) -> None:
    """Obtiene un dataset individual por su identifier (UUID).

    El identifier aparece en los campos ``identifier`` o ``_about``
    de la respuesta de ``dataset list``.

    Ejemplo:

      datosgob dataset get b0da07b8-a123-4abc-9def-0123456789ab
    """
    client: APIClient = ctx.obj["client"]

    try:
        response = client._fetch_page(
            f"catalog/dataset/{identifier}.json",
            {},
        )
        page_data = response.get("result", {})
        items = page_data.get("items", [])
        item = items[0] if items else {}
        click.echo(format_json(item))
    except Exception as exc:
        click.echo(f"Error al obtener dataset: {exc}", err=True)
        raise click.Abort() from exc
