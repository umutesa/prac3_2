  
# Import libraries
from ES2EEPROMUtils import ES2EEPROM
from gpiozero import PWMLED, Buzzer, LED
import os
import random
import RPi.GPIO as GPIO
import time

# Global Variables
end_of_game = None  
Accuracy = None
Buz = None
eeprom = None
Menu = False
submit = False
answer = 0
counter = 0
GameScore = 0
scores = []
name = ""

# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzer = 33



# Print the game banner
def welcome():
    os.system('clear')
    print("  _   _                 _                  _____ _            __  __ _")
    print("| \ | |               | |                / ____| |          / _|/ _| |")
    print("|  \| |_   _ _ __ ___ | |__   ___ _ __  | (___ | |__  _   _| |_| |_| | ___ ")
    print("| . ` | | | | '_ ` _ \| '_ \ / _ \ '__|  \___ \| '_ \| | | |  _|  _| |/ _ \\")
    print("| |\  | |_| | | | | | | |_) |  __/ |     ____) | | | | |_| | | | | | |  __/")
    print("|_| \_|\__,_|_| |_| |_|_.__/ \___|_|    |_____/|_| |_|\__,_|_| |_| |_|\___|")
    print("")
    print("Guess the number and immortalise your name in the High Score Hall of Fame!")


# Print the game menu
def menu():
    global end_of_game, answer
    option = input("Select an option:   H - View High Scores     P - Play Game       Q - Quit\n")
    option = option.upper()
    if option == "H":
        os.system('clear')
        print("HIGH SCORES!!")
        s_count, ss = fetch_scores()
        display_scores(s_count, ss)
    elif option == "P":
        os.system('clear')
        print("Starting a new round!")
        print("Use the buttons on the Pi to make and submit your guess!")
        print("Press and hold the guess button to cancel your game")
        answer = generate_number()
        Menu = False
        print(answer)
        while not end_of_game:
            trigger_buzzer()
            pass
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")


def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    print("There are {} scores. Here are the top 3!".format(count))
    index = 1
    for score in raw_data:
        print("{} - {} took {} guesses".format(index, score[0], score[1]))
        index += 1
    # print out the scores in the required format
    pass


