curl -X POST "http://127.0.0.1:8000/dataset/upload" -F "file=@C:\Users\LucasMartins\Documents\llm_garage\data\data_test.json"
curl -X POST "http://127.0.0.1:8000/finetune/set_train_params" -H "Content-Type: application/json" -d "{\"model_name\": \"google/gemma-2b\", \"dataset_path\": \"data_test.json\"}"
