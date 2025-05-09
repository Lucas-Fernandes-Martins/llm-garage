# vertex_job.py
from google.cloud import aiplatform

def submit_custom_job(project_id: str, region: str, container_uri: str, display_name: str,
                      dataset_path: str, epochs: int, learning_rate: float, lora_rank: int):
    aiplatform.init(project=project_id, location=region)

    command = "python"
    args = [
        "main.py",
        "--dataset_path", dataset_path,
        "--epochs", str(epochs),
        "--learning_rate", str(learning_rate),
        "--lora_rank", str(lora_rank)
    ]

    # The training container must be built to read WS_UPDATE_URL.
    custom_job = {
        "display_name": display_name,
        "job_spec": {
            "worker_pool_specs": [
                {
                    "machine_spec": {"machine_type": "n1-standard-4"},
                    "replica_count": 1,
                    "container_spec": {
                        "image_uri": container_uri,
                        "command": [command],
                        "args": args,
                        "env": [
                            {"name": "WS_UPDATE_URL", "value": "ws://your-backend.example.com/ws/producer"}
                        ]
                    },
                }
            ],
        },
    }

    job = aiplatform.CustomJob(**custom_job)
    job.run(sync=False)  # Launch the job asynchronously
    return job
