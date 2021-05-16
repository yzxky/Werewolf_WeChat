#-*- coding:utf-8 -*-

import re

from wolflib.stageguardnight import StageGuardNight
from wolflib import stageWitchNightBGM, stageWitchNightVoice, stageWitchNightEnding
from wolflib.gamemanager import GameManager

class StageWitchNight():
    def __init__(self, gm):
        self.parent = None
        self.running = True
        
        self.stageCompleted = False

        self.bgmRepeat = True
        self.bgm = stageWitchNightBGM
        self.voice = stageWitchNightVoice
        self.ending = stageWitchNightEnding
        
        # get gamemanager from previous stage
        self.gamemanager = gm
        # the witches who are alive
        self.aliveWitchList = []
        for seatNo in self.gamemanager.role2seatNoList(u'女巫'):
            if self.gamemanager.isAlive(seatNo):
                self.aliveWitchList.append(seatNo)
        
        # witch needs two messages
        self.receivingSaveMSG = False
        self.receivingKillMSG = False
        
    def isSkipped(self):
        if self.gamemanager.N_WITCH == 0:
            return True
        else:
            return False
    
    def isWithoutAction(self):
        # the stage needs no action if no living roles
        if len(self.aliveWitchList) == 0:
            return True
        if (not self.receivingSaveMSG) and (not self.receivingKillMSG):
            return True
        return False
            
    def get_sleepTimeBounds(self):
        return (5.0, 15.0)
        
    def get_msgIntroList(self):
        msgIntroList = []
        # 告知女巫如何救人
        for seatNo in self.aliveWitchList:
            if not self.gamemanager.witchSaveUsed:
                kill = self.gamemanager.wolfNightKill
                if kill == 0:
                    if not self.gamemanager.witchKillUsed:
                        text = u'今晚没有玩家中刀。请输入毒药使用对象的号码，0则不使用：'
                        self.receivingKillMSG = True
                    else:
                        text = u'今晚没有玩家中刀。毒药已使用。请等待回合自动结束。'
                elif kill in self.aliveWitchList:
                    if self.gamemanager.WITCH_SELF_SAVE_ALWAYS or \
                       (self.gamemanager.WITCH_SELF_SAVE_FIRST_NIGHT_ONLY and (self.gamemanager.round == 1)):
                        text = u'今晚你自己中刀，输入1使用解药，0则不使用：'
                        self.receivingSaveMSG = True
                    else:
                        if not self.gamemanager.witchKillUsed:
                            text = u'今晚你自己中刀，你不能自救。请输入毒药使用对象的号码，0则不使用：'
                            self.receivingKillMSG = True
                        else:
                            text = u'今晚你自己中刀，你不能自救。毒药已使用。请等待回合自动结束。'
                else:
                    text = u'今晚%d号玩家中刀，输入1使用解药，0则不使用：' % kill
                    self.receivingSaveMSG = True
            else:
                if not self.gamemanager.witchKillUsed:
                    text = u'解药已使用。请输入毒药使用对象的号码，0则不使用：'
                    self.receivingKillMSG = True
                else:
                    text = u'解药已使用。毒药已使用。请等待回合自动结束。'
            msgIntroList.append({'ToUserName': self.gamemanager.getUserName(seatNo),
                                 'Text': text })                         
        return msgIntroList

    def msgVerify(self, msg):
        fromSeatNo = self.gamemanager.userName2seatNo(msg['FromUserName'])
        # if fromUserName not in game
        if fromSeatNo is None:
            return False
        if fromSeatNo not in self.aliveWitchList:
            if not self.gamemanager.SOLO_DEBUG:
                return False
        return True
        
    def msgHandle(self, msg):
        msgReplyList = []
        fromUserName = msg['FromUserName']
        if self.receivingSaveMSG:
            m = re.search(u'^([01])$', msg['Text'])
            if m is None: 
                msgReplyList.append({'ToUserName': fromUserName,
                                     'Text': u'输入无效，请输入0或1' })
                return msgReplyList
            mSave = bool(int(m.group(1)))
            # now handle
            if mSave:
                msgReplyList.append({'ToUserName': fromUserName,
                                     'Text': u'你使用了解药' })
                self.gamemanager.witchSaveTonight = True
                self.gamemanager.witchSaveUsed = True
                self.stageCompleted = True
                return msgReplyList
            else:
                msgReplyList.append({'ToUserName': fromUserName,
                                     'Text': u'你保留了解药。请输入毒药使用对象的号码，0则不使用：' })
                self.receivingSaveMSG = False
                self.receivingKillMSG = True
                return msgReplyList
        if self.receivingKillMSG:
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
            self.gamemanager.witchKill = mSeatNo
            if mSeatNo == 0:
                msgReplyList.append({'ToUserName': fromUserName,
                                     'Text': u'你保留了毒药' })
            else:
                msgReplyList.append({'ToUserName': fromUserName,
                                     'Text': u'你对%d号玩家使用了毒药' % mSeatNo })
                self.gamemanager.witchKillUsed = True
            self.stageCompleted = True
            return msgReplyList
        return msgReplyList
        
    def enterNextStage(self):
        self.running = False
        self.parent.nextStage = StageGuardNight(self.gamemanager)
        self.parent.set_active_stage(self.parent.nextStage)
        if self.parent.nextStage.isSkipped():
            self.parent.nextStage.enterNextStage()
