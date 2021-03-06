#-*- coding:utf-8 -*-

import re

from wolflib.stagewitchnight import StageWitchNight
from wolflib import stageDemonNightBGM, stageDemonNightVoice, stageDemonNightEnding
from wolflib.gamemanager import GameManager

class StageDemonNight():
    def __init__(self, gm):
        self.parent = None
        self.running = True
        
        self.stageCompleted = False

        self.bgmRepeat = True
        self.bgm = stageDemonNightBGM
        self.voice = stageDemonNightVoice
        self.ending = stageDemonNightEnding
        
        # get gamemanager from previous stage
        self.gamemanager = gm
        # the demons who are alive
        self.aliveDemonList = []
        for seatNo in self.gamemanager.role2seatNoList(u'恶魔'):
            if self.gamemanager.isAlive(seatNo):
                self.aliveDemonList.append(seatNo)
        
    def isSkipped(self):
        if self.gamemanager.N_DEMON == 0:
            return True
        else:
            return False
    
    def isWithoutAction(self):
        # the stage needs no action if no living roles
        if len(self.aliveDemonList) == 0:
            return True
        else:
            return False
            
    def get_sleepTimeBounds(self):
        return (5.0, 15.0)

    def get_msgIntroList(self):
        msgIntroList = []
        if self.isWithoutAction():
            return msgIntroList
        # 告知恶魔如何验神
        for seatNo in self.aliveDemonList:
            msgIntroList.append({'ToUserName': self.gamemanager.getUserName(seatNo),
                                 'Text': u'请输入验神的号码：' })
        return msgIntroList

    def msgVerify(self, msg):
        fromSeatNo = self.gamemanager.userName2seatNo(msg['FromUserName'])
        # if fromUserName not in game
        if fromSeatNo is None:
            return False
        if fromSeatNo not in self.aliveDemonList:
            if not self.gamemanager.SOLO_DEBUG:
                return False
        return True
        
    def msgHandle(self, msg):
        msgReplyList = []
        fromUserName = msg['FromUserName']
        m = re.search(u'^([0-9]+)$', msg['Text'])
        if m is None: 
            msgReplyList.append({'ToUserName': fromUserName,
                                 'Text': u'输入无效，请输入数字号码' })
            return msgReplyList
        mSeatNo = int(m.group(1))
        # check errors
        if mSeatNo > self.gamemanager.N_TOTAL:
            msgReplyList.append({'ToUserName': fromUserName,
                                 'Text': u'您输入的号码%d大于游戏人数%d人，输入无效' % (mSeatNo, self.gamemanager.N_TOTAL) })
            return msgReplyList
        if not self.gamemanager.isAlive(mSeatNo):
            msgReplyList.append({'ToUserName': fromUserName,
                                 'Text': u'%d号玩家已离开游戏，输入无效' % mSeatNo })
            return msgReplyList
        # now handle
        if mSeatNo in self.gamemanager.getGodList():
            msgReplyList.append({'ToUserName': fromUserName,
                                 'Text': u'%d号玩家是神民' % mSeatNo })
        else:
            msgReplyList.append({'ToUserName': fromUserName,
                                 'Text': u'%d号玩家不是神民' % mSeatNo })
        self.stageCompleted = True
        return msgReplyList
        
    def enterNextStage(self):
        self.running = False
        self.parent.nextStage = StageWitchNight(self.gamemanager)
        self.parent.set_active_stage(self.parent.nextStage)
        if self.parent.nextStage.isSkipped():
            self.parent.nextStage.enterNextStage()
