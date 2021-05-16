#-*- coding:utf-8 -*-

import re

from wolflib.stagegargoylenight import StageGargoyleNight
from wolflib import stageGuardNightBGM, stageGuardNightVoice, stageGuardNightEnding
from wolflib.gamemanager import GameManager

class StageGuardNight():
    def __init__(self, gm):
        self.parent = None
        self.running = True
        
        self.stageCompleted = False

        self.bgmRepeat = True
        self.bgm = stageGuardNightBGM
        self.voice = stageGuardNightVoice
        self.ending = stageGuardNightEnding
        
        # get gamemanager from previous stage
        self.gamemanager = gm
        # the guards who are alive
        self.aliveGuardList = []
        for seatNo in self.gamemanager.role2seatNoList(u'守卫'):
            if self.gamemanager.isAlive(seatNo):
                self.aliveGuardList.append(seatNo)
        
    def isSkipped(self):
        if self.gamemanager.N_GUARD == 0:
            return True
        else:
            return False
    
    def isWithoutAction(self):
        # the stage needs no action if no living roles
        if len(self.aliveGuardList) == 0:
            return True
        else:
            return False
            
    def get_sleepTimeBounds(self):
        return (5.0, 15.0)
        
    def get_msgIntroList(self):
        msgIntroList = []
        if self.isWithoutAction():
            return msgIntroList
        # 告知守卫如何守人
        for seatNo in self.aliveGuardList:
            msgIntroList.append({'ToUserName': self.gamemanager.getUserName(seatNo),
                                 'Text': u'请输入守护的号码，输入0则空守：' })
        return msgIntroList

    def msgVerify(self, msg):
        fromSeatNo = self.gamemanager.userName2seatNo(msg['FromUserName'])
        # if fromUserName not in game
        if fromSeatNo is None:
            return False
        if fromSeatNo not in self.aliveGuardList:
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
        if (mSeatNo != 0) and (mSeatNo == self.gamemanager.guardLastNight):
            if mSeatNo in self.aliveGuardList:
                msgReplyList.append({'ToUserName': fromUserName,
                                     'Text': u'昨晚已守护自己，不能连续两晚守护同一玩家，输入无效' })
            else:
                msgReplyList.append({'ToUserName': fromUserName,
                                     'Text': u'昨晚已守护%d号玩家，不能连续两晚守护同一玩家，输入无效' % mSeatNo })
            return msgReplyList
        # now handle
        self.gamemanager.guardSave = mSeatNo
        if mSeatNo == 0:
            msgReplyList.append({'ToUserName': fromUserName,
                                 'Text': u'你没有守护任何玩家' })
        elif mSeatNo in self.aliveGuardList:
            msgReplyList.append({'ToUserName': fromUserName,
                                 'Text': u'你守护了自己' })
        else:
            msgReplyList.append({'ToUserName': fromUserName,
                                 'Text': u'你守护了%d号玩家' % mSeatNo })
        self.stageCompleted = True
        return msgReplyList
        
    def enterNextStage(self):
        self.running = False
        self.parent.nextStage = StageGargoyleNight(self.gamemanager)
        self.parent.set_active_stage(self.parent.nextStage)
        if self.parent.nextStage.isSkipped():
            self.parent.nextStage.enterNextStage()
