"""Tests de estructura de comandos para datosgob-cli.

Verifica que todos los modulos de comandos se importan
y que el CLI group registra cada subcomando.
"""

import sys

sys.path.insert(0, "src")

# Verificar imports de todos los modulos de comandos
from datosgob_cli.commands import dataset, distribution, nti, publisher, spatial, theme


def test_commands_importable() -> None:
    """Todos los modulos de comandos se importan sin errores."""
    assert dataset is not None
    assert distribution is not None
    assert publisher is not None
    assert theme is not None
    assert spatial is not None
    assert nti is not None


def test_cli_group_has_commands() -> None:
    """El CLI group registra los subcomandos correctamente."""
    from datosgob_cli.cli import cli
    commands = {c.name for c in cli.commands.values()}
    expected = {"dataset", "distribution", "publisher", "theme", "spatial", "nti"}
    assert commands == expected, f"Comandos registrados: {commands}"


def test_dataset_has_list_and_get() -> None:
    """Dataset group tiene los subcomandos 'list' y 'get'."""
    from datosgob_cli.cli import cli
    dataset_cmd = cli.commands["dataset"]
    subcommands = {c.name for c in dataset_cmd.commands.values()}
    assert "list" in subcommands, f"Falta subcomando list: {subcommands}"
    assert "get" in subcommands, f"Falta subcomando get: {subcommands}"


def test_spatial_still_registered() -> None:
    """Spatial group se mantiene registrado aunque devuelva error."""
    from datosgob_cli.cli import cli
    assert "spatial" in cli.commands


if __name__ == "__main__":
    test_commands_importable()
    test_cli_group_has_commands()
    test_dataset_has_list_and_get()
    test_spatial_still_registered()
    print("OK")
