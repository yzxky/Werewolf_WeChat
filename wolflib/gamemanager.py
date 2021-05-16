#-*- coding:utf-8 -*-

import itchat

import wolflib

class GameManager:
    def __init__(self):
        # used in stageWolfNight msgHandle, and all msgVerify, can be turned on in stagePrepare by "我要玩0号"
        self.SOLO_DEBUG = False
        # get data from rules
        self.N_TOTAL            = wolflib.rules["N_TOTAL"]
        self.N_WOLF             = wolflib.rules["N_WOLF"]
        self.N_VILLAGER         = wolflib.rules["N_VILLAGER"]
        self.N_SEER             = wolflib.rules["N_SEER"]
        self.N_WITCH            = wolflib.rules["N_WITCH"]
        self.N_HUNTER           = wolflib.rules["N_HUNTER"]
        self.N_GUARD            = wolflib.rules["N_GUARD"]
        self.N_IDIOT            = wolflib.rules["N_IDIOT"]
        self.N_WHITEWOLFKING    = wolflib.rules["N_WHITEWOLFKING"]
        self.N_DEMON            = wolflib.rules["N_DEMON"]
        self.N_GARGOYLE         = wolflib.rules["N_GARGOYLE"]
        self.N_TOMBKEEPER       = wolflib.rules["N_TOMBKEEPER"]
        self.WITCH_SELF_SAVE_ALWAYS             = bool(wolflib.rules["WITCH_SELF_SAVE_ALWAYS"])
        self.WITCH_SELF_SAVE_FIRST_NIGHT_ONLY   = bool(wolflib.rules["WITCH_SELF_SAVE_FIRST_NIGHT_ONLY"])
        self.WITCH_GUARD_KILL                   = bool(wolflib.rules["WITCH_GUARD_KILL"])
        self.WEREWOLF_KNOW_HEADWOLF             = bool(wolflib.rules["WEREWOLF_KNOW_HEADWOLF"])
        # roles initialization
        self.roles = [""] * self.N_TOTAL
        i = 0
        for _ in range(self.N_WOLF):            self.roles[i] = u"普通狼人";    i += 1
        for _ in range(self.N_VILLAGER):        self.roles[i] = u"普通村民";    i += 1
        for _ in range(self.N_SEER):            self.roles[i] = u"预言家";      i += 1
        for _ in range(self.N_WITCH):           self.roles[i] = u"女巫";        i += 1
        for _ in range(self.N_HUNTER):          self.roles[i] = u"猎人";        i += 1
        for _ in range(self.N_GUARD):           self.roles[i] = u"守卫";        i += 1
        for _ in range(self.N_IDIOT):           self.roles[i] = u"白痴";        i += 1
        for _ in range(self.N_WHITEWOLFKING):   self.roles[i] = u"白狼王";      i += 1
        for _ in range(self.N_DEMON):           self.roles[i] = u"恶魔";        i += 1
        for _ in range(self.N_GARGOYLE):        self.roles[i] = u"石像鬼";      i += 1
        for _ in range(self.N_TOMBKEEPER):      self.roles[i] = u"守墓人";      i += 1
        
        import random
        random.shuffle(self.roles)
        self.roles.insert(0, u"没有身份")
        # role to seatNoList dictionary
        self.role2seatNoListDict = {}
        for seatNo in range(1, self.N_TOTAL+1):
            if self.roles[seatNo] not in self.role2seatNoListDict:
                self.role2seatNoListDict[self.roles[seatNo]] = [seatNo]
            else:
                self.role2seatNoListDict[self.roles[seatNo]].append(seatNo)
        # seatNoList for werewolves and bads
        self.badList = []
        for badRole in [u"普通狼人", u"白狼王", u"恶魔", u"石像鬼"]:
            if badRole in self.role2seatNoListDict:
                self.badList += self.role2seatNoListDict[badRole]
        # seatNoList for gods
        self.godList = []
        for godRole in [u"预言家", u"女巫", u"猎人", u"守卫", u"白痴", u"守墓人"]:
            if godRole in self.role2seatNoListDict:
                self.godList += self.role2seatNoListDict[godRole]
                
        # nickName and userName initialization
        self.nickName = [""] * (self.N_TOTAL+1)
        self.userName = [""] * (self.N_TOTAL+1)
        # userName to seatNo dictionary
        self.userName2seatNoDict = {}
        
        # status initialization
        self.alive = [True] * (self.N_TOTAL+1)
        # data in the game
        self.round = 1
        self.wolfNightKill = 0
        self.witchSaveUsed = False
        self.witchKillUsed = False
        self.witchSaveTonight = False
        self.witchKill = 0
        self.guardLastNight = 0
        self.guardSave = 0
        
    def setName(self, fromUserName, seatNo):
        self.userName[seatNo] = fromUserName
        self.nickName[seatNo] = itchat.search_friends(userName=fromUserName)['NickName']
        self.userName2seatNoDict[fromUserName] = seatNo
        
    def getRole(self, seatNo):
        return self.roles[seatNo]
        
    def isAlive(self, seatNo):
        return self.alive[seatNo]
    
    def leave(self, seatNo):
        if seatNo == 0:
            import sys
            sys.exit("In gamemanager.py, seatNo 0 is leaving. Check getOutList()")
        else:
            self.alive[seatNo] = False
        
    def isEmpty(self, seatNo):
        if self.userName[seatNo] == "": return True
        else: return False
        
    def getUserName(self, seatNo):
        return self.userName[seatNo]
        
    def getNickName(self, seatNo):
        return self.nickName[seatNo]
        
    def role2seatNoList(self, roleName):
        if roleName not in self.role2seatNoListDict:
            return []
        else:
            return self.role2seatNoListDict[roleName]
            
    def userName2seatNo(self, someUserName):
        if someUserName not in self.userName2seatNoDict:
            return None
        else:
            return self.userName2seatNoDict[someUserName]
            
    def getBadList(self):
        return self.badList
        
    def getGodList(self):
        return self.godList
    
    def getOutList(self):
        outList = []
        if (self.witchKill != 0) and (self.witchKill not in self.role2seatNoList(u"恶魔")):
            outList.append(self.witchKill)
        if (self.wolfNightKill != 0) and (self.wolfNightKill not in outList):
            if self.WITCH_GUARD_KILL:
                if (self.witchSaveTonight and (self.wolfNightKill == self.guardSave)) \
                or ((not self.witchSaveTonight) and (self.wolfNightKill != self.guardSave)):
                    outList.append(self.wolfNightKill)
            else:
                if ((not self.witchSaveTonight) and (self.wolfNightKill != self.guardSave)):
                    outList.append(self.wolfNightKill)
        for seatNo in outList:
            self.leave(seatNo)
        outList.sort()
        return outList
    
    def getModerator(self):
        text = u'玩家身份：\n'
        for seatNo in range(1, self.N_TOTAL+1):
            text += u'%d %s\n' % (seatNo, self.getRole(seatNo))
        if self.N_WITCH != 0:
            text += u'女巫%s使用解药\n' % (u"已经" if self.witchSaveUsed else u"还没有")
            if not self.witchKillUsed:
                text += u'女巫还没有使用毒药\n' 
            else:
                text += u'女巫已经对%d号玩家使用毒药\n' % self.witchKill
        if self.N_GUARD != 0:
            if self.guardSave == 0:
                text += u'守卫昨晚空守\n'
            else:
                text += u'守卫昨晚守护了%d号玩家\n' % self.guardSave
        return text
    
    def enterNextDay(self):
        pass

