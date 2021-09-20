  
# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
import time

# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game
curr_guess = 0
num_guesses = 0
rand_num = 0
name = ""

# DEFINE THE PINS USED HERE
buzzer_pin = 23
led = [21, 20, 16]
LED_accuracy = 32
btn_submit = 24
btn_increase = 25
buzzer = None
led1 = None
led2 = None
led3 = None
eeprom = ES2EEPROMUtils.ES2EEPROM()


# Print the game banner
def welcome():
    os.system('clear')
    print(" _   _                 _                  _____ _            __  __ _")
    print("| \ | |               | |                / ____| |          / _|/ _| |")
    print("|  \| |_   _ _ __ ___ | |__   ___ _ __  | (___ | |__  _   _| |_| |_| | ___ ")
    print("| . ` | | | | '_ ` _ \| '_ \ / _ \ '__|  \___ \| '_ \| | | |  _|  _| |/ _ \\")
    print("| |\  | |_| | | | | | | |_) |  __/ |     ____) | | | | |_| | | | | | |  __/")
    print("|_| \_|\__,_|_| |_| |_|_.__/ \___|_|    |_____/|_| |_|\__,_|_| |_| |_|\___|")
    print("")
    print("Guess the number and immortalise your name in the High Score Hall of Fame!")


# Print the game menu
def menu():
    global end_of_game
    option = input("Select an option:   H - View High Scores     P - Play Game       Q - Quit\n")
    option = option.upper()
    if option == "H":
        os.system('clear')
        print("HIGH SCORES!!")
        s_count, ss = fetch_scores()
        display_scores(s_count, ss)
    elif option == "P":
        end_of_game = False
        os.system('clear')
        print("Starting a new round!")
        print("Use the buttons on the Pi to make and submit your guess!")
        print("Press and hold the guess button to cancel your game")
        value = generate_number()
        while end_of_game != True:
            pass
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")


def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    print("There are {} scores. Here are the top 3!".format(count))
    # put the top scores in order into the order array
    order = []
    for i in range(0, 3):
        lowest = 0
        for j in range(0, count):
            if(raw_data[j][1] < raw_data[lowest][1]):
                lowest = j
        order.append(raw_data[lowest])
        raw_data.pop(lowest)
        count-=1
    
    # print out high scores in the right format
    for i in range(0, 3):
        print(str(i+1) + " - "+ order[i][0] + " took " + str(order[i][1]) + " guesses")

