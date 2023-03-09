import time
import itchat as bot
import gpt_api
import re
from datetime import datetime
import json


def archive(data):
    current_time = datetime.now()
    time_format = current_time.strftime("%Y-%m-%d_%H-%M-%S")
    filename = f'history/{time_format}.json'
    with open(filename, 'w', encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def session():
    s1 = gpt_api.gpt_thread()


def auth(username):
    if username == #用户id:
        return True


t1 = gpt_api.gpt_thread()


@bot.msg_register('Text', isGroupChat=True)
def groupchat_reply(msg):
    print(msg['Text'])
    message_receive = msg['Text']
    NickName = msg['ActualNickName']
    UserName = msg['ActualUserName']
    print(f'{NickName} says {message_receive}')
    if message_receive.startswith('/'):
        if message_receive == '/init':
            if auth(UserName):
                data = t1.messages
                archive(data)
                t1.reset_log()
                print('重置成功')
                bot.send('重置成功\n上一轮对话已保存', msg['FromUserName'])
            else:
                bot.send(f'{NickName} is unauthorized for command {message_receive}!!!!', msg['FromUserName'])
        elif message_receive == '/save':
            if auth(UserName):
                archive(t1.messages)
                print('保存成功')
                bot.send('本轮对话已保存', msg['FromUserName'])
            else:
                bot.send(f'{NickName} is unauthorized for command {message_receive}!!!!', msg['FromUserName'])
        elif message_receive == '/print msg':
            if auth(UserName):
                print(t1.messages)
                for item in t1.messages[1:]:
                    role = item['role']
                    content = item['content']
                    time.sleep(0.2)
                    bot.send(f'{role} says {content}', msg['FromUserName'])
            else:
                bot.send(f'{NickName} is unauthorized for command {message_receive}!!!!', msg['FromUserName'])
        elif message_receive == '/test':
            print('运行正常喵~')
            bot.send('运行正常喵~', msg['FromUserName'])
        elif message_receive == '/logout':
            bot.logout()
        elif message_receive == '/help':
            if auth(UserName):
                bot.send('用法：/ask 你的问题\n'
                         '更多命令：\n'
                         '/init\t保存上一轮对话并重置prompt\n'
                         '/save\t保存本轮对话\n'
                         '/sys init {prompt}\t重置初始prompt\n'
                         '/sys add {role} {content}\t添加自定义身份的信息\n'
                         '可用的角色：\nsystem\tassistant\tuser\n'
                         '/print msg\t查看本轮对话所有信息',
                         msg['FromUserName'])
            else:
                bot.send('用法：/ask 你的问题\n'
                         '更多命令：\n'
                         '/add 只添加content',
                         msg['FromUserName'])
        elif message_receive.startswith('/sys'):
            if auth(UserName):
                print('将以system操作')
                pattern = r"/sys\s+(.*)"
                result = re.findall(pattern, message_receive)[0]
                if result.startswith('init'):
                    pattern = r"init\s+(.*)"
                    result = re.findall(pattern, result)[0]
                    t1.reset_log()
                    t1.reset_system_content(result)
                    print(f'将初始prompt更改为：{result}')
                    bot.send(f'将初始prompt更改为：{result}.', msg['FromUserName'])
                elif result.startswith('add'):
                    pattern = r"add\s+(.*)"
                    result = re.findall(pattern, result)[0]
                    roles = {'system': 0, 'user': 1, 'assistant': 2}
                    for role in roles:
                        if result.startswith(role):
                            pattern = r"[a-zA-Z]+\s+(.*)"
                            result = re.findall(pattern, result)[0]
                            t1.add_content(role, result)
                            print(f'add：{result} as {role}')
                            bot.send(f'以{role}身份添加了prompt：{result}.', msg['FromUserName'])
            else:
                bot.send(f'{NickName} is unauthorized for command {message_receive}!!!!', msg['FromUserName'])
        elif message_receive.startswith('/ask'):
            pattern = r"/ask\s+(.*)"
            result = re.findall(pattern, msg['Text'])[0]
            res = t1.get_response(result)
            reply_text = res['choices'][0]['message']['content']
            print(f'Bot says {reply_text}')
            bot.send(reply_text, msg['FromUserName'])
        elif message_receive.startswith('/add'):
            pattern = r"/add\s+(.*)"
            result = re.findall(pattern, msg['Text'])[0]
            t1.add_content('user', result)
            bot.send(f'以 user 身份添加了prompt：{result}.', msg['FromUserName'])
        else:
            bot.send('わからない（', msg['FromUserName'])


if __name__ == '__main__':
    bot.auto_login(hotReload=True)
    bot.run()
