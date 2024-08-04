import os

import openai

from openai import OpenAI

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ['OPENAI_API_KEY'],
)


openai.api_key = os.environ['OPENAI_API_KEY']

def gpt_request_chatComplection(engine,prompts,temperature=0.0,stream=True):

    response= openai.ChatCompletion.create(
        model=engine,
        messages=prompts,
        temperature=temperature,
        stream=stream,
    )

    message = ""

    if stream:
        for chunk in response:
            delta = chunk["choices"][0]["delta"]
            if "content" in delta:
                message += delta["content"]
    else:
        message=response["choices"][0]["message"]
    return message

def gpt_request_chatComplection_new(engine,prompts,temperature=0.0):

    stream= client.chat.completions.create(
        model=engine,
        messages=prompts,
        temperature=temperature,
        stream=True,
    )
    message = ""

    for chunk in stream:
        # print(chunk.choices[0].delta.content or "", end="")
        message+=chunk.choices[0].delta.content or ""
    return message

model0="text-embedding-3-small"
model1="text-embedding-3-large"
model2="text-embedding-ada-002"
def get_embedding(text, model=model0):
   text = text.replace("\n", " ")
   # return client.embeddings.create(input = [text], model=model,  encoding_format="float",  dimensions=256).data[0].embedding
   return client.embeddings.create(input = [text], model=model,  encoding_format="float").data[0].embedding



