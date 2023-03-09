# wxbot_w_gpt
Wechat Bot with GPT

## 如何使用
在gpt_api.py文件下你应该填入以下信息
- proxy
- api-key
- initial_prompt
然后运行wxbot.py

## 接下来要做的
- 各个用户有独立的session
- 可以保存读取过去的对话
- 更完善的权限（现在做的就是依托答辩
- 完善文档

## 存在的问题
指令的匹配不能换行（玩不明白正则表达式
如果/ask 后面的内容带有换行那换行符以后的内容不会进入message

## 参考
gpt_api.py抄的https://github.com/hzq1995/UI-of-chatGPT-API
