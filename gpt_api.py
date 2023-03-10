import openai
import json

with open('config.json', encoding='utf-8') as f:
    config = json.load(f)

proxies = config[0]['proxies']
openai.proxy = proxies
openai.proxy

SECRET_KEY = config[0]['api-key']
openai.api_key = SECRET_KEY

ENGINE_LIST = openai.Engine.list()
MODEL_LIST = openai.Model.list()
MAX_TOKEN_LEN = 1024
TIME_OUT = 3

BOT_ROLE = 'assistant'
USER_ROLE = 'user'
initial_prompt = config[0]['initial_prompt']


class gpt_thread:
    def __init__(self) -> None:
        self.messages = []
        self.reset_log()

    def receive_message_from_api(self):
        response = []
        # self.messages.text.count
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo-0301',
            messages=self.messages,
            temperature=1.0,
            max_tokens=MAX_TOKEN_LEN,
            top_p=0.6,
            frequency_penalty=2.0,
            presence_penalty=0.0,
            timeout=TIME_OUT,
        )
        return response

    def get_response(self, prompt):
        self.add_user_content(prompt)
        response = self.receive_message_from_api()
        self.add_bot_content(response['choices'][0]['message']['content'])
        return response

    def reset_log(self):
        self.messages = [{'role': 'system', 'content': f'{initial_prompt}，你的角色是 {BOT_ROLE}。'}]

    def add_user_content(self, content):
        self.messages.append({'role': USER_ROLE, 'content': content})

    def add_content(self, ROLE_add, content):
        self.messages.append({'role': ROLE_add, 'content': content})

    def add_bot_content(self, content):
        self.messages.append({'role': BOT_ROLE, 'content': content})

    def reset_system_content(self, content):
        self.messages = [{'role': 'system', 'content': content}]


if __name__ == '__main__':
    gpt_thread1 = gpt_thread();
    resp = gpt_thread1.get_response('hello')
    print(resp['choices'][0]['message']['content'])
