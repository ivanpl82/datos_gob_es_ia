"""Formateadores de salida para datosgob-cli.

Soporta:
- JSON estructurado
- CSV plano con cabeceras
- DataFrame pandas serializado a JSON (con flag --pandas)
"""

from __future__ import annotations

import csv
import io
import json
from typing import Any


def format_json(items: list[dict[str, Any]]) -> str:
    """Serializa los items como JSON indentado."""
    return json.dumps(items, indent=2, ensure_ascii=False, default=str)


def format_csv(items: list[dict[str, Any]]) -> str:
    """Serializa los items como CSV con cabeceras.

    Las cabeceras se extraen de la primera fila.
    """
    if not items:
        return ""

    fieldnames = _collect_fieldnames(items)
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(items)
    return buf.getvalue()


def format_pandas(items: list[dict[str, Any]]) -> str:
    """Convierte items a DataFrame pandas y lo serializa como JSON.

    Solo se usa cuando --pandas esta activo.
    """
    import pandas as pd

    df = pd.DataFrame(items)
    return df.to_json(orient="records", force_ascii=False, date_format="iso")


def _collect_fieldnames(items: list[dict[str, Any]]) -> list[str]:
    """Recolecta todos los nombres de campo unicos en orden de aparicion."""
    seen: set[str] = set()
    fieldnames: list[str] = []
    for item in items:
        for key in item:
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)
    return fieldnames
