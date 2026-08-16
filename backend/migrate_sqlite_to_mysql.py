import sqlite3
from pathlib import Path

from sqlalchemy.dialects import mysql
from sqlalchemy.schema import CreateIndex, CreateTable

from app.models.database import Base


SOURCE_SQLITE = Path(__file__).resolve().parent.parent / "database" / "law_game.db"
OUTPUT_SQL = Path(__file__).resolve().parent / "mysql_migration.sql"

TABLE_ORDER = [
    "events",
    "agents",
    "laws",
    "plans",
    "simulations",
    "simulation_rounds",
]


def sql_value(value):
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value).replace("\\", "\\\\").replace("'", "''")
    return f"'{text}'"


def build_create_table_sql():
    dialect = mysql.dialect()
    statements = []
    for table_name in TABLE_ORDER:
        table = Base.metadata.tables[table_name]
        ddl = str(CreateTable(table).compile(dialect=dialect)).rstrip()
        statements.append(f"DROP TABLE IF EXISTS `{table_name}`;")
        statements.append(f"{ddl};")
        for index in sorted(table.indexes, key=lambda item: item.name or ""):
            statements.append(f"{str(CreateIndex(index).compile(dialect=dialect)).rstrip()};")
    return statements


def build_insert_sql():
    conn = sqlite3.connect(str(SOURCE_SQLITE))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    statements = []

    for table_name in TABLE_ORDER:
        cur.execute(f'SELECT * FROM "{table_name}"')
        rows = cur.fetchall()
        if not rows:
            continue
        columns = [f"`{col}`" for col in rows[0].keys()]
        prefix = f"INSERT INTO `{table_name}` ({', '.join(columns)}) VALUES"
        values_sql = []
        for row in rows:
            values = ", ".join(sql_value(row[col]) for col in row.keys())
            values_sql.append(f"({values})")
        statements.append(prefix)
        statements.append(",\n".join(values_sql) + ";")

    conn.close()
    return statements


def main():
    if not SOURCE_SQLITE.exists():
        raise FileNotFoundError(f"SQLite database not found: {SOURCE_SQLITE}")

    sql_parts = [
        "SET NAMES utf8mb4;",
        "SET FOREIGN_KEY_CHECKS = 0;",
        "",
    ]
    sql_parts.extend(build_create_table_sql())
    sql_parts.append("")
    sql_parts.extend(build_insert_sql())
    sql_parts.append("")
    sql_parts.append("SET FOREIGN_KEY_CHECKS = 1;")

    OUTPUT_SQL.write_text("\n".join(sql_parts), encoding="utf-8")
    print(f"Generated migration SQL: {OUTPUT_SQL}")


if __name__ == "__main__":
    main()
