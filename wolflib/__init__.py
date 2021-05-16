import os
import pygame

from .dictmapper import DictMapper

#SETTINGS

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(path, "data")
sound_path = os.path.join(data_path, "sounds")

rules = DictMapper()
rules.load(os.path.join(data_path, "rules.json"))

__VERSION__ = rules["VERSION"]

pygame.mixer.init()

def get_sound(fileName):
    filePath = os.path.join(sound_path, fileName)
    return pygame.mixer.Sound(filePath)

# stagePrepare
stagePrepareBGM = get_sound("prepareBGM.wav")
stagePrepareVoice = get_sound("prepareVoice.wav")
stagePrepareEnding = get_sound("prepareEnding.wav")

# stageWolfNight
stageWolfNightBGM = get_sound("wolfNightBGM.wav")
stageWolfNightVoice = get_sound("wolfNightVoice.wav")
stageWolfNightEnding = get_sound("wolfNightEnding.wav")

# stageDemonNight
stageDemonNightBGM = get_sound("demonNightBGM.wav")
stageDemonNightVoice = get_sound("demonNightVoice.wav")
stageDemonNightEnding = get_sound("demonNightEnding.wav")

# stageSeerNight
stageSeerNightBGM = get_sound("seerNightBGM.wav")
stageSeerNightVoice = get_sound("seerNightVoice.wav")
stageSeerNightEnding = get_sound("seerNightEnding.wav")

# stageWitchNight
stageWitchNightBGM = get_sound("witchNightBGM.wav")
stageWitchNightVoice = get_sound("witchNightVoice.wav")
stageWitchNightEnding = get_sound("witchNightEnding.wav")

# stageGuardNight
stageGuardNightBGM = get_sound("guardNightBGM.wav")
stageGuardNightVoice = get_sound("guardNightVoice.wav")
stageGuardNightEnding = get_sound("guardNightEnding.wav")

# stageHunterNight
stageHunterNightBGM = get_sound("hunterNightBGM.wav")
stageHunterNightVoice = get_sound("hunterNightVoice.wav")
stageHunterNightEnding = get_sound("hunterNightEnding.wav")

# stageGargoyleNight
stageGargoyleNightBGM = get_sound("seerNightBGM.wav")
stageGargoyleNightVoice = get_sound("gargoyleNightVoice.wav")
stageGargoyleNightEnding = get_sound("gargoyleNightEnding.wav")

# stageFirstDaytime
stageFirstDaytimeBGM = get_sound("firstDaytimeBGM.wav")
stageFirstDaytimeVoice = get_sound("firstDaytimeVoice.wav")
stageFirstDaytimeEnding = None