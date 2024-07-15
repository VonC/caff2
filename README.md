# Additional features 
- Allows clearer input from user for the number of minutes
- Uses threading to revert to default if value isn't entered in fast enough (e.g. if the user forgets to enter even after starting the program)
- Adds all actions into a txt file for analysis if required
- Allows stopping mechanism via escape button



# Stay-Awake
A small python script to move your mouse, press the shift key, and keep your PC awake when you're away
Uses command line arguments to set the number of minutes between movements and requires Python3 or higher.
Default timer is 3 minutes, but can be 1 or more. 

# Dependencies
This software uses PyAutoGui https://github.com/asweigart/pyautogui as the driver behind the movement. 
> Optional- Create Virtual Env Step: ``` python3 -m venv ./StayAwake ```
> ``` pip install -r requirements.txt  ```
