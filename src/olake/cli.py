import os
import typer
import databricks.sql
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from .__version__ import __version__
from . import cdc

load_dotenv()  # load .env

app = typer.Typer(help="OLake CLI")


# 🔑 Spark bootstrap helper
def get_spark() -> SparkSession:
    spark = SparkSession.getActiveSession()
    if spark is None:
        spark = (
            SparkSession.builder.appName("olake-cli")
            .master("local[2]")
            # keep local FS; avoids some Hadoop checks (still
            # required for file writes)
            .config("spark.hadoop.fs.file.impl.disable.cache", "true")
            .config(
                "spark.hadoop.fs.file.impl",
                "org.apache.hadoop.fs.LocalFileSystem",
            )
            .config(
                "spark.hadoop.fs.AbstractFileSystem.file.impl",
                "org.apache.hadoop.fs.local.LocalFs",
            )
            .getOrCreate()
        )
    return spark


@app.command("version")
def show_version():
    typer.echo(f"olake version: {__version__}")


@app.command("hello")
def hello():
    typer.echo("hello from olake")


@app.command("demo")
def demo():
    """
    Run the full Bronze → Silver → Gold demo in one
    Spark session (view mode).
    """
    spark = get_spark()

    # Step 1: Bronze temp view
    data = [
        {"id": 1, "value": "old", "ts": "2024-01-01"},
        {"id": 1, "value": "new", "ts": "2024-01-02"},
        {"id": 2, "value": "keep", "ts": "2024-01-02"},
    ]
    df = spark.createDataFrame(data)
    df.createOrReplaceTempView("bronze_orders")
    typer.echo("✅ Bronze temp view 'bronze_orders' created")

    # Step 2: Silver via CDC
    cdc.CDC.apply_to_delta(
        bronze_path="bronze_orders",
        silver_table="silver_orders",
        pk="id",
        ts_col="ts",
    )
    typer.echo("✅ CDC applied → Silver temp view 'silver_orders'")

    # Step 3: Gold summary (counts per value)
    silver_df = spark.sql("SELECT * FROM silver_orders")
    gold_df = silver_df.groupBy("value").count()
    gold_df.createOrReplaceTempView("gold_summary")
    typer.echo("✅ Gold summary created → temp view 'gold_summary'")

    # Show results
    print("\n--- Bronze ---")
    spark.sql(
        "SELECT * FROM bronze_orders ORDER BY id, ts"
    ).show(truncate=False)

    print("\n--- Silver ---")
    silver_df.show(truncate=False)

    print("\n--- Gold ---")
    gold_df.show(truncate=False)


@app.command("connect")
def connect():
    host = os.getenv("DATABRICKS_HOST")
    token = os.getenv("DATABRICKS_TOKEN")
    http_path = os.getenv("DATABRICKS_SQL_PATH")

    if not host or not token or not http_path:
        missing = [
            n
            for n, v in [
                ("DATABRICKS_HOST", host),
                ("DATABRICKS_TOKEN", token),
                ("DATABRICKS_SQL_PATH", http_path),
            ]
            if not v
        ]
        typer.echo(
            "❌ Connection failed: missing env var(s): "
            f"{', '.join(missing)}"
        )
        return

    try:
        with databricks.sql.connect(
            server_hostname=host.replace("https://", ""),
            access_token=token,
            http_path=http_path,
        ) as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1")
        typer.echo("✅ Connection successful!")
    except Exception as e:
        typer.echo(f"❌ Connection failed: {e}")


@app.command("cdc")
def run_cdc(
    bronze_path: str = typer.Option(
        ...,
        help=(
            "Path to Bronze Parquet/Delta OR a temp view "
            "name (e.g. 'bronze_orders')."
        ),
    ),
    silver_table: str = typer.Option(
        ...,
        help="Target Silver table name (temp view or file path).",
    ),
    pk: str = typer.Option("id", help="Primary key column."),
    ts_col: str = typer.Option("ts", help="Timestamp column."),
    mode: str = typer.Option(
        "view",
        help=(
            "Output mode: 'view' (default, creates a temp view) "
            "or 'file' (writes Parquet)."
        ),
    ),
):
    """
    Run CDC logic: take Bronze data (from Parquet path or
    Spark temp view), deduplicate to latest per PK/ts,
    and publish a Silver table either as a temp view
    (default) or as a Parquet file.
    """
    try:
        df = cdc.CDC.apply_to_delta(
            bronze_path=bronze_path,
            silver_table=silver_table,
            pk=pk,
            ts_col=ts_col,
        )

        if mode == "view":
            df.createOrReplaceTempView(silver_table)
            typer.echo(f"✅ CDC applied. Silver temp view: {silver_table}")
        elif mode == "file":
            df.write.mode("overwrite").parquet(silver_table)
            typer.echo(
                f"✅ CDC applied. Silver dataset written to: {silver_table}"
            )
        else:
            typer.echo("❌ Invalid mode. Use 'view' or 'file'.")
    except Exception as e:
        typer.echo(f"❌ CDC failed: {e}")


@app.command("gen-sample")
def gen_sample(
    bronze_path: str = typer.Option(
        "view:bronze_orders",
        help=(
            "Where to put the sample Bronze data. "
            "Use 'view:<name>' to create an in-memory temp view "
            "(recommended on Windows), or provide a filesystem "
            "path (e.g. ./data/bronze) to write Parquet."
        ),
    )
):
    """
    Generate a small sample Bronze dataset for CDC testing.
    - On Windows, prefer 'view:<name>' to avoid Hadoop/winutils.
    """
    spark = get_spark()

    data = [
        {"id": 1, "value": "old", "ts": "2024-01-01"},
        {"id": 1, "value": "new", "ts": "2024-01-02"},
        {"id": 2, "value": "keep", "ts": "2024-01-02"},
    ]
    df = spark.createDataFrame(data)

    if bronze_path.lower().startswith("view:"):
        view_name = bronze_path.split("view:", 1)[1].strip() or "bronze_orders"
        df.createOrReplaceTempView(view_name)
        typer.echo(
            f"✅ Sample Bronze temp view '{view_name}' created (in memory)."
        )
        return

    try:
        df.write.mode("overwrite").parquet(bronze_path)
        typer.echo(f"✅ Sample Bronze dataset written to {bronze_path}")
    except Exception as e:
        typer.echo(
            "❌ Writing Parquet failed. On Windows this typically "
            "requires winutils/HADOOP_HOME.\n"
            f"   Details: {e}\n"
            "   Tip: Run again with --bronze-path 'view:bronze_orders' "
            "to avoid filesystem writes."
        )


# 👇 entry point
cli = app
