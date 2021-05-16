#-*- coding:utf-8 -*-

import random

# from wolflib.stagewolfnight import StageWolfNight
from wolflib import stageFirstDaytimeBGM, stageFirstDaytimeVoice, stageFirstDaytimeEnding
from wolflib.gamemanager import GameManager

class StageFirstDaytime():
    def __init__(self, gm):
        self.parent = None
        self.running = True
        
        self.stageCompleted = False

        self.bgmRepeat = False
        self.bgm = stageFirstDaytimeBGM
        self.voice = stageFirstDaytimeVoice
        self.ending = stageFirstDaytimeEnding
        
        # get gamemanager from previous stage
        self.gamemanager = gm
        # the player list
        self.playerList = range(1, self.gamemanager.N_TOTAL+1)
        
        # several messages are needed in this stage 
        self.receivingRaiseOrder = False  # 接受警上“发言顺序”信息
        self.receivingResult = False      # 接受“昨夜信息”信息
        self.receivingModerator = False   # 接受“接管上帝”信息
        
    def isSkipped(self):
        return False
    
    def isWithoutAction(self):
        # the stage always needs action
        return False
            
    def get_sleepTimeBounds(self):
        pass
        
    def get_msgIntroList(self):
        msgIntroList = []
        # 告知所有玩家白天如何发送信息
        for seatNo in self.playerList:
            msgIntroList.append({'ToUserName': self.gamemanager.getUserName(seatNo),
                                 'Text': u'现在开始警长竞选。玩家举手后，请任意一名玩家输入“发言顺序”获得随机发言顺序' })
        self.receivingRaiseOrder = True
        return msgIntroList

    def msgVerify(self, msg):
        fromSeatNo = self.gamemanager.userName2seatNo(msg['FromUserName'])
        # if fromUserName not in game
        if fromSeatNo is None:
            return False
        else:
            return True
        
    def msgHandle(self, msg):
        msgReplyList = []
        fromUserName = msg['FromUserName']
        startSeatNo = random.randint(1, self.gamemanager.N_TOTAL)
        order = u'升序' if random.randint(0,1) else u'降序'
        m = msg['Text']
        if m == u'发言顺序':
            if not self.receivingRaiseOrder:
                msgReplyList.append({'ToUserName': fromUserName,
                                     'Text': u'已有玩家输入“发言顺序”' })
                return msgReplyList
            # now handle
            for seatNo in self.playerList:
                msgReplyList.append({'ToUserName': self.gamemanager.getUserName(seatNo),
                                     'Text': u'请从%d号玩家开始按照%s发言' % (startSeatNo, order) })
            for seatNo in self.playerList:
                msgReplyList.append({'ToUserName': self.gamemanager.getUserName(seatNo),
                                     'Text': u'警长竞选结束后，请任意一名玩家输入“昨夜信息”获得昨夜信息' })
            self.receivingRaiseOrder = False
            self.receivingResult = True
            return msgReplyList
        elif m == u'昨夜信息':
            if not self.receivingResult:
                if self.receivingRaiseOrder:
                    msgReplyList.append({'ToUserName': fromUserName,
                                         'Text': u'请先输入“发言顺序”' })
                    return msgReplyList
                else:
                    msgReplyList.append({'ToUserName': fromUserName,
                                         'Text': u'已有玩家输入“昨夜信息”' })
                    return msgReplyList
            # now handle
            outList = self.gamemanager.getOutList()
            if len(outList) == 0:
                for seatNo in self.playerList:
                    msgReplyList.append({'ToUserName': self.gamemanager.getUserName(seatNo),
                                         'Text': u'昨晚是平安夜' })
                for seatNo in self.playerList:
                    msgReplyList.append({'ToUserName': self.gamemanager.getUserName(seatNo),
                                         'Text': u'请警长指定从警左或警右开始发言。若本局游戏没有警长，请从%d号玩家开始按照%s发言' % (startSeatNo, order) })
            elif len(outList) == 1:
                for seatNo in self.playerList:
                    msgReplyList.append({'ToUserName': self.gamemanager.getUserName(seatNo),
                                         'Text': u'昨晚%d号玩家“死亡”，请发表“遗言”' % outList[0] })
                for seatNo in self.playerList:
                    msgReplyList.append({'ToUserName': self.gamemanager.getUserName(seatNo),
                                         'Text': u'“遗言”结束后，请警长指定从“死左”或“死右”开始发言。若本局游戏没有警长，请从%d号%s后的玩家开始发言' % (outList[0], order) })
            elif len(outList) > 1:
                startSeatNo = random.choice(outList)
                for seatNo in self.playerList:
                    msgReplyList.append({'ToUserName': self.gamemanager.getUserName(seatNo),
                                         'Text': u'昨晚%s玩家“死亡”，请从%d号玩家开始%s发表“遗言”' 
                                                 % (self.outList2str(outList), startSeatNo, 
                                                    "" if len(outList)==2 else order) })
                aliveList = []
                for seatNo in self.playerList:
                    if self.gamemanager.isAlive(seatNo):
                        aliveList.append(seatNo)
                if aliveList != []:
                    startSeatNo = random.choice(aliveList)
                order = u'升序' if random.randint(0,1) else u'降序'
                for seatNo in self.playerList:
                    msgReplyList.append({'ToUserName': self.gamemanager.getUserName(seatNo),
                                         'Text': u'“遗言”结束后，请警长指定从警左或警右开始发言。若本局游戏没有警长，请从%d号玩家开始按照%s发言' % (startSeatNo, order) })
            for seatNo in self.playerList:
                msgReplyList.append({'ToUserName': self.gamemanager.getUserName(seatNo),
                                     'Text': u'发言结束后，请自行投票推出怀疑的玩家。离开游戏的玩家可输入“接管上帝”' })
            self.receivingResult = False
            self.receivingModerator = True
            return msgReplyList
        elif m == u'接管上帝':
            if not self.receivingModerator:
                msgReplyList.append({'ToUserName': fromUserName,
                                     'Text': u'现在还不能接管上帝' })
                return msgReplyList
            # now handle
            msgReplyList.append({'ToUserName': fromUserName,
                                 'Text': self.gamemanager.getModerator() })
            for seatNo in self.playerList:
                msgReplyList.append({'ToUserName': self.gamemanager.getUserName(seatNo),
                                     'Text': u'%d号玩家已接管上帝' % self.gamemanager.userName2seatNo(fromUserName) })
            self.receivingModerator = False
            self.stageCompleted = True
            return msgReplyList
        msgReplyList.append({'ToUserName': fromUserName,
                             'Text': u'输入无效' })
        return msgReplyList
        
    def outList2str(self, outList):
        outStr = u'%d号' % outList[0]
        for seatNo in outList[1:]:
            outStr += u'、%d号' % seatNo
        return outStr
        
    def enterNextStage(self):
        self.running = False
        self.parent.activeStage = None
#        self.parent.nextStage = StageWolfNight(self.gamemanager)
#        self.parent.set_active_stage(self.parent.nextStage)
#        if self.parent.nextStage.isSkipped():
#            self.parent.nextStage.enterNextStage()
