#-*- coding:utf-8 -*-

import re

from wolflib.stageguardnight import StageGuardNight
from wolflib import stagePrepareBGM, stagePrepareVoice, stagePrepareEnding
from wolflib.gamemanager import GameManager

class StagePrepare():
    def __init__(self):
        self.parent = None
        self.running = True
        
        self.stageCompleted = False

        self.bgmRepeat = True
        self.bgm = stagePrepareBGM
        self.voice = stagePrepareVoice
        self.ending = stagePrepareEnding
        
        #Create gamemanager
        self.gamemanager = GameManager()
        self.emptySeats = self.gamemanager.N_TOTAL
        
    def playBGM(self):
        # since this is the first stage, need to play sounds manually
        import pygame
        pygame.mixer.init()
        self.bgm.play(-1)
        self.voice.play()

    def msgVerify(self, msg):
        # 我要玩x号
        m = re.search(u'^我要玩([0-9]+)号$', msg['Text'])
        if m is None: return False
        else: return True
        
    def msgHandle(self, msg):
        msgReplyList = []
        fromUserName = msg['FromUserName']
        m = re.search(u'^我要玩([0-9]+)号$', msg['Text'])
        mSeatNo = int(m.group(1))
        # check errors
        if mSeatNo > self.gamemanager.N_TOTAL:
            msgReplyList.append({'ToUserName': fromUserName,
                              'Text': u'您输入的号码%d大于游戏人数%d人，输入无效' % (mSeatNo, self.gamemanager.N_TOTAL) })
            return msgReplyList
        if mSeatNo == 0:
            msgReplyList.append({'ToUserName': fromUserName,
                                 'Text': u'开启单人调试模式（若误入请重启游戏）' })
            self.gamemanager.SOLO_DEBUG = True
            return msgReplyList
        if (not self.gamemanager.SOLO_DEBUG) and (self.gamemanager.userName2seatNo(fromUserName) is not None):
            uSeatNo = self.gamemanager.userName2seatNo(fromUserName)
            msgReplyList.append({'ToUserName': fromUserName,
                                 'Text': u'您已在%d号坐下，%s' % (uSeatNo, \
                                         u'输入无效' if mSeatNo != uSeatNo else \
                                         (u'身份是%s' % self.gamemanager.getRole(uSeatNo)) ) })
            return msgReplyList
        if not self.gamemanager.isEmpty(mSeatNo):
            msgReplyList.append({'ToUserName': fromUserName,
                                 'Text': u'%d号已被%s占用，输入无效' % (mSeatNo, self.gamemanager.getNickName(mSeatNo)) })
            return msgReplyList
        # now handle
        self.gamemanager.setName(fromUserName, mSeatNo)
        msgReplyList.append({'ToUserName': fromUserName,
                             'Text': u'您已在%d号坐下，身份是%s' % (mSeatNo, self.gamemanager.getRole(mSeatNo)) })
        self.emptySeats -= 1
        if self.emptySeats == 0:
            # 发放座位表
            seatTable = u'座位表：\n'
            for seatNo in range(1, self.gamemanager.N_TOTAL+1):
                seatTable += u'%d %s\n' % (seatNo, self.gamemanager.getNickName(seatNo))
            for seatNo in range(1, self.gamemanager.N_TOTAL+1):
                msgReplyList.append({'ToUserName': self.gamemanager.getUserName(seatNo),
                                     'Text': seatTable })
            self.stageCompleted = True
        return msgReplyList
        
    def enterNextStage(self):
        self.running = False
        self.parent.nextStage = StageGuardNight(self.gamemanager)
        self.parent.set_active_stage(self.parent.nextStage)
        if self.parent.nextStage.isSkipped():
            self.parent.nextStage.enterNextStage()

