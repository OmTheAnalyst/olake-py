from pyspark.sql import SparkSession, functions as F, Window


class CDC:
    @staticmethod
    def apply_to_delta(
        bronze_path: str, silver_table: str, pk: str, ts_col: str
    ) -> None:
        spark = SparkSession.getActiveSession()
        if spark is None:
            raise RuntimeError("No active Spark session found.")

        # Try to read as Parquet, else assume it's a temp view
        try:
            bronze_df = spark.read.parquet(bronze_path)
        except Exception:
            bronze_df = spark.table(bronze_path)

        # Keep only latest row per pk
        windowed = (
            bronze_df.withColumn(
                "rn",
                F.row_number().over(
                    Window.partitionBy(pk).orderBy(F.col(ts_col).desc())
                ),
            )
            .filter(F.col("rn") == 1)
            .drop("rn")
        )

        # Register as Silver table (temp view)
        windowed.createOrReplaceTempView(silver_table)
