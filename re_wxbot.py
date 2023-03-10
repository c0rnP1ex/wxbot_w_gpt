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
        self.gpt = gpt_api.gpt_thread()
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

    def receive_msg(self, msg):
        self.msg = msg
        self.text = self.msg['Text']
        self.FromUser = self.msg['FromUserName']
        self.GroupName = self.msg['User']['NickName']
        self.NickName = self.msg['ActualNickName']
        self.UserName = self.msg['ActualUserName']
        if self.bool_whitelist():
            print(f'{self.NickName} says {self.text}')

    def start(self):
        self.bot_thread.run()

    def text_reply(self, reply_msg):
        print(f'床爪 says {reply_msg}')
        self.bot_thread.send(reply_msg, self.FromUser)

    def help(self):
        if self.op_auth(send_res=False):
            self.text_reply('用法：/ask {你的问题}\n'
                            '/u add {content}')
        else:
            self.text_reply('用法：\n'
                            '/help\t查看帮助\n'
                            '/ask {你的问题}\n'
                            '/u add {content}\n'
                            '更多用法：\n'
                            '/sys su {password}\t切换到operator\n'
                            '/sys su list\t现有的op\n'
                            '/sys su reset\t重置op列表\n'
                            '/sys init\t保存并重置本轮对话\n'
                            '/sys init {prompt}\t自定义初始prompt\n'
                            '/sys add {role} {content}\t加入指定角色的内容\n'
                            '/sys print msg\t输出本轮对话的所有内容\n'
                            '/sys save\t保存本轮对话\n'
                            '/sys reload whitelist\t重新加载群组白名单\n'
                            '/sys reload op\t重新加载op白名单\n'
                            '/sys enable group_auth {true/false}\t打开/关闭群组白名单\n'
                            '/sys enable op_auth {true/false}\t打开/关闭op白名单')

    def enable_group_auth(self, _bool):
        self.bool_group_auth = _bool

    def enable_op_auth(self, _bool):
        self.bool_op_auth = _bool

    def ask(self):
        pattern = r"/ask\s(.*)"
        match = re.findall(pattern, self.text, re.DOTALL)[0]
        response = self.gpt.get_response(match)
        reply_msg = response['choices'][0]['message']['content']
        self.text_reply(reply_msg)

    def u_add(self):
        pattern = r"/u add\s(.*)"
        match = re.findall(pattern, self.text, re.DOTALL)[0]
        self.gpt.add_content('user', match)
        self.text_reply(f'[{self.NickName}] 添加了 [{match}]')

    def sys(self):
        if self.op_auth(send_res=False):
            if self.text == '/sys su list':
                time.sleep(0.2)
                self.text_reply('当前operator')
                for item in self.operator_NickName:
                    time.sleep(0.2)
                    self.text_reply(item)
                return
            elif self.text == '/sys su reset':
                time.sleep(0.2)
                self.operator = []
                self.operator_NickName = []
                self.text_reply('已重置operator')
                return
            elif self.text == '/sys init':
                archive(self.gpt.messages)
                self.gpt.reset_log()
                self.text_reply('已重置')
                return
            elif self.text.startswith('/sys init'):
                pattern = r"/sys init\s(.*)"
                match = re.findall(pattern, self.text, re.DOTALL)[0]
                self.gpt.reset_system_content(match)
                self.text_reply(f'将初始prompt设置为[{match}]')
                return
            elif self.text.startswith('/sys add'):
                pattern = r"/sys add\s+(.*)"
                match = re.findall(pattern, self.text)[0]
                roles = {'system': 0, 'user': 1, 'assistant': 2}
                for role in roles:
                    if match.startswith(role):
                        pattern = r"[a-zA-Z]+\s+(.*)"
                        match = re.findall(pattern, match)[0]
                        self.gpt.add_content(role, match)
                        self.text_reply(f'Add：[{match}] as [{role}].')
                return
            elif self.text == '/sys print msg':
                for item in self.gpt.messages[1:]:
                    role = item['role']
                    content = item['content']
                    time.sleep(0.2)
                    self.text_reply(f'{role} says {content}')
                return
            elif self.text == '/sys save':
                archive(self.gpt.messages)
                self.text_reply('已保存本轮对话')
                return
            elif self.text == '/sys reload whitelist':
                self.whitelist = get_whitelist()
                self.text_reply('已重新加载白名单')
                return
            elif self.text == '/sys reload op':
                self.load_op_auth()
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
                    self.text_reply('わからない（')
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
                    self.text_reply('わからない（')
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
                elif self.text.startswith('/sys'):
                    self.sys()
                elif self.text.startswith('/u add'):
                    self.u_add()
                else:
                    self.text_reply('わからない（')


def MainThread(wxbot1):
    @wxbot1.bot_thread.msg_register('Text', isGroupChat=True)
    def groupchat_reply(msg):
        wxbot1.receive_msg(msg)
        wxbot1.lex()

    wxbot1.start()


if __name__ == '__main__':
    bot_instance = wxbot()
    MainThread(bot_instance)
