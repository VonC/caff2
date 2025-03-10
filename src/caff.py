import pyautogui
import time
import sys
from datetime import datetime

pyautogui.FAILSAFE = False
numMin = None
if (len(sys.argv) < 2) or sys.argv[1].isalpha() or int(sys.argv[1]) < 1:
    numMin = 3
else:
    numMin = int(sys.argv[1])
while True:
    x = 0
    while x < numMin:
        time.sleep(60)
        x += 1
    # Get current mouse position
    current_x, current_y = pyautogui.position()

    # Make small movements relative to current position
    for i in range(0, 10):
        pyautogui.moveTo(0, i * 4)

    # Return to a position close to the original
    pyautogui.moveTo(current_x + 1, current_y + 1)

    for i in range(0, 3):
        pyautogui.press("shift")
    print("Movement made at {}".format(datetime.now().time()))
