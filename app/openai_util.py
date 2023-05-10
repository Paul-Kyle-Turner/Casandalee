import openai
import re
import time
from tqdm import tqdm
import tiktoken

from config import AppConfig

# openai init
openai.api_key = AppConfig.OPENAI_API_KEY


def get_openai_embeddings(content, engine=AppConfig.EMBEDDING_ENGINE):
    content = content.encode(
        encoding="ASCII", errors="ignore").decode()  # fix unicode errors
    print("here")
    response = openai.Embedding.create(input=content, engine=engine)
    vector = response['data'][0]['embedding']
    return vector


def openai_completion(messages, model=AppConfig.MODEL_ENGINE, max_retry=5):
    retry = 0
    while True:
        try:
            print("getting reponse from openai")
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages
            )
            text = response["choices"][0]["message"]['content'].strip()
            text = re.sub(r'[\r\n]+', "\n", text)
            text = re.sub(r'[\t]+', " ", text)
            return text

        except Exception as e:
            retry += 1
            if retry >= max_retry:
                return f"GPT4 error: {e}"
            print("Error in communication with openai.")
            time.sleep(1)


def openai_completion_stream(messages, model=AppConfig.MODEL_ENGINE, max_retry=5):
    retry_number = 0
    retry = True
    print(messages)
    print(model)
    while retry:
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                stream=True
            )
            retry = False
            for chunk in response:
                try:
                    text = chunk["choices"][0]['delta']['content']
                    if re.match(r'[0-9]', text):
                        yield " " + text
                    else:
                        yield text
                except Exception as e:
                    retry_number += 1
                    if retry_number >= max_retry:
                        return f"GPT4 error: {e}"
                    print("Error in communication with openai.")
                    time.sleep(1)

        except Exception as e:
            retry_number += 1
            if retry_number >= max_retry:
                return f"GPT4 error: {e}"
            print("Error in communication with openai.")
            time.sleep(1)

def get_embeddings_for_docx_sections(sections):
    for section_key in tqdm(sections):
        for chunk_key in sections[section_key]['chunks']:
            content = sections[section_key]['chunks'][chunk_key]
            vector = get_openai_embeddings(content, engine="text-embedding-ada-002")
            sections[section_key]['chunks'][chunk_key] = {'content': content, 'vector': vector}
    return sections

def num_tokens_from_string(string, encoding_name="cl100k_base"):
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens