#-*- coding:utf-8 -*-

from wolflib.stagefirstdaytime import StageFirstDaytime
# from wolflib.stagelaterdaytime import StageLaterDaytime
from wolflib import stageHunterNightBGM, stageHunterNightVoice, stageHunterNightEnding
from wolflib.gamemanager import GameManager

class StageHunterNight():
    def __init__(self, gm):
        self.parent = None
        self.running = True
        
        self.stageCompleted = False

        self.bgmRepeat = True
        self.bgm = stageHunterNightBGM
        self.voice = stageHunterNightVoice
        self.ending = stageHunterNightEnding
        
        # get gamemanager from previous stage
        self.gamemanager = gm
        # the hunters who are alive
        self.aliveHunterList = []
        for seatNo in self.gamemanager.role2seatNoList(u'猎人'):
            if self.gamemanager.isAlive(seatNo):
                self.aliveHunterList.append(seatNo)
        
    def isSkipped(self):
        if self.gamemanager.N_HUNTER == 0:
            return True
        else:
            return False
    
    def isWithoutAction(self):
        # the stage needs no action
        return True
            
    def get_sleepTimeBounds(self):
        return (7.0, 7.0)
        
    def get_msgIntroList(self):
        msgIntroList = []
        # 告知猎人信息
        for seatNo in self.aliveHunterList:
            if seatNo == self.gamemanager.witchKill:
                msgIntroList.append({'ToUserName': self.gamemanager.getUserName(seatNo),
                                     'Text': u'女巫对你使用了毒药，你不能开枪' })
            else:
                msgIntroList.append({'ToUserName': self.gamemanager.getUserName(seatNo),
                                     'Text': u'女巫没有对你使用毒药，你可以开枪' })
        return msgIntroList

    def msgVerify(self, msg):
        pass
        
    def msgHandle(self, msg):
        pass
        
    def enterNextStage(self):
        self.running = False
        if self.gamemanager.round == 1:
            self.parent.nextStage = StageFirstDaytime(self.gamemanager)
        else:
            #self.parent.nextStage = StageLaterDaytime(self.gamemanager)
            pass
        self.parent.set_active_stage(self.parent.nextStage)
        if self.parent.nextStage.isSkipped():
            self.parent.nextStage.enterNextStage()
