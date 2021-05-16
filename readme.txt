Python 狼人杀小法官 writen in python using pygame game library and itchat

Creator: Changnan Peng <839465687@qq.com>

先用文本编辑器打开data文件夹中的rules.json，更改游戏人数等设定
再用python运行pyWolfGame.py，会自动弹出二维码
扫码登录网页版微信，向扫码者发送“我要玩x号”进入游戏，其中x为座位号

若提示remove game lock，则删除game.lock文件即可
若需要人声减弱的版本，可在data文件夹中删去sound文件夹及其中文件，更改sound_small文件夹名称为sound

Acknowledgement: orneo1212 <orneo1212@gmail.com>'s FarmGame

更多说明：
用之前要安装pygame和itchat两个python package（比如可以pip install pygame itchat），要用的时候先打开data文件夹里的rules.json更改人数，然后用terminal（或者Windows的cmd）运行python pyWolfGame.py，一切正常的话会弹出一个二维码，用微信扫码登录，bgm就会响起来了，然后加了你微信的小伙伴们就可以给你发“我要玩x号"了。注意你自己要先在微信的设置里开消息免打扰（避免别人发给你信息的时候出现弹窗），然后你玩的时候要给手机微信上的文件传输助手发”我要玩x号“，并且之后游戏全程只打开文件传输助手的界面，对文件传输助手发消息（就跟你们发消息给我那样）。