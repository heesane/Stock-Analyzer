from __future__ import annotations

import mysql.connector

from .base import Exporter, flatten_summary


class MySQLExporter(Exporter):
    def __init__(
        self,
        *,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
        table: str,
        create_table: bool = True,
    ) -> None:
        self.config = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
        }
        self.table = table
        self.create_table = create_table

    def export(self, summary: dict) -> None:
        data = flatten_summary(summary)
        connection = mysql.connector.connect(**self.config)
        try:
            cursor = connection.cursor()
            if self.create_table:
                self._ensure_table(cursor)
            placeholders = ", ".join(["%s"] * len(data))
            columns = ", ".join(f"`{col}`" for col in data.keys())
            query = f"INSERT INTO `{self.table}` ({columns}) VALUES ({placeholders})"
            cursor.execute(query, list(data.values()))
            connection.commit()
        finally:
            connection.close()

    def _ensure_table(self, cursor) -> None:
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS `{self.table}` (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ticker VARCHAR(32) NOT NULL,
                latest_date DATE NOT NULL,
                latest_close DOUBLE,
                macd DOUBLE,
                macd_signal DOUBLE,
                macd_hist DOUBLE,
                rsi DOUBLE,
                decision_action VARCHAR(32),
                decision_rationale TEXT,
                sma20 DOUBLE,
                sma50 DOUBLE,
                volume_latest DOUBLE,
                volume_avg20 DOUBLE,
                support_price DOUBLE,
                support_date DATE,
                resistance_price DOUBLE,
                resistance_date DATE,
                channels_json JSON,
                support_resistance_json JSON,
                prob_bullish DOUBLE,
                prob_bearish DOUBLE,
                prob_confidence VARCHAR(32),
                prob_breakdown_json JSON,
                score_total DOUBLE,
                score_rating VARCHAR(32),
                score_indicators_json JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
