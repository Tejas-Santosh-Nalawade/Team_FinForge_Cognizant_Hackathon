import io
import json
from typing import Any, Dict, List, Tuple

import pandas as pd


def make_json_serializable(value: Any) -> Any:

    if value is None:
        return None

    if pd.isna(value):
        return None

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass

    if isinstance(value, dict):
        return {
            str(k): make_json_serializable(v) # pyright: ignore[reportUnknownArgumentType]
            for k, v in value.items()
        }

    if isinstance(value, list):
        return [
            make_json_serializable(v)
            for v in value
        ]

    return value


def dataframe_to_rows(
    dataframe: pd.DataFrame,
) -> List[Dict[str, Any]]:

    dataframe = dataframe.where(
        pd.notna(dataframe),
        None,
    )

    records = dataframe.to_dict(
        orient="records"
    )

    result = []

    for record in records:
        result.append(
            {
                str(key): make_json_serializable(value)
                for key, value in record.items()
            }
        )

    return result


def parse_excel(
    file_bytes: bytes,
) -> List[Tuple[str, List[Dict[str, Any]]]]:

    workbook = pd.read_excel(
        io.BytesIO(file_bytes),
        sheet_name=None,
    )

    parsed = []

    for sheet_name, dataframe in workbook.items():

        if dataframe.empty:
            continue

        rows = dataframe_to_rows(dataframe)

        if rows:
            parsed.append(
                (
                    str(sheet_name),
                    rows,
                )
            )

    return parsed


def parse_csv(
    file_bytes: bytes,
) -> List[Tuple[str, List[Dict[str, Any]]]]:

    dataframe = pd.read_csv(
        io.BytesIO(file_bytes)
    )

    if dataframe.empty:
        return []

    rows = dataframe_to_rows(dataframe)

    return [
        (
            "__default__",
            rows,
        )
    ]


def parse_json(
    file_bytes: bytes,
) -> List[Tuple[str, List[Dict[str, Any]]]]:

    payload = json.loads(
        file_bytes.decode("utf-8")
    )

    if isinstance(payload, list):

        rows = []

        for item in payload:

            if isinstance(item, dict):
                rows.append(
                    make_json_serializable(item)
                )
            else:
                rows.append(
                    {"value": make_json_serializable(item)}
                )

        return [
            (
                "__default__",
                rows,
            )
        ]

    if isinstance(payload, dict):

        return [
            (
                "__default__",
                [
                    make_json_serializable(payload)
                ],
            )
        ]

    return [
        (
            "__default__",
            [
                {
                    "value": make_json_serializable(payload)
                }
            ],
        )
    ]


def parse_file(
    filename: str,
    file_bytes: bytes,
) -> List[Tuple[str, List[Dict[str, Any]]]]:

    filename_lower = filename.lower()

    if filename_lower.endswith(".xlsx"):
        return parse_excel(file_bytes)

    if filename_lower.endswith(".xls"):
        return parse_excel(file_bytes)

    if filename_lower.endswith(".csv"):
        return parse_csv(file_bytes)

    if filename_lower.endswith(".json"):
        return parse_json(file_bytes)

    raise ValueError(
        "Unsupported file format"
    )