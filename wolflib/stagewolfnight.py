#-*- coding:utf-8 -*-

import re
from collections import Counter

from wolflib.stagedemonnight import StageDemonNight
from wolflib import stageWolfNightBGM, stageWolfNightVoice, stageWolfNightEnding
from wolflib.gamemanager import GameManager

class StageWolfNight():
    def __init__(self, gm):
        self.parent = None
        self.running = True
        
        self.stageCompleted = False

        self.bgmRepeat = True
        self.bgm = stageWolfNightBGM
        self.voice = stageWolfNightVoice
        self.ending = stageWolfNightEnding
        
        # get gamemanager from previous stage
        self.gamemanager = gm
        # the wolfs and bads who are alive
        self.aliveBadList = []
        # number of wolfs and bads who haven't voted the kill
        self.waitingBads = 0
        for seatNo in self.gamemanager.getBadList():
            if self.gamemanager.isAlive(seatNo):
                self.aliveBadList.append(seatNo)
                self.waitingBads += 1
        # the votes
        self.votes = {}
        
    def isSkipped(self):
        if self.gamemanager.N_WOLF == 0 and \
           self.gamemanager.N_WHITEWOLFKING == 0 and \
           self.gamemanager.N_DEMON == 0:
            return True
        else:
            return False
    
    def isWithoutAction(self):
        # the stage needs no action if no living roles
        if self.waitingBads == 0:
            return True
        else:
            return False
            
    def get_sleepTimeBounds(self):
        return (5.0, 15.0)
        
    def get_msgIntroList(self):
        msgIntroList = []
        if self.isWithoutAction():
            return msgIntroList
        # 发放座位表
        seatTable = u'狼人座位表：\n'
        for seatNo in self.aliveBadList:
            seatTable += u'%d %s\n' % (seatNo, self.gamemanager.getRole(seatNo))
        for seatNo in self.aliveBadList:
            msgIntroList.append({'ToUserName': self.gamemanager.getUserName(seatNo),
                                 'Text': seatTable })
        # 告知狼人如何刀人
        for seatNo in self.aliveBadList:
            msgIntroList.append({'ToUserName': self.gamemanager.getUserName(seatNo),
                                 'Text': u'每位狼人都需要输入刀人的号码（空刀输入0），平票则空刀。请输入号码：' })
        return msgIntroList

    def msgVerify(self, msg):
        fromSeatNo = self.gamemanager.userName2seatNo(msg['FromUserName'])
        # if fromUserName not in game
        if fromSeatNo is None:
            return False
        # if fromUserName is not among living wolfs or bads
        if fromSeatNo not in self.aliveBadList:
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
        fromSeatNo = self.gamemanager.userName2seatNo(fromUserName)
        if fromSeatNo not in self.votes:
            self.waitingBads -= 1
        else:
            if self.gamemanager.SOLO_DEBUG:
                self.waitingBads -= 1
        self.votes[fromSeatNo] = mSeatNo
        if mSeatNo == 0:
            msgReplyList.append({'ToUserName': fromUserName,
                                 'Text': u'您选择了空刀' })
        else:
            msgReplyList.append({'ToUserName': fromUserName,
                                 'Text': u'您选择了刀%d号玩家' % mSeatNo })
        if self.waitingBads == 0:
            # 统计
            values = Counter(self.votes.values())
            most_common_values = values.most_common(2)  # [(most_common_value, times), (2nd_value, times)]
            kill = most_common_values[0][0]
            # if votes split
            if len(most_common_values) > 1:
                if most_common_values[1][1] == most_common_values[0][1]:
                    kill = 0
            self.gamemanager.wolfNightKill = kill
            # 发放刀票结果
            seatTable = u'刀票结果：\n'
            for seatNo in self.aliveBadList:
                if self.gamemanager.SOLO_DEBUG:
                    seatNo = self.gamemanager.userName2seatNo(self.gamemanager.getUserName(seatNo))
                if self.votes[seatNo] == 0:
                    seatTable += u'%d号空刀\n' % seatNo
                else:
                    seatTable += u'%d号刀%d号\n' % (seatNo, self.votes[seatNo])
            if kill == 0:
                seatTable += u'最终结果：空刀'
            else:
                seatTable += u'最终结果：%d号中刀' % kill
            for seatNo in self.aliveBadList:
                msgReplyList.append({'ToUserName': self.gamemanager.getUserName(seatNo),
                                     'Text': seatTable })
            self.stageCompleted = True
        return msgReplyList
        
    def enterNextStage(self):
        self.running = False
        self.parent.nextStage = StageDemonNight(self.gamemanager)
        self.parent.set_active_stage(self.parent.nextStage)
        if self.parent.nextStage.isSkipped():
            self.parent.nextStage.enterNextStage()

