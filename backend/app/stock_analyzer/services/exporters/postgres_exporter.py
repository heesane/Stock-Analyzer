from __future__ import annotations

import psycopg

from .base import Exporter, flatten_summary


class PostgresExporter(Exporter):
    def __init__(
        self,
        *,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
        table: str,
        schema: str | None = None,
        create_table: bool = True,
    ) -> None:
        self.conn_kwargs = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "dbname": database,
        }
        self.table = table
        self.schema = schema
        self.create_table = create_table

    def export(self, summary: dict) -> None:
        data = flatten_summary(summary)
        with psycopg.connect(**self.conn_kwargs) as conn:
            with conn.cursor() as cur:
                if self.create_table:
                    self._ensure_table(cur)
                table_ref = self._table_reference()
                columns = ", ".join(f'"{col}"' for col in data.keys())
                placeholders = ", ".join(["%s"] * len(data))
                query = f'INSERT INTO {table_ref} ({columns}) VALUES ({placeholders})'
                cur.execute(query, list(data.values()))
            conn.commit()

    def _table_reference(self) -> str:
        if self.schema:
            return f'"{self.schema}"."{self.table}"'
        return f'"{self.table}"'

    def _ensure_table(self, cursor) -> None:
        table_ref = self._table_reference()
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {table_ref} (
                id SERIAL PRIMARY KEY,
                ticker VARCHAR(32) NOT NULL,
                latest_date DATE NOT NULL,
                latest_close DOUBLE PRECISION,
                macd DOUBLE PRECISION,
                macd_signal DOUBLE PRECISION,
                macd_hist DOUBLE PRECISION,
                rsi DOUBLE PRECISION,
                decision_action VARCHAR(32),
                decision_rationale TEXT,
                sma20 DOUBLE PRECISION,
                sma50 DOUBLE PRECISION,
                volume_latest DOUBLE PRECISION,
                volume_avg20 DOUBLE PRECISION,
                support_price DOUBLE PRECISION,
                support_date DATE,
                resistance_price DOUBLE PRECISION,
                resistance_date DATE,
                channels_json JSONB,
                support_resistance_json JSONB,
                prob_bullish DOUBLE PRECISION,
                prob_bearish DOUBLE PRECISION,
                prob_confidence VARCHAR(32),
                prob_breakdown_json JSONB,
                score_total DOUBLE PRECISION,
                score_rating VARCHAR(32),
                score_indicators_json JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
