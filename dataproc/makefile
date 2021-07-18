

REGION="europe-west1"
ZONE="europe-west1-b"
TEMPLATE_ID="download_production_table"

dev_dataproc_assets_bucket="gs://your-dataproc-assets-bucket/production/"
dev_project=your-gcp-project-id

upload_assets:
	gsutil cp main.py ${dev_dataproc_assets_bucket} --region ${REGION} --project ${dev_project}

upload_template:
	gcloud dataproc workflow-templates import ${TEMPLATE_ID} --region ${REGION} --source workflow-tmpl.yaml