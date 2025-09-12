import os
import databricks.sql

with databricks.sql.connect(
    server_hostname=os.getenv("DATABRICKS_HOST").replace("https://", ""),
    access_token=os.getenv("DATABRICKS_TOKEN"),
    http_path=os.getenv("DATABRICKS_SQL_PATH")  # from .env
) as conn:
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES")
    for row in cursor.fetchall():
        print(row)
