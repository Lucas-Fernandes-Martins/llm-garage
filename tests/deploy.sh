gcloud builds submit --region=us-central1 --tag us-central1-docker.pkg.dev/llm-garage/llm-garage-repo/llm-garage:latest


gcloud artifacts repositories create llm-garage-repo --repository-format=docker     --location=us-central1 --description="Docker repository"

gcloud ai custom-jobs create \
  --region=us-central1 \
  --display-name="llm-garage-training" \
  --worker-pool-spec=machine-type=n1-standard-4,replica-count=1,container-image-uri=gcr.io/llm-garage/llm-garage-training:latest