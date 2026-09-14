from __future__ import annotations

import io
from functools import lru_cache

import pandas as pd
import requests


# Official Open Data platform of Bogota.
BASE = "https://datosabiertos.bogota.gov.co"


def _read_csv(raw: bytes, encoding: str) -> pd.DataFrame:
    """Read a CSV and detect the delimiter."""

    # Bogota datasets commonly use semicolon as delimiter.
    try:
        df = pd.read_csv(
            io.BytesIO(raw),
            encoding=encoding,
            sep=";",
            low_memory=False,
        )

        # More than one column means the delimiter worked.
        if len(df.columns) > 1:
            return df

    except Exception:
        pass

    # Fallback: let pandas detect the delimiter.
    return pd.read_csv(
        io.BytesIO(raw),
        encoding=encoding,
        sep=None,
        engine="python",
        low_memory=False,
    )


@lru_cache(maxsize=8)
def load_dataset(resource_id: str) -> pd.DataFrame:
    """Download and temporarily cache a CKAN CSV resource."""

    # CKAN endpoint used to obtain resource metadata.
    api = f"{BASE}/api/3/action/resource_show"

    response = requests.get(
        api,
        params={"id": resource_id},
        timeout=45,
    )
    response.raise_for_status()

    payload = response.json()

    if not payload.get("success"):
        raise RuntimeError(
            "CKAN did not return valid resource information."
        )

    # URL of the official data file.
    url = payload["result"]["url"]

    response = requests.get(
        url,
        timeout=90,
    )
    response.raise_for_status()

    raw = response.content

    # Try the most common encodings.
    last_error = None

    for encoding in ("utf-8-sig", "latin-1"):
        try:
            return _read_csv(raw, encoding)

        except Exception as exc:
            last_error = exc

    raise RuntimeError(
        f"Could not interpret the CSV: {last_error}"
    )