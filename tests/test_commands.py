"""Tests de estructura de comandos para datosgob-cli.

Verifica que todos los modulos de comandos se importan
y que el CLI group registra cada subcomando.

Este test NO necesita pytest ni mock — solo imports sobre
el codigo real y verifica que el arbol de comandos existe.
"""

import sys
sys.path.insert(0, "src")

# Verificar imports de todos los modulos de comandos
from datosgob_cli.commands import dataset
from datosgob_cli.commands import distribution
from datosgob_cli.commands import publisher
from datosgob_cli.commands import theme
from datosgob_cli.commands import spatial
from datosgob_cli.commands import nti


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


if __name__ == "__main__":
    test_commands_importable()
    test_cli_group_has_commands()
    print("OK")