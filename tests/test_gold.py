import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark():
    return (
        SparkSession.builder.master("local[2]")
        .appName("olake-gold-tests")
        .getOrCreate()
    )


def test_gold_summary_counts(spark):
    # Silver sample (already deduped by CDC)
    data = [
        {"id": 1, "value": "new", "ts": "2024-01-02"},
        {"id": 2, "value": "keep", "ts": "2024-01-02"},
        {"id": 3, "value": "new", "ts": "2024-01-03"},
    ]
    silver_df = spark.createDataFrame(data)
    silver_df.createOrReplaceTempView("silver_orders")

    # Gold = counts per value
    gold_df = silver_df.groupBy("value").count()

    result = {row["value"]: row["count"] for row in gold_df.collect()}

    assert result == {
        "new": 2,
        "keep": 1,
    }
