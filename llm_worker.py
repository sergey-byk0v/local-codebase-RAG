import os
from pathlib import Path
import json
import time
from datetime import datetime
import redis

import torch

from transformers import AutoTokenizer, AutoModelForCausalLM


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REQ_QUEUE = "llm:req"

r = redis.Redis.from_url(REDIS_URL, decode_responses=True)

# set up LLM
DEVICE = "cuda"
# model_id = "ibm-granite/granite-4.0-350m"
model_id = "Qwen/Qwen2.5-Coder-1.5B-Instruct"   

try:
    tokenizer = AutoTokenizer.from_pretrained(model_id, local_files_only=True)
    llm_model = AutoModelForCausalLM.from_pretrained(model_id, device_map=DEVICE, local_files_only=True)
except Exception as e:
    print('-'*8 + 'Failed to load model' + '-'*8)
    raise e

def promt_formater(context: str):
    content = (f"""
    Answer shortly to following question.
    Message:{context}
    Response:"""
    )
    return [{"role": "user", "content": content}]


def main():
    print("LLM test worker listening on", REQ_QUEUE)
    try:
        while True:
            item = r.blpop(REQ_QUEUE, timeout=1)  # blocks up to 5s
            if not item:
                continue
            _, raw = item
            try:
                payload = json.loads(raw)
            except Exception:
                payload = {"raw": raw}

            reply_queue = payload.get("reply_queue") or f"llm:resp:{payload.get('request_id','')}"

            prompt = payload.get("prompt", "")
            llm_prompt = promt_formater(prompt)
            input_ids = tokenizer.apply_chat_template(
                llm_prompt,
                add_generation_prompt=True,
                tokenize=True,
                return_dict=True,
                return_tensors="pt",
            ).to(DEVICE)
            outputs = llm_model.generate(**input_ids,
                                        do_sample=True,
                                        temperature=0.9,
                                        #  use_cache=False,
                                        max_new_tokens=300
                                        )
            new_tokens = outputs[0][input_ids['input_ids'].shape[1]:]
            response = tokenizer.decode(new_tokens, skip_special_tokens=True)

            resp_payload = {"response": response, "ts": time.time()}

            # push answer (Streamlit app will BLPOP this queue)
            r.rpush(reply_queue, json.dumps(resp_payload))
            print("Answered request:", payload.get("request_id"), "->", response)
    except KeyboardInterrupt:
        print("Worker stopped")

if __name__ == "__main__":
    main()