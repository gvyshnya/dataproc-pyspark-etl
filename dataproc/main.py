from pyspark.sql.functions import *
from pyspark.context import SparkContext
from pyspark.sql.session import SparkSession
import sys

YES_TOKEN = "Yes"

sc = SparkContext.getOrCreate()
spark = SparkSession(sc)

gcp_project_id = 'your-project-id'  # it has to be replaced with the real GCP Project ID

def export_a_bigquery_view (
    dataset,
    entity_name,
    gcs_output_bucket,
    materialization_gcp_project_id,
    materialization_dataset,
    output_parquet,
    is_partitioned,
    is_full_reload,
    since_date
):
    table = "".join([gcp_project_id, '.', dataset, '.', entity_name])
    filter_value = f"createdAt > '{since_date}'"
    df = spark.read.format("bigquery") \
        .option("viewsEnabled", True) \
        .option("viewMaterializationProject", materialization_gcp_project_id) \
        .option("viewMaterializationDataset", materialization_dataset) \
        .option("filter", filter_value) \
        .load(table)
    
    spark_write_method = ""
    if is_full_reload:
        spark_write_method = "overwrite"
    else:
        # incremental update, doing append rather then overwrite
        spark_write_method = "append"
    
    if is_partitioned:
        # create a partition field
        df = df.withColumn("partitionDate", to_date(col('createdAt')))

        if output_parquet:
            # write down as a partitioned parquet file
            output_parquet_path = "".join(
                [
                    gcs_output_bucket,
                    '/parquet/', entity_name, '/'
                ])
            df.write.partitionBy("partitionDate").mode(spark_write_method).parquet(output_parquet_path)
        else:
            # write down as a partitioned JSON file
            output_json_path = "".join(
                [
                    gcs_output_bucket,
                    '/json/', entity_name, '/'
                ])
            df.write.partitionBy("partitionDate").mode(spark_write_method).json(output_json_path)
    else:
        # write down a non-partitioned table/view
        if output_parquet:
            # write down as a partitioned parquet file
            output_parquet_path = "".join(
                [
                    gcs_output_bucket,
                    '/parquet/', entity_name, '/'
                ])
            df.write.mode(spark_write_method).parquet(output_parquet_path)
        else:
            # write down as a partitioned JSON file
            output_json_path = "".join(
                [
                    gcs_output_bucket,
                    '/json/', entity_name, '/'
                ])
            df.write.mode(spark_write_method).json(output_json_path)

        
def main(argv):

    dataset = argv[0]
    entity_name = argv[1]
    gcs_output_bucket = argv[2]
    materialization_gcp_project_id = argv[3]
    materialization_dataset = argv[4]
    parquet_flag = argv[5]
    is_partitioned_flag = argv[6]
    is_full_reload_flag = argv[7]
    since_date = argv[8]

    output_parquet = False
    is_partitioned = False
    is_full_reload = False

    if parquet_flag == YES_TOKEN:
        output_parquet = True
    
    if is_partitioned_flag == YES_TOKEN:
        is_partitioned = True
    
    if is_full_reload_flag == YES_TOKEN:
        is_full_reload_flag = True
    
    export_a_bigquery_view (
        dataset,
        entity_name,
        gcs_output_bucket,
        materialization_gcp_project_id,
        materialization_dataset,
        output_parquet,
        is_partitioned,
        is_full_reload,
        since_date
    )


if __name__ == "__main__":
    main(sys.argv[1:])
    sc.stop()