# Setup Pins
def setup():
    global led1
    global led2
    global led3
    global buzzer
    global led
    global buzzer_pin
    global btn_submit
    global btn_increase
    # Setup board mode
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    # Setup regular GPIO
    GPIO.setup(led[0], GPIO.OUT)
    GPIO.setup(led[1], GPIO.OUT)
    GPIO.setup(led[2], GPIO.OUT)
    GPIO.setup(buzzer_pin, GPIO.OUT)
    GPIO.setup(btn_submit, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
    GPIO.setup(btn_increase, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
    # Setup PWM channels
    buzzer = GPIO.PWM(buzzer_pin, 0.1)
    led1 = GPIO.PWM(led[0], 50)
    led1.start(0)
    led2 = GPIO.PWM(led[1], 50)
    led2.start(0)
    led3 = GPIO.PWM(led[2], 50)
    led3.start(0)
    # Setup debouncing and callbacks
    GPIO.add_event_detect(btn_submit, GPIO.RISING, callback = btn_guess_pressed, bouncetime = 200)
    GPIO.add_event_detect(btn_increase, GPIO.RISING, callback = btn_increase_pressed, bouncetime = 200)


# Load high scores
def fetch_scores():
    # get however many scores there are
    score_count = eeprom.read_block(0, 4)[0]
    # Get the scores
    #eeprom.populate_mock_scores()
    scores_temp = []
    for i in range(0, score_count):
        scores_temp.append(eeprom.read_block(i+1, 4))
    
    # convert the codes back to ascii
    scores = []
    for i in range(0, score_count):
        name = ""
        for j in range(0, 3):
            name = name + chr(scores_temp[i][j])
        scores.append([name, scores_temp[i][3]])
    
    # return back the results
    return score_count, scores


# Save high scores
def save_scores():
    global name
    global eeprom
    global num_guesses
    # fetch scores
    # include new score
    # sort
    # update total amount of scores
    # write new scores
    
    # Fetch scores
    score_count, scores = fetch_scores()
    score_count+=1
    scores.append([name, num_guesses])
    
    # Sort the scores
    scores.sort(key=lambda x: x[1])
    
    # Write updated scores back to EEPROM
    data_to_write = []
    for score in scores:
        # get the string
        for letter in score[0]:
            data_to_write.append(ord(letter))
        data_to_write.append(score[1])
    eeprom.write_block(0, [score_count])
    eeprom.write_block(1, data_to_write) 


# Generate guess number
def generate_number():
    global rand_num
    rand_num = random.randint(0, pow(2, 3)-1)
    return rand_num


# Increase button pressed
def btn_increase_pressed(channel):
    global curr_guess
    global led1
    global led2
    global led3
    
    # Increment the guess
    curr_guess+=1
    # Increase the value shown on the LEDs
    if curr_guess == 0:
        led1.ChangeDutyCycle(0)
        led2.ChangeDutyCycle(0)
        led3.ChangeDutyCycle(0)
    elif curr_guess == 1:
        led1.ChangeDutyCycle(LED_accuracy)
        led2.ChangeDutyCycle(0)
        led3.ChangeDutyCycle(0)
    elif curr_guess == 2:
        led1.ChangeDutyCycle(0)
        led2.ChangeDutyCycle(LED_accuracy)
        led3.ChangeDutyCycle(0)
    elif curr_guess == 3:
        led1.ChangeDutyCycle(LED_accuracy)
        led2.ChangeDutyCycle(LED_accuracy)
        led3.ChangeDutyCycle(0)
    elif curr_guess == 4:
        led1.ChangeDutyCycle(0)
        led2.ChangeDutyCycle(0)
        led3.ChangeDutyCycle(LED_accuracy)
    elif curr_guess == 5:
        led1.ChangeDutyCycle(LED_accuracy)
        led2.ChangeDutyCycle(0)
        led3.ChangeDutyCycle(LED_accuracy)
    elif curr_guess == 6:
        led1.ChangeDutyCycle(0)
        led2.ChangeDutyCycle(LED_accuracy)
        led3.ChangeDutyCycle(LED_accuracy)
    elif curr_guess == 7:
        led1.ChangeDutyCycle(LED_accuracy)
        led2.ChangeDutyCycle(LED_accuracy)
        led3.ChangeDutyCycle(LED_accuracy)
    else:
        curr_guess = 0
        led1.ChangeDutyCycle(0)
        led2.ChangeDutyCycle(0)
        led3.ChangeDutyCycle(0)

# Guess button
def btn_guess_pressed(channel):
    global curr_guess
    global rand_num
    global led1
    global led2
    global led3
    global name
    global end_of_game
    global buzzer
    global num_guesses
    
    # Increment number of guesses
    num_guesses+=1
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    start_time = time.time()
    while GPIO.input(btn_submit) == 1:
        time.sleep(0.01)
    time_held = time.time() - start_time
    if time_held > 3:
        curr_guess = 0
        num_guesses = 0
        led1.ChangeDutyCycle(0)
        led2.ChangeDutyCycle(0)
        led3.ChangeDutyCycle(0)
        end_of_game = True
    # Compare the actual value with the user value displayed on the LEDs
    accuracy_leds()
    # Change the PWM LED
    # if it's close enough, adjust the buzzer
    if curr_guess != rand_num:
        trigger_buzzer()
        if curr_guess == 0:
            led1.ChangeDutyCycle(0)
            led2.ChangeDutyCycle(0)
            led3.ChangeDutyCycle(0)
        elif curr_guess == 1:
            led1.ChangeDutyCycle(LED_accuracy)
            led2.ChangeDutyCycle(0)
            led3.ChangeDutyCycle(0)
        elif curr_guess == 2:
            led1.ChangeDutyCycle(0)
            led2.ChangeDutyCycle(LED_accuracy)
            led3.ChangeDutyCycle(0)
        elif curr_guess == 3:
            led1.ChangeDutyCycle(LED_accuracy)
            led2.ChangeDutyCycle(LED_accuracy)
            led3.ChangeDutyCycle(0)
        elif curr_guess == 4:
            led1.ChangeDutyCycle(0)
            led2.ChangeDutyCycle(0)
            led3.ChangeDutyCycle(LED_accuracy)
        elif curr_guess == 5:
            led1.ChangeDutyCycle(LED_accuracy)
            led2.ChangeDutyCycle(0)
            led3.ChangeDutyCycle(LED_accuracy)
        elif curr_guess == 6:
            led1.ChangeDutyCycle(0)
            led2.ChangeDutyCycle(LED_accuracy)
            led3.ChangeDutyCycle(LED_accuracy)
        elif curr_guess == 7:
            led1.ChangeDutyCycle(LED_accuracy)
            led2.ChangeDutyCycle(LED_accuracy)
            led3.ChangeDutyCycle(LED_accuracy)
    # if it's an exact guess:
    # - Disable LEDs and Buzzer
    # - my extension: LED dance on correct guess
    # - tell the user and prompt them for a name
    # - fetch all the scores
    # - add the new score
    # - sort the scores
    # - Store the scores back to the EEPROM, being sure to update the score count
    elif curr_guess == rand_num:
        sleep = 0.1
        print("Congratulations, you win!!!")
        # This is something a little extra.
        # To make the win a bigger deal, the buzzer will sound
        # and the LEDs will do a little dance
        buzzer.stop()
        buzzer.start(100)
        for i in range(7):
            led1.ChangeDutyCycle(100)
            led2.ChangeDutyCycle(0)
            led3.ChangeDutyCycle(0)
            time.sleep(sleep)
            led1.ChangeDutyCycle(0)
            led2.ChangeDutyCycle(100)
            led3.ChangeDutyCycle(0)
            time.sleep(sleep)
            led1.ChangeDutyCycle(0)
            led2.ChangeDutyCycle(0)
            led3.ChangeDutyCycle(100)
            time.sleep(sleep)
            led1.ChangeDutyCycle(0)
            led2.ChangeDutyCycle(100)
            led3.ChangeDutyCycle(0)
            time.sleep(sleep)
        led1.ChangeDutyCycle(0)
        led2.ChangeDutyCycle(0)
        led3.ChangeDutyCycle(0)
        buzzer.stop()
        buzzer.ChangeDutyCycle(0)
        # Handle the name of the user
        name = input("Please enter your name below (maximum of 3 letters allowed):\n")
        while len(name) > 3:
            name = input("Please enter your name below (maximum of 3 letters allowed):\n")
        if len(name) < 3:
            name = name + (3-len(name))*'-'
        
        # Save scores
        save_scores()
        
        #reset to defualts
        curr_guess = 0
        num_guesses = 0
        end_of_game = True
        
        
# LED Brightness
def accuracy_leds():
    global LED_accuracy
    global curr_guess
    global rand_num
    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
    temp_curr = curr_guess
    temp_rand = rand_num
    if curr_guess == 0:
        temp_curr = 1
    if rand_num == 0:
        temp_rand = 1
    if curr_guess <= rand_num:
        LED_accuracy = (temp_curr/temp_rand)*100
    else:
        LED_accuracy = ((8-curr_guess)/(8-rand_num))*100

# Sound Buzzer
def trigger_buzzer():
    global buzzer
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    if abs(curr_guess - rand_num) == 3:
        buzzer.stop()
        buzzer.start(50)
        buzzer.ChangeFrequency(1)
    elif abs(curr_guess - rand_num) == 2:
        buzzer.stop()
        buzzer.start(50)
        buzzer.ChangeFrequency(2)
    elif abs(curr_guess - rand_num) == 1:
        buzzer.stop()
        buzzer.start(50)
        buzzer.ChangeFrequency(4)
    else:
        buzzer.stop()
        buzzer.ChangeDutyCycle(0)


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