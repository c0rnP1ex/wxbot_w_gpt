import time
import itchat as wx
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


def archive(data):
    current_time = datetime.now()
    time_format = current_time.strftime("%Y-%m-%d_%H-%M-%S")
    filename = f'history/{time_format}.json'
    write2json(filename, data)


def get_whitelist():
    data = readjson('whitelist.json')
    wl = data[0].get("group")
    whitelist = []
    for group, group_info in wl.items():
        name_value = group_info.get("name")
        whitelist.append(name_value)
    return whitelist


class wxbot:

    def __init__(self) -> None:
        self.bot_thread = wx.Core()
        self.bot_thread.auto_login(hotReload=True)
        self.gpt_thread = gpt_api.gpt_thread()
        self.msg = {}
        self.text = ''
        self.FromUser = ''
        self.GroupName = ''
        self.NickName = ''
        self.UserName = ''
        auth_config = readjson('auth.json')
        self.config_GroupName = auth_config[0]['accept_GroupName']
        self.config_NickName = auth_config[0]['accept_NickName']
        self.config_passwd = auth_config[0]['passwd']
        self.operator = []
        self.operator_NickName = []
        self.whitelist = get_whitelist()
        self.bool_group_auth = False
        self.bool_op_auth = False
        print(self.whitelist)

    def start(self):
        self.bot_thread.run()

    def receive_msg(self, msg):
        self.msg = msg
        self.text = self.msg['Text']
        self.FromUser = self.msg['FromUserName']
        self.GroupName = self.msg['User']['NickName']
        self.NickName = self.msg['ActualNickName']
        self.UserName = self.msg['ActualUserName']
        if self.bool_whitelist():
            current_time = datetime.now()
            time_format = current_time.strftime("%Y-%m-%d_%H-%M-%S")
            print(f'{time_format} From Group {self.GroupName} {self.NickName} says \n{self.text}')

    def text_reply(self, reply_msg):
        current_time = datetime.now()
        time_format = current_time.strftime("%Y-%m-%d_%H-%M-%S")
        print(f'{time_format} From Group {self.GroupName} ?????? says \n{reply_msg}')
        self.bot_thread.send(reply_msg, self.FromUser)

    def bool_whitelist(self, send_res=False):
        if self.bool_group_auth == True:
            return True
        if self.GroupName not in self.whitelist:
            if send_res:
                self.text_reply('Unregistered Group.')
            return False
        return True

    def load_op_auth(self):
        auth_config = readjson('auth.json')
        self.config_GroupName = auth_config[0]['accept_GroupName']
        self.config_NickName = auth_config[0]['accept_NickName']
        self.config_passwd = auth_config[0]['passwd']
        self.operator = []
        self.operator_NickName = []

    def op_auth(self, passwd=False, send_res=True):
        if self.bool_op_auth:
            return True
        if self.UserName not in self.operator:
            if passwd:
                if self.GroupName == self.config_GroupName:
                    if self.NickName == self.config_NickName:
                        if passwd == self.config_passwd:
                            self.operator.append(self.UserName)
                            self.operator_NickName.append(self.NickName)
                            self.text_reply(f'Added {self.NickName} to operator group.')
                            return True
        else:
            self.text_reply(f'{self.NickName} has authorization!')
            return True
        if send_res:
            self.text_reply(f'{self.NickName} has no authorization!')
        return False

    def help(self):
        if self.op_auth(send_res=False):
            self.text_reply('?????????\n'
                            '/help\t????????????\n'
                            '/ask {????????????}\n'
                            '/u add {content}\n'
                            '???????????????\n'
                            '/sys su {password}\t?????????operator\n'
                            '/sys su list\t?????????op\n'
                            '/sys su reset\t??????op??????\n'
                            '/sys init\t???????????????????????????\n'
                            '/sys init {prompt}\t???????????????prompt\n'
                            '/sys add {role} {content}\t???????????????????????????\n'
                            '/sys print msg\t?????????????????????????????????\n'
                            '/sys save\t??????????????????\n'
                            '/sys reload whitelist\t???????????????????????????\n'
                            '/sys reload op\t????????????op?????????\n'
                            '/sys enable group_auth {true/false}\t??????/?????????????????????\n'
                            '/sys enable op_auth {true/false}\t??????/??????op?????????')

        else:
            self.text_reply('?????????\n'
                            '/ask {????????????}\n'
                            '/u add {content}')

    def enable_group_auth(self, _bool):
        self.bool_group_auth = _bool

    def enable_op_auth(self, _bool):
        self.bool_op_auth = _bool

    def ask(self):
        pattern = r"/ask\s(.*)"
        match = re.findall(pattern, self.text, re.DOTALL)[0]
        response = self.gpt_thread.get_response(match)
        reply_msg = response['choices'][0]['message']['content']
        self.text_reply(reply_msg)

    def u_add(self):
        pattern = r"/u add\s(.*)"
        match = re.findall(pattern, self.text, re.DOTALL)[0]
        self.gpt_thread.add_content('user', match)
        self.text_reply(f'[{self.NickName}] ????????? [{match}]')

    def sys(self):
        if self.op_auth(send_res=False):
            if self.text == '/sys su list':
                self.text_reply('??????operator')
                for item in self.operator_NickName:
                    time.sleep(0.3)
                    self.text_reply(item)
                return
            elif self.text == '/sys su reset':
                time.sleep(0.2)
                self.operator = []
                self.operator_NickName = []
                self.text_reply('?????????operator')
                return
            elif self.text == '/sys init':
                archive(self.gpt_thread.messages)
                self.gpt_thread.reset_log()
                self.text_reply('??????????????????????????????')
                return
            elif self.text.startswith('/sys init'):
                archive(self.gpt_thread.messages)
                pattern = r"/sys init\s(.*)"
                match = re.findall(pattern, self.text, re.DOTALL)[0]
                self.gpt_thread.reset_system_content(match)
                self.text_reply(f'?????????????????????????????????prompt?????????[{match}]')
                return
            elif self.text.startswith('/sys add'):
                pattern = r"/sys add\s+(.*)"
                match = re.findall(pattern, self.text)[0]
                roles = {'system': 0, 'user': 1, 'assistant': 2}
                for role in roles:
                    if match.startswith(role):
                        pattern = r"[a-zA-Z]+\s+(.*)"
                        match = re.findall(pattern, match)[0]
                        self.gpt_thread.add_content(role, match)
                        self.text_reply(f'Add???[{match}] as [{role}].')
                return
            elif self.text == '/sys print msg':
                for item in self.gpt_thread.messages[1:]:
                    role = item['role']
                    content = item['content']
                    time.sleep(0.2)
                    self.text_reply(f'{role} says {content}')
                return
            elif self.text == '/sys save':
                archive(self.gpt_thread.messages)
                self.text_reply('?????????????????????')
                return
            elif self.text == '/sys reload whitelist':
                self.whitelist = get_whitelist()
                self.text_reply('??????????????????????????????')
                return
            elif self.text == '/sys reload op':
                self.load_op_auth()
                self.text_reply('???????????????op??????')
                return
            elif self.text.startswith('/sys enable group_auth'):
                pattern = r"/sys enable group_auth\s+(.*)"
                match = re.findall(pattern, self.text)[0]
                if match == 'true':
                    self.enable_group_auth(True)
                    self.text_reply('Switch group_auth to true.')
                elif match == 'false':
                    self.enable_group_auth(False)
                    self.text_reply('Switch group_auth to false.')
                else:
                    self.text_reply('??????????????????')
                return
            elif self.text.startswith('/sys enable op_auth'):
                pattern = r"/sys enable op_auth\s+(.*)"
                match = re.findall(pattern, self.text)[0]
                if match == 'true':
                    self.enable_op_auth(True)
                    self.text_reply('Switch op_auth to true.')
                elif match == 'false':
                    self.enable_op_auth(False)
                    self.text_reply('Switch op_auth to false.')
                else:
                    self.text_reply('??????????????????')
                return
        if self.text.startswith('/sys su'):
            pattern = r"/sys su\s+(.*)"
            passwd = re.findall(pattern, self.text)[0]
            self.op_auth(passwd=passwd)
            return
        else:
            self.op_auth()

    def lex(self):
        if self.text.startswith('/'):
            if self.bool_whitelist(send_res=True):
                if self.text == '/help':
                    self.help()
                elif self.text.startswith('/ask'):
                    self.ask()
                elif self.text.startswith('/u add'):
                    self.u_add()
                elif self.text.startswith('/sys'):
                    self.sys()
                else:
                    self.text_reply('??????????????????')


def MainThread(wxbot1):
    @wxbot1.bot_thread.msg_register('Text', isGroupChat=True)
    def groupchat_reply(msg):
        wxbot1.receive_msg(msg)
        wxbot1.lex()

    wxbot1.start()


if __name__ == '__main__':
    bot_instance = wxbot()
    MainThread(bot_instance)