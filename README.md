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

在whitelist.json文件下你应该填入以下信息
- group name

你的python env应当安装以下两个模块
- openai
- itchat-uos-fix

然后运行re_wxbot.py(把wxbot.py重构了一遍)


## bot指令（在wx聊天框输入）
普通用户：

| command     | use     |
| ------------ | ------------ |
| /help  | 查看帮助 |
| /ask  | 向bot提出问题，会返回回答 |
| /u add  | 在请求以user角色中加入content，不会返回回答 |

管理员：
| command     | use     |
| ------------ | ------------ |
| /sys su {密码}| 切换到operator |
| /sys su list| 现有的op |
| /sys su reset| 重置op列表 |
| /sys init  | 保存并重置本轮对话 |
| /sys init {prompt}  | 自定义初始prompt |
| /sys add {role} {content}  | 以指定role添加content，不返回回答 |
| /sys print msg | 输出本轮对话所有内容 |
| /sys save  | 保存本轮对话 |
| /sys reload whitelist | 重新加载群组白名单 |
| /sys reload op | 重新加载op白名单 |
| /sys enable group_auth {true/false} | 打开/关闭群组白名单 |
| /sys enable op_auth {true/false} | 打开/关闭op白名单 |


## 接下来要做的
- 各个用户有独立的session
- 可以读取过去的对话
- 队列
- 完善文档

## 存在的问题

微信获取到的ActualName会变化，需要找到一种新的方式管理权限

## 参考
gpt_api.py参考https://github.com/hzq1995/UI-of-chatGPT-API

（做了一些小改动）
