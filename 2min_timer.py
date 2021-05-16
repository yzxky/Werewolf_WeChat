import sys
import time
import os

import winsound

freq = 440
   
for n in range(120,0,-1):
	if n == 30:
		winsound.Beep(freq, 500)
	if n <= 10:
		winsound.Beep(freq, 100)
	if n//60 > 0:
		print(n//60,':',end='',sep='')
		if n%60 < 10:
			print('0',end='',sep='')
	print(n%60)
	time.sleep(1)

print('0')
winsound.Beep(freq, 1500)