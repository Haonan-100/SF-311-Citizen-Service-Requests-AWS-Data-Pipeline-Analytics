import gzip
from pathlib import Path
import pyarrow.parquet as pq
import psycopg2

cwd = Path.cwd()
if "__file__" in globals():
    # Running as a script, __file__ exists
    BASE = Path(__file__).resolve().parent.parent
else:
    # Running in a notebook, __file__ does not exist
    # If there's a data/ folder in cwd, treat it as the project root; otherwise, move up one level
    if (cwd / "data").exists():
        BASE = cwd
    elif (cwd.parent / "data").exists():
        BASE = cwd.parent
    else:
        raise FileNotFoundError(f"Could not locate the data folder (cwd={cwd})")

DATA_DIR = BASE / "data"
PARQUET  = DATA_DIR / "sf311_snapshot.parquet"
CSV_TMP  = DATA_DIR / "sf311_tmp.csv.gz"

def parquet_to_csv_gz():
    print("Converting Parquet → gzip-compressed CSV …")
    # Arrow's zero-copy write_csv returns None, so convert to pandas first
    table = pq.read_table(PARQUET)
    df = table.to_pandas()
    with gzip.open(CSV_TMP, "wt", newline="", encoding="utf-8") as f:
        df.to_csv(f, index=False)
    size_mb = CSV_TMP.stat().st_size / 1e6
    print(f"CSV written: {CSV_TMP} ({size_mb:.1f} MB)")

def copy_into_pg():
    print("COPY into Postgres …")
    conn = psycopg2.connect(
        dbname="sf311", user="sf311",
        password="sf311", host="localhost", port=5433
    )
    cur = conn.cursor()
    cur.execute("SET client_encoding TO 'UTF8'")
    cur.execute("CREATE SCHEMA IF NOT EXISTS raw")
    cur.execute("DROP TABLE IF EXISTS raw.sf311")

    # Automatically create table based on CSV header (all columns as TEXT)
    with gzip.open(CSV_TMP, "rt", encoding="utf-8") as f:
        header = f.readline().strip()
    cols = ", ".join(f'"{c}" TEXT' for c in header.split(","))
    cur.execute(f"CREATE TABLE raw.sf311 ({cols});")
    conn.commit()

    # Perform the actual COPY operation
    with gzip.open(CSV_TMP, "rb") as f:
        cur.copy_expert(
            "COPY raw.sf311 FROM STDIN WITH (FORMAT CSV, HEADER, DELIMITER ',')",
            f
        )
    conn.commit()
    cur.close()
    conn.close()
    print("COPY finished!")

    if __name__ == "__main__":
        parquet_to_csv_gz()
        copy_into_pg()