# Setup Pins
def setup():
    # Setup board mode
    global Buz, Accuracy, eeprom, Menu, name
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    eeprom = ES2EEPROM()

    # Reset Variables
    GameScore = 0
    name = ""

    # Setup LED GPIO
    GPIO.setup(LED_value[0], GPIO.OUT)
    GPIO.setup(LED_value[1], GPIO.OUT)
    GPIO.setup(LED_value[2], GPIO.OUT)
    GPIO.setup(LED_accuracy, GPIO.OUT)

    GPIO.output(LED_value[0], GPIO.LOW)
    GPIO.output(LED_value[1], GPIO.LOW)
    GPIO.output(LED_value[2], GPIO.LOW)
    GPIO.output(LED_accuracy, GPIO.LOW)
    
    GPIO.setup(buzzer, GPIO.OUT)

    # Setup PWM channels
    if Buz is None:
        Buz = GPIO.PWM(buzzer,1000)

    if Accuracy is None:
        Accuracy = GPIO.PWM(LED_accuracy, 50)
    
    #PWM Duty Cycle 
    Buz.start(0)
    Accuracy.start(0)

    # Setup debouncing and callbacks
    GPIO.setup(btn_increase, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(btn_submit, GPIO.IN,  pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(btn_increase, GPIO.FALLING, callback=btn_increase_pressed, bouncetime=500)  
    GPIO.add_event_detect(btn_submit, GPIO.FALLING, callback=btn_guess_pressed, bouncetime=500)
    pass


# Load high scores
def fetch_scores():
    global eeprom
    tscores = []
    
    #Retrieve High Scores
    scores = ES2EEPROM.read_block(eeprom,0,13) 
    score_count = scores[0]
    tname = ""

    # Ascii Conversion
    for i in range(1,len(scores)):
        if (i)%4 == 0:
            tscores.append([tname, scores[i]])
            tname = ""
        else:
            tname += chr(scores[i])

    scores = tscores

    # Return Results
    return score_count, scores

# Save high scores
def save_scores():
    global GameScore, eeprom, name
    s_count, ss = fetch_scores()
    s_count += 1 # add one to score count

    # include new score
    # sort
    # update total amount of scores
    # write new scores

    ss.append([name, GameScore])
    ss.sort(key=lambda x: x[1])

    data_to_write = []
    data_to_write.append(s_count)

    for score in ss[0:3]:
        for letter in score[0]:
            data_to_write.append(ord(letter))
        data_to_write.append(score[1])
    ES2EEPROM.write_block(eeprom, 0, data_to_write)
    pass


# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)


# Increase button pressed
def btn_increase_pressed(channel):
    # Increase the value shown on the LEDs
    # You can choose to have a global variable store the user's current guess, 
    # or just pull the value off the LEDs when a user makes a guess

    global counter
    ButtonState = GPIO.input(btn_increase)

    #Check & Increase Guess Value
    if ButtonState == 0:
        if counter == 7:
            counter = 0
        else:
            counter += 1
    
    #Display Guess Value on LEDs
    if counter == 0:
        GPIO.output(LED_value[0], GPIO.LOW)
        GPIO.output(LED_value[1], GPIO.LOW)
        GPIO.output(LED_value[2], GPIO.LOW)
    elif counter == 1:
        GPIO.output(LED_value[0], GPIO.LOW)
        GPIO.output(LED_value[1], GPIO.LOW)
        GPIO.output(LED_value[2], GPIO.HIGH)
    elif counter == 2:
        GPIO.output(LED_value[0], GPIO.LOW)
        GPIO.output(LED_value[1], GPIO.HIGH)
        GPIO.output(LED_value[2], GPIO.LOW)
    elif counter == 3:
        GPIO.output(LED_value[0], GPIO.LOW)
        GPIO.output(LED_value[1], GPIO.HIGH)
        GPIO.output(LED_value[2], GPIO.HIGH)
    elif counter == 4:
        GPIO.output(LED_value[0], GPIO.HIGH)
        GPIO.output(LED_value[1], GPIO.LOW)
        GPIO.output(LED_value[2], GPIO.LOW)
    elif counter == 5:
        GPIO.output(LED_value[0], GPIO.HIGH)
        GPIO.output(LED_value[1], GPIO.LOW)
        GPIO.output(LED_value[2], GPIO.HIGH)
    elif counter == 6:
        GPIO.output(LED_value[0], GPIO.HIGH)
        GPIO.output(LED_value[1], GPIO.HIGH)
        GPIO.output(LED_value[2], GPIO.LOW)
    elif counter == 7:
        GPIO.output(LED_value[0], GPIO.HIGH)
        GPIO.output(LED_value[1], GPIO.HIGH)
        GPIO.output(LED_value[2], GPIO.HIGH)
    pass


# Guess button
def btn_guess_pressed(channel):
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    # Compare the actual value with the user value displayed on the LEDs
    # Change the PWM LED
    # if it's close enough, adjust the buzzer
    # if it's an exact guess:
    # - Disable LEDs and Buzzer
    # - tell the user and prompt them for a name
    # - fetch all the scores
    # - add the new score
    # - sort the scores
    # - Store the scores back to the EEPROM, being sure to update the score count

    #Variables
    global counter, answer, submit, Menu, GameScore, end_of_game, name
    start = time.time()
    submit = True

    # Return to Menu
    while GPIO.input(btn_submit) == GPIO.LOW:
        time.sleep(0.01)
        length = time.time() - start

        #Checks Button Has Been Held
        if length > 1:
            print("Returning to Menu")
            Menu = True
            off()
            GPIO.remove_event_detect(btn_increase)
            GPIO.remove_event_detect(btn_submit)
            setup()
            welcome()
            menu()
            break
            
    
    print("Your guess was ", counter)
    print("The answer was ", answer)

    # Compare Guess to Answer
    if counter != answer and not Menu:
        accuracy_leds()
        trigger_buzzer()
        GameScore+=1
    elif counter == answer and not Menu:
        # if it's an exact guess:
        # - Disable LEDs and Buzzer
        # - tell the user and prompt them for a name
        # - fetch all the scores
        # - add the new score
        # - sort the scores
        # - Store the scores back to the EEPROM, being sure to update the score count
        off()
        name = input("YOURE AMAZING, enter your name:\n")
        name = name.upper()

        while not end_of_game:
            if len(name) < 3:
                name = input("Name must contail at least 3 letters:\n")
                name = name.upper()
            else:
                name = name[0:3]
                save_scores()
                end_of_game = True
    pass

def off():
    GPIO.output(LED_value[0], GPIO.LOW)
    GPIO.output(LED_value[1], GPIO.LOW)
    GPIO.output(LED_value[2], GPIO.LOW)
    GPIO.output(LED_accuracy, GPIO.LOW)
    GPIO.output(buzzer, GPIO.LOW)

# LED Brightness
def accuracy_leds():
    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
    global Accuracy, submit, answer, counter
    Brightness = 0

    if (counter < answer) and (submit == True):
        Brightness = (counter/answer)*100
        Accuracy.start(Brightness)
    elif (counter > answer) and (submit == True):
        Brightness = ((8-counter)/(8-answer))*100
        Accuracy.start(Brightness)


    pass

# Sound Buzzer
def trigger_buzzer():
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    global buzzer, submit, answer, counter
    offset = abs(answer-counter)

    if (offset == 1) and (submit == True):
        GPIO.output(buzzer, GPIO.HIGH)
        time.sleep(0.25)
        GPIO.output(buzzer, GPIO.LOW)
    elif (offset == 2) and (submit == True):
        GPIO.output(buzzer, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(buzzer, GPIO.LOW)
    elif (offset == 3) and (submit == True):
        GPIO.output(buzzer, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(buzzer, GPIO.LOW)
    else:
        GPIO.output(buzzer, GPIO.LOW)

    pass


if __name__ == "__main__":
    try:
        # Call setup function
        setup()
        welcome()
        while True:
            menu()
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()