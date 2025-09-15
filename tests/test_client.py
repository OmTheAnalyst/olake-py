import sys
import pytest
from pyspark.sql import SparkSession
from olake import cdc


@pytest.fixture(scope="session")
def spark():
    return (
        SparkSession.builder.master("local[2]")
        .appName("olake-tests")
        # Ensure Spark uses the venv Python
        .config("spark.executorEnv.PYTHON", sys.executable)
        .config("spark.pyspark.python", sys.executable)
        .getOrCreate()
    )


def test_apply_to_delta_inserts_and_updates(spark):
    # Bronze data with update for same id
    data = [
        {"id": 1, "value": "old", "ts": "2024-01-01"},
        {"id": 1, "value": "new", "ts": "2024-01-02"},
        {"id": 2, "value": "keep", "ts": "2024-01-02"},
    ]
    bronze_df = spark.createDataFrame(data)
    bronze_df.createOrReplaceTempView("bronze_orders")

    # Run CDC helper
    cdc.CDC.apply_to_delta(
        bronze_path="bronze_orders", silver_table="silver_orders", pk="id", ts_col="ts"
    )

    result = spark.sql("SELECT * FROM silver_orders").collect()
    assert len(result) == 2
    assert {r["value"] for r in result} == {"new", "keep"}
