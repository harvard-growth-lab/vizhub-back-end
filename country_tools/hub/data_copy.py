import io
import pandas as pd
from sqlalchemy import text
from country_tools.country_tools_api.database.base import engine, Base
from country_tools.country_tools_api.database.hub import HubProjects  # noqa: F401

HUB_SCHEMA = "hub"
HUB_PROCESSED_DATA_DIR = "./hub/processed_data"
HUB_TABLES = ["projects"]


def copy_df(conn, df, schema, table):
    buf = io.StringIO()
    df.to_csv(buf, index=False, header=False, na_rep="\\N")
    buf.seek(0)
    cols = ", ".join(f'"{col}"' for col in df.columns)
    sql = (
        f'COPY {schema}."{table}" ({cols}) '
        f"FROM STDIN WITH (FORMAT csv, NULL '\\N')"
    )
    with conn.connection.cursor() as cur:   # raw psycopg2 cursor
        cur.copy_expert(sql, buf)


if __name__ == "__main__":
    with engine.begin() as c:
        c.execute(text(f"CREATE SCHEMA IF NOT EXISTS {HUB_SCHEMA}"))

    Base.metadata.create_all(bind=engine)

    with engine.begin() as c:
        for table in HUB_TABLES:
            df = pd.read_csv(f"{HUB_PROCESSED_DATA_DIR}/{table}.csv")
            c.execute(text(f'TRUNCATE TABLE {HUB_SCHEMA}."{table}" CASCADE'))
            copy_df(c, df, HUB_SCHEMA, table)