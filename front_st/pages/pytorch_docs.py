import os
import uuid
import json
from time import sleep
from pathlib import Path

import numpy as np
import streamlit as st

import torch
from sentence_transformers import SentenceTransformer, util

import redis

st.title("Pytorch documentation search")
st.set_page_config(
    page_title="RAG",
    page_icon="🤖")


def find_closest_embeddings(embeds_df, target_emded, top_n=5):
    embeddings = embeds_df[:, 3:]
    distances = np.mean((embeddings - target_emded)**2, axis=1)
    top_indices = np.argsort(distances)[:top_n]

    return embeds_df[top_indices, 0], embeds_df[top_indices, 2], top_indices

def create_question(question, names, docstrings):
    names = ['`' + x + '`' for x in names]
    results_str = f'''{question}  
    Also I found couple functions / methods that could help :  
    [{", ".join(names)}]  
    Here's description for first one:   
    name - `{names[0]}`  
    dicstring - `{docstrings[0]}`
    '''
    return results_str


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
r = redis.Redis.from_url(REDIS_URL, decode_responses=True)
REQ_QUEUE = "llm:req"
embeds_path = Path("../") / "embedings" / "torch_doc_embeds_v2.npy"
embeds_df = np.load(embeds_path, allow_pickle=True)

if "embedding_model" not in st.session_state:
    st.session_state.embedding_model = SentenceTransformer(model_name_or_path="all-mpnet-base-v2", 
                                                           device="cpu",
                                                           local_files_only=True)



if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What do you search today?"):
    
    target_emded = st.session_state.embedding_model.encode(prompt)
    names, docstrings, _ = find_closest_embeddings(embeds_df, target_emded)

    prompt = create_question(prompt, names, docstrings)
    
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # push request to redis
    request_id = uuid.uuid4().hex
    reply_queue = f"llm:resp:{request_id}"

    payload = {
        "request_id": request_id,
        "reply_queue": reply_queue,
        "prompt": prompt,
        "history": json.dumps(st.session_state.messages),
    }
    r.rpush(REQ_QUEUE, json.dumps(payload))

response = f"{prompt}"

with st.chat_message("assistant"):
    with st.spinner("Wait for LLM responce...", show_time=True):
        if prompt:
            print('-'*20)
            print(prompt)
            print('-'*20)

            item = r.blpop(reply_queue, timeout=600)
            if item is None:
                response = "Timed out waiting for the worker."
            else:
                _, raw = item

                try:
                    response = json.loads(raw).get("response", raw)
                except Exception:
                    response = raw

        else:
            response = "Hello! How can I assist you today?"
        st.markdown(response)

st.session_state.messages.append({"role": "assistant", "content": response})