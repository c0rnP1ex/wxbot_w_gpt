import time
import itchat as bot
import gpt_api
import re
from datetime import datetime
import json

def readjson(filename):
    with open(filename, encoding='utf-8') as f:
        data = json.load(f)
    return data


def write2json(filename, data):
    with open(filename, 'w', encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


class authorize:
    def __init__(self) -> None:
        auth_config = readjson('auth.json')
        self.config_GroupName = auth_config[0]['accept_GroupName']
        self.config_NickName = auth_config[0]['accept_NickName']
        self.cofig_passwd = auth_config[0]['passwd']
        self.operator = []
        self.operator_NickName =[]

    def auth(self, msg):
        message_receive = msg['Text']
        if message_receive.startswith('/su'):
            GroupName = msg['User']['NickName']
            NickName = msg['ActualNickName']
            UserName = msg['ActualUserName']
            pattern = r"/su\s+(.*)"
            passwd = re.findall(pattern, message_receive)[0]
            if UserName not in self.operator:
                if GroupName == self.config_GroupName:
                    if NickName == self.config_NickName:
                        if passwd == self.cofig_passwd:
                            self.operator.append(UserName)
                            self.operator_NickName.append(NickName)
                            bot.send(f'Added {NickName} to operator group.',
                                     msg['FromUserName'])
                            print(f'Added {NickName} to operator group.')
                            return
            else:
                bot.send(f'{NickName} has authorization!',
                         msg['FromUserName'])
                print(f'{NickName} has authorization!')
                return
            bot.send(f'{NickName} has no authorization!',
                     msg['FromUserName'])
            print(f'{NickName} has no authorization!')
            return

    def bool_(self, msg):
        GroupName = msg['User']['NickName']
        NickName = msg['ActualNickName']
        UserName = msg['ActualUserName']
        time.sleep(0.2)
        if UserName not in self.operator:
            bot.send(f'{NickName} authorized failed!',
                     msg['FromUserName'])
            print(f'auth failed!')
            return False
        else:
            bot.send(f'{NickName} authorized success!',
                     msg['FromUserName'])
            return True

    def reset_op(self):
        self.operator = []
        self.operator_NickName = []


def archive(data):
    current_time = datetime.now()
    time_format = current_time.strftime("%Y-%m-%d_%H-%M-%S")
    filename = f'history/{time_format}.json'
    write2json(filename, data)


t1 = gpt_api.gpt_thread()
auth_check = authorize()

@bot.msg_register('Text', isGroupChat=True)
def groupchat_reply(msg):
    print(msg['FromUserName'])
    print(msg['Text'])
    message_receive = msg['Text']
    GroupName = msg['User']['NickName']
    NickName = msg['ActualNickName']
    UserName = msg['ActualUserName']
    # pattern = r"@??????\s+(.+)"
    # result = re.findall(pattern, msg['Text'])[0]
    # print(msg['FromUserName'] + ' ' + message_receive)
    print(f'{NickName} says {message_receive}')
    auth_check.auth(msg)
    if message_receive.startswith('/'):
        if message_receive.startswith('/su'):
            if auth_check.bool_(msg):
                if message_receive.startswith('/su reset'):
                    auth_check.reset_op()
                    time.sleep(0.2)
                    bot.send('?????????operator', msg['FromUserName'])
                elif message_receive.startswith('/su list'):
                    time.sleep(0.2)
                    bot.send('??????operator', msg['FromUserName'])
                    for item in auth_check.operator_NickName:
                        time.sleep(0.2)
                        bot.send(item, msg['FromUserName'])
        elif message_receive == '/init':
            if auth_check.bool_(msg):
                data = t1.messages
                archive(data)
                t1.reset_log()
                print('????????????')
                bot.send('???????????????????????????????????????????????????????????????\n????????????????????????', msg['FromUserName'])
            else:
                bot.send(f'{NickName} is unauthorized for command {message_receive}!!!!', msg['FromUserName'])
        elif message_receive == '/save':
            if auth_check.bool_(msg):
                archive(t1.messages)
                print('????????????')
                bot.send('?????????????????????', msg['FromUserName'])
            else:
                bot.send(f'{NickName} is unauthorized for command {message_receive}!!!!', msg['FromUserName'])
        elif message_receive == '/print msg':
            if auth_check.bool_(msg):
                print(t1.messages)
                for item in t1.messages[1:]:
                    role = item['role']
                    content = item['content']
                    time.sleep(0.2)
                    bot.send(f'{role} says {content}', msg['FromUserName'])
            else:
                bot.send(f'{NickName} is unauthorized for command {message_receive}!!!!', msg['FromUserName'])
        elif message_receive == '/test':
            print('?????????????????????~')
            bot.send('?????????????????????~', msg['FromUserName'])
        elif message_receive == '/logout':
            bot.logout()
        elif message_receive == '/help':
            if auth_check.bool_(msg):
                bot.send('?????????/ask ????????????\n'
                         '???????????????\n'
                         '/add ?????????content\n'
                         '/init\t??????????????????????????????prompt\n'
                         '/save\t??????????????????\n'
                         '/su {??????} ?????????operator\n'
                         '/su list ?????????????????????\n'
                         '/su reset ?????????????????????\n'
                         '/sys init {prompt}\t????????????prompt\n'
                         '/sys add {role} {content}\t??????????????????????????????\n'
                         '??????????????????\n'
                         'system\tassistant\tuser\n'
                         '/print msg\t??????????????????????????????',
                         msg['FromUserName'])
            else:
                bot.send('?????????/ask ????????????\n'
                         '???????????????\n'
                         '/add ?????????content',
                         msg['FromUserName'])
        elif message_receive.startswith('/sys'):
            if auth_check.bool_(msg):
                print('??????system??????')
                pattern = r"/sys\s+(.*)"
                result = re.findall(pattern, message_receive)[0]
                if result.startswith('init'):
                    pattern = r"init\s+(.*)"
                    result = re.findall(pattern, result)[0]
                    t1.reset_log()
                    t1.reset_system_content(result)
                    print(f'?????????prompt????????????{result}')
                    bot.send(f'?????????prompt????????????{result}.', msg['FromUserName'])
                elif result.startswith('add'):
                    pattern = r"add\s+(.*)"
                    result = re.findall(pattern, result)[0]
                    roles = {'system': 0, 'user': 1, 'assistant': 2}
                    for role in roles:
                        if result.startswith(role):
                            pattern = r"[a-zA-Z]+\s+(.*)"
                            result = re.findall(pattern, result)[0]
                            t1.add_content(role, result)
                            print(f'add???{result} as {role}')
                            bot.send(f'???{role}???????????????prompt???{result}.', msg['FromUserName'])
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
            bot.send(f'??? user ???????????????prompt???{result}.', msg['FromUserName'])
        else:
            bot.send('??????????????????', msg['FromUserName'])


if __name__ == '__main__':
    bot.auto_login(hotReload=True)
    bot.run()
