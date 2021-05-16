#!/usr/bin/env python
#-*- coding:utf-8 -*-
import os
import time
import pygame
import itchat

from wolflib.stageprepare import StagePrepare

DEBUG = False

pygame.mixer.init()

class WolfGamePygame:
    def __init__(self):
        """Init game"""
        self.activeStage = None
        self.nextStage = None
        self.hostUserName = None

    def set_active_stage(self, activestage):
        self.activeStage = activestage
        self.activeStage.parent = self

    def msgVerify(self, msg):
        return self.activeStage.msgVerify(msg)

    def msgHandle(self, msg):
        return self.activeStage.msgHandle(msg)

    def enterNextStage(self):
        self.activeStage.enterNextStage()

    def run(self):
        """
            Run game. Remove lock when error
        """
        try:
            self.main()
        except Exception:
            import traceback
            traceback.print_exc()
            self.remove_game_lock()
            pygame.mixer.stop()
            itchat.logout()
            exit(1)

    def check_game_lock(self):
        if os.path.isfile("game.lock"):
            print("Game is already running. If not manualy"\
                " remove game.lock file and try again")
            exit(0)
        else:
            open("game.lock", "w").close()

    def remove_game_lock(self):
        if os.path.isfile("game.lock"):
            os.remove("game.lock")

    def main(self):
        """Main"""
        #check for lock file
        self.check_game_lock()
        
        itchat.auto_login(hotReload=True)
        
        # stagePrepare is the first stage, need to play sounds manually
        self.activeStage.playBGM()
        
        # store the host's information, host sends msg to filehelper
        self.hostUserName = itchat.search_friends()['UserName']
        
        # kind of a main loop, triggered by messages
        @itchat.msg_register(itchat.content.TEXT)
        def _(msg):
            # filter
            if not self.msgVerify(msg): 
                if DEBUG:
                    print("blocked msg %s from %s" % (msg['Text'],msg['FromUserName']))
                return
            # handle
            msgReplyList = self.msgHandle(msg)
            # reply
            for msgReply in msgReplyList:
                if DEBUG:
                    itchat.send("send %s to %s"%(msgReply['Text'],msgReply['ToUserName']), 'filehelper')
                else:
                    itchat.send(msgReply['Text'], 
                                msgReply['ToUserName'] if (msgReply['ToUserName'] != self.hostUserName) \
                                else 'filehelper')
                time.sleep(.5)
            # in msgHandle(msg), if everything in a stage completed, stageCompleted turns to True
            if self.activeStage.stageCompleted:
                enteringNextStageWithoutAction = True 
                # if a stage needs no action (e.g. has no living roles), 
                # then need to enteringNextStageWithoutAction
                while enteringNextStageWithoutAction:
                    # play the ending voice
                    ending = self.activeStage.ending
                    bgm = self.activeStage.bgm
                    if ending is not None:
                        ending.play()
                        if bgm is not None:
                            bgm.fadeout(int(ending.get_length()*1000))
                        time.sleep(ending.get_length())
                    else: 
                        if bgm is not None:
                            bgm.stop()
                    # enter the next stage, activeStage changes here
                    self.enterNextStage()
                    if self.activeStage is None:
                        self.remove_game_lock()
                        pygame.mixer.stop()
                        itchat.logout()
                        import sys
                        sys.exit("All stages completed. Exit.")
                    # play the new bgm and starting voice
                    bgm = self.activeStage.bgm
                    voice = self.activeStage.voice
                    if bgm is not None:
                        if self.activeStage.bgmRepeat:
                            bgm.play(-1)
                        else:
                            bgm.play()
                    if voice is not None:
                        voice.play()
                        time.sleep(voice.get_length()*0.5)
                    # send introduction
                    msgIntroList = self.activeStage.get_msgIntroList()
                    for msgIntro in msgIntroList:
                        if DEBUG:
                            itchat.send("send %s to %s"%(msgIntro['Text'],msgIntro['ToUserName']), 'filehelper')
                        else:
                            itchat.send(msgIntro['Text'], 
                                        msgIntro['ToUserName'] if (msgIntro['ToUserName'] != self.hostUserName) \
                                        else 'filehelper')
                        time.sleep(.5)
                    # if no action is needed in this stage
                    if self.activeStage.isWithoutAction():
                        lower, upper = self.activeStage.get_sleepTimeBounds()
                        # sleep for some random time
                        import random
                        someRandomTime = random.uniform(lower, upper)
                        time.sleep(someRandomTime)
                        self.activeStage.stageCompleted = True
                        enteringNextStageWithoutAction = True
                    else:
                        enteringNextStageWithoutAction = False

        itchat.run()

        #remove lock
        self.remove_game_lock()

if __name__ == '__main__':
    f = WolfGamePygame()
    f.set_active_stage(StagePrepare())
    f.run()