# wxbot_w_gpt
Wechat Bot with GPT

## 如何使用
在config.json文件下你应该填入以下信息
- proxy
- api-key
- initial_prompt

在auth.json文件下你应该填入以下信息
- accept_GroupName
- accept_NickName
- passwd

你的python env应当安装以下两个模块
- openai
- itchat-uos-fix

然后运行wxbot.py

## bot指令（在wx聊天框输入）
普通用户：

| command     | use     |
| ------------ | ------------ |
| /help  | 查看帮助 |
| /ask  | 向bot提出问题，会返回回答 |
| /add  | 在请求以user角色中加入content，不会返回回答 |

管理员：
| command     | use     |
| ------------ | ------------ |
| /init  | 保存本轮对话，并重置本轮对话 |
| /save  | 保存本轮对话 |
| /su {密码}| 切换为operator |
| /su list | 查看现有管理员 |
| /su reset | 清空所有管理员 |
| /sys init {prompt}  | 自定义初始prompt |
| /sys add {role} {content}  | 以指定role添加content，不返回回答 |
| /print  | 输出本轮对话所有内容 |


## 接下来要做的
- 各个用户有独立的session
- 可以读取过去的对话
- 队列
- 完善文档

## 存在的问题
指令的匹配不能换行（玩不明白正则表达式

如果/ask 后面的内容带有换行那换行符以后的内容不会进入message

微信获取到的ActualName会变化，需要找到一种新的方式管理权限

## 参考
gpt_api.py参考https://github.com/hzq1995/UI-of-chatGPT-API（做了一些小改动）
