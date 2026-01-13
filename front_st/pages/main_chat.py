import os
import torch
import streamlit as st
import redis
import uuid
import json
from time import sleep


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
r = redis.Redis.from_url(REDIS_URL, decode_responses=True)
REQ_QUEUE = "llm:req"


st.title("RAGoBot")
st.set_page_config(
    page_title="RAGoBot",
    page_icon="🤖")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
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
        # wait for responce with wheel spinner
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