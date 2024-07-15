import pyautogui ## for controlling mouse and keyboard
import time
import sys ## access command line arguments 
from datetime import datetime
import random
import os
import threading 
import msvcrt



## Failsafe -- prevent script from stopping once mouse moves to screen corner 
pyautogui.FAILSAFE = False 

## TWO WAYS OF SETTING THE TIME IN BETWEEN ACTIONS 
## M1: ====================================================================================
## Get durations from user :
def min_num():
    while True: 
        try:
            numMin = int(input('Enter number of minutes to wait between actions'))
            if numMin <1:
                print('Has to be more than 1')
                raise ValueError ## has to be more than 1 min 
            print(f'chosen duration: {numMin}')
            return numMin   
        except ValueError:
            print('Please enter an integer (e.g. not a string)')

## M2: ====================================================================================
## Create a dynamic function that takes 5 mins as default if the user didnt enter a value within
## a period of time 
## This is useful is the user runs the function and leaves the computer before entering in the integer
def timed_input(prompt, timeout = 60, default_duration = 5):
    '''
    Like the previous function that takes in an input from the user for duration between actions
    But if the user forgets to enter, which is a possibility, default to a random value 
    after a certain time has passed 
    '''
    print(prompt, end = '', flush=True) ## no extra line, and flush to output string to console immediately (to ensure that outputs appear as expected and no buffer - useful for threading)
    result = [None]
    def input_thread(): ## thread that take input and saves it from user 
        result[0] = input() 

    it = threading.Thread(target = input_thread)
    it.start() ## allow user input to run separately from main program 
    it.join(timeout) # JOIN: WAITS FOR THREAD TO FINISH (OR IF TOO LONG, TIMEOUT)

    ## Case when user doesnt enter fast enough 
    if it.is_alive(): ## check if thread is still alive 
        print(f'\nNo input was received before time limit, defaulting duration {default_duration}')
        it.join() ## ensures thread is finished despite timeout
        return default_duration
    else: 
        try:
            return(int(result[0])) ## try to integerise user input 
        except ValueError:
            print(f'Invalid input, using default value {default_duration}')
            return default_duration

## Random mouse movement 
def random_mouse_move():
    width, height = pyautogui.size() ## 1920 by 1080, i.e. screen resolution
    x = random.uniform(0, width)
    y = random.uniform(0, height)
    pyautogui.moveTo(x,y)
    return(x,y)

## Logging actions onto text file: 
def log_action(action_deets):
    with open('mouse moving and text typing.txt'.replace(' ', '_'), 'a') as log_file: ## a for append mode 
        log_file.write(f'{datetime.now()}: {action_deets}\n')

## Stopping the program 
def stop_mechanism():
    global stop_thread ##global variable outside of the function (top level of script)
    while True:
        if msvcrt.kbhit():
            char = msvcrt.getch()
            if char == chr(27): ## this is for escape key
                print('\nStopping mousemover')
                stop_thread = True
                break
        time.sleep(0.5)



## ============================

def main():
    global stop_thread
    stop_thread = False

    # Starting the stop mechanism in a separate thread
    stop_threading = threading.Thread(target=stop_mechanism)
    stop_threading.start()

    # Record the start time
    start_time = datetime.now()
    
    try:
        while not stop_thread:
            duration = timed_input("Enter the number of minutes to wait between actions (or press ESC to stop anytime): ", 60, 5)
            print(f"Waiting for {duration} minutes...")
            time.sleep(duration * 60)  # Converts minutes to seconds

            x, y = random_mouse_move()
            action_details = f"Mouse was moved to ({x:.2f}, {y:.2f})"
            log_action(action_details)
            print(f"Action logged at {datetime.now()}. Details: {action_details}")
        
    except KeyboardInterrupt:
        print("Program interrupted manually.")

    finally:
        # Calculate total runtime
        end_time = datetime.now()
        total_runtime = end_time - start_time
        print(f"Total runtime: {total_runtime}")

        # Ensure all threads are cleaned up before exiting
        stop_thread = True
        stop_threading.join()
        print("Program has been stopped.")

if __name__ == "__main__":
    main()
