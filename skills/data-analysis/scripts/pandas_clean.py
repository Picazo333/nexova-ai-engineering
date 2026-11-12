"""
Safe snippet for basic pandas cleaning. Copy and adapt for your dataset.
Run: python pandas_clean.py  (ensure pandas is installed)
"""
import sys
from pathlib import Path


def main() -> int:
    path = Path("data.csv")
    if not path.is_file():
        print("error: falta data.csv o no se puede leer.", file=sys.stderr)
        return 1
    try:
        import pandas as pd
    except ImportError:
        print("error: pandas no está instalado.", file=sys.stderr)
        return 1
    try:
        df = pd.read_csv(path)
    except (OSError, UnicodeError, ValueError):
        print("error: data.csv no tiene un CSV legible.", file=sys.stderr)
        return 1

    print("df_shape", df.shape)
    print("df_dtypes", df.dtypes)

    df = df.dropna(axis=1, how="all")
    print("df_shape_after_drop_all_null_cols", df.shape)

    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    print("df_columns", list(df.columns))

    before = len(df)
    df = df.drop_duplicates()
    print("rows_dropped_duplicates", before - len(df))
    print("df_head", df.head())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
