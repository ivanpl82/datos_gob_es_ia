"""Comando spatial: consulta coberturas geograficas de datos.gob.es.

ATENCION: El endpoint ``/catalog/spatial`` devuelve error 500
(Internal Server Error). Este comando esta deshabilitado.

Uso: datosgob spatial list  (siempre muestra error)
"""

from __future__ import annotations

import click


@click.group(name="spatial")
def spatial_group() -> None:
    """Comandos para consultar coberturas geograficas."""


@spatial_group.command(name="list")
@click.pass_context
def spatial_list(ctx: click.Context) -> None:
    """Lista todas las coberturas geograficas.

    NO DISPONIBLE: el endpoint ``/catalog/spatial`` de datos.gob.es
    devuelve Internal Server Error (HTTP 500).
    """
    click.echo(
        "Error: El endpoint /catalog/spatial de datos.gob.es no esta disponible "
        "(devuelve HTTP 500 Internal Server Error).\n"
        "No es posible listar coberturas geograficas.",
        err=True,
    )
    raise click.Abort()
