from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    pipeline,
    logging,
    TrainerCallback,
    Gemma3ForCausalLM
)
from trl import SFTConfig, SFTTrainer
from peft import LoraConfig
from torch.utils.data import DataLoader
from datasets import load_dataset
import torch
import asyncio


import asyncio
import time
from transformers import TrainerCallback


WEIGHTS_PATH = '/app/weights/weights.pth'

class WebSocketCallback(TrainerCallback):
    def __init__(self, websocket, loop):
        self.websocket = websocket
        self.loop = loop  # Main event loop
        self.last_update = time.time()
        asyncio.create_task(self._check_for_updates())

    async def _check_for_updates(self):
        while True:
            await asyncio.sleep(1)  # check every second
            now = time.time()
            if now - self.last_update > 5:  # if no update for 5 seconds
                try:
                    asyncio.run_coroutine_threadsafe(
                        self.websocket.send_json({"status": "waiting for updates"}), self.loop
                    )
                    self.last_update = now
                except Exception as e:
                    print("Error sending waiting update:", e)
                    break

    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs is not None:
            self.last_update = time.time()
            asyncio.run_coroutine_threadsafe(
                self.websocket.send_json(logs), self.loop
            )
        return control


class FineTuningEngine:

    def __init__(self, model_name, websocket):
        self.datasets = []
        self.model_name = model_name
        self.trainer = None
        self.websocket = websocket
        self.model = self.create_model(self.model_name)
        self.weights_path = WEIGHTS_PATH

    def set_websocket(self, websocket):
        self.websocket = websocket

    def load_new_dataset(self, dataset_name:str, file_extension:str='json'):
        path_to_dataset = f'./uploads/{dataset_name}'
        dataset = load_dataset(file_extension, data_files=path_to_dataset, split="train")
        self.datasets.append(dataset)
        return dataset

    def set_lora_fine_tuning(self, dataset=None, learning_rate=2e-4, epochs=1, lora_rank=4, callback_loop=None):
        if dataset is None:
            ccdv_dataset = "King-Harry/NinjaMasker-PII-Redaction-Dataset"
            dataset = load_dataset(ccdv_dataset, split="train", trust_remote_code=True)
            self.dataset = dataset

        peft_params = LoraConfig(
        lora_alpha=16,
        lora_dropout=0.1,
        target_modules=["q_proj", "v_proj"],
        r=lora_rank,
        bias="none",
        task_type="CAUSAL_LM",
        )

        tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "right"

        training_params = TrainingArguments(
        output_dir="./results",
        num_train_epochs=epochs,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=1,
        optim="adamw_torch",
        save_steps=25,
        logging_steps=1,
        learning_rate=learning_rate,
        weight_decay=0.001,
        fp16=False,
        bf16=False,
        max_grad_norm=0.3,
        max_steps=-1,
        warmup_ratio=0.03,
        group_by_length=True,
        lr_scheduler_type="constant",
        report_to="tensorboard",
        per_device_eval_batch_size =8
        )

        trainer = SFTTrainer(
        model=self.model,
        train_dataset=dataset,
        peft_config=peft_params,
        tokenizer=tokenizer,
        args=training_params,
        callbacks=[WebSocketCallback(self.websocket, callback_loop)]  # Add the custom callback here
        )

        self.trainer = trainer

    def perform_fine_tuning(self, update_callback=None):

        if self.trainer is None:
            raise Exception("Error! You must create trainer before fine tuning")
        
        self.trainer.train()
        self.trainer.model.merge_and_unload()
        #self.model.save_pretrained(self.weights_path)
        #save weights
        torch.save(self.trainer.model.state_dict(), self.weights_path)
        #self.trainer.model.save_pretrained(self.weights_path)



    def create_model(self, model_name:str="princeton-nlp/Sheared-LLaMA-1.3B"):
        # model = AutoModelForCausalLM.from_pretrained(
        #     model_name,
        #     device_map="cpu"
        # )
        model = Gemma3ForCausalLM.from_pretrained(model_name, 
                                          device_map="cpu")
        model.config.use_cache = False
        model.config.pretraining_tp = 1
        return model
    