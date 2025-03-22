gcloud builds submit --region=us-central1 --tag us-central1-docker.pkg.dev/llm-garage/llm-garage-repo/llm-garage:latest


gcloud artifacts repositories create llm-garage-repo --repository-format=docker     --location=us-central1 --description="Docker repository"

