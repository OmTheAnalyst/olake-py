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
    # Bronze data with update for same id (basic case)
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


def test_cdc_raises_on_missing_bronze_view(spark):
    # Try to run CDC on a view that does not exist
    with pytest.raises(Exception):
        cdc.CDC.apply_to_delta(
            bronze_path="non_existent_view",
            silver_table="silver_fail",
            pk="id",
            ts_col="ts",
        )


def test_apply_to_delta_with_late_arrival_and_delete(spark):
    # Bronze data simulating late arrival + tombstone delete
    data = [
        {"id": 1, "value": "v1", "ts": "2024-01-01"},  # insert
        {"id": 1, "value": "v2", "ts": "2024-01-03"},  # update
        {"id": 2, "value": "a1", "ts": "2024-01-02"},  # insert
        {"id": 2, "value": "a2", "ts": "2024-01-01"},  # late arrival (older)
        {"id": 3, "value": "x1", "ts": "2024-01-05"},  # insert
        {"id": 3, "value": None, "ts": "2024-01-06"},  # tombstone (delete)
    ]
    bronze_df = spark.createDataFrame(data)
    bronze_df.createOrReplaceTempView("bronze_extended")

    # Run CDC helper
    cdc.CDC.apply_to_delta(
        bronze_path="bronze_extended",
        silver_table="silver_extended",
        pk="id",
        ts_col="ts",
    )

    result = spark.sql(
        "SELECT id, value, ts FROM silver_extended ORDER BY id"
    ).collect()
    result_dict = {r["id"]: (r["value"], r["ts"]) for r in result}

    expected = {
        1: ("v2", "2024-01-03"),  # latest update
        2: ("a1", "2024-01-02"),  # latest wins, despite late arrival
        3: (None, "2024-01-06"),  # tombstone (delete)
    }
    assert result_dict == expected
