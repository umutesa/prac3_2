# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
import time
import sys

# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game
begin = 0
end = 0
buttonStatus = 0
guesses = 0


# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzer = 33
eeprom = ES2EEPROMUtils.ES2EEPROM()


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
        while not end_of_game:
            
            pass
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")


class Counter():            #counter class created for ease of use
    def __init__(self):      #definitions self explanitory
        self.cnt = 0

    def increment(self):
        self.cnt += 1

    def reset(self):
        self.cnt = 0

    def get_value(self):
        return self.cnt


GPIO.setmode(GPIO.BOARD)            #set PWM pins
GPIO.setup(LED_accuracy, GPIO.OUT)
GPIO.setup(buzzer, GPIO.OUT)
LED_pwm = GPIO.PWM(LED_accuracy, 1000)
buzzer_pwm = GPIO.PWM(buzzer, 1000)
count = Counter()


def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    print("There are {} scores. Here are the top 3!".format(count))
    # print out the scores in the required format
    scores = raw_data
    if (count == 0):                                        #situation where there is no scores recorded
        print("sadly there are non :(")
    else:
        scores.sort(key=sort_list)                    #sort list
        i = 0
        for entry in scores:                            #dislay top 3 scores
            if (i == 3):
                break
            print("{} - {} took {} guesses".format((i + 1),entry[0],entry[1]))
            i += 1
    pass


def callback1(channel):
    btn_guess_pressed()
    print("falling edge detected on btn_submit")
    pass


def callback2(channel):
    btn_increase_pressed()
    print("falling edge detected on btn_increase")
    pass


# Setup Pins
def setup():
                                            #pin setup
    GPIO.setup(LED_value[0], GPIO.OUT)      #set LED's to outputs
    GPIO.setup(LED_value[1], GPIO.OUT)
    GPIO.setup(LED_value[2], GPIO.OUT)
    GPIO.setup(btn_submit, GPIO.IN, pull_up_down=GPIO.PUD_UP)   #set push buttons to inputs and pulldown
    GPIO.setup(btn_increase, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.output(LED_value[0], GPIO.LOW)     #set initial value of LED's to 0
    GPIO.output(LED_value[1], GPIO.LOW)
    GPIO.output(LED_value[2], GPIO.LOW)
    GPIO.output(buzzer, GPIO.LOW)

    LED_pwm.start(0)
    buzzer_pwm.start(0)
    GPIO.add_event_detect(btn_submit, GPIO.BOTH, callback=callback1, bouncetime=500)        #inturrupt when increase button is pressed
    GPIO.add_event_detect(btn_increase, GPIO.FALLING, callback=callback2, bouncetime=500)   #inturreupt when sumbit button is pressed
    # Setup debouncing and callbacks
    pass


# Load high scores
def fetch_scores():
    # get however many scores there are
    
    score_count = eeprom.read_byte(0)                       #Read 1st register to find num scores
    print("amount of scores is: {}" .format(score_count))
    
    # Get the scores
    scores_raw = []
    scores_raw = eeprom.read_block(1,score_count*4)         #get amount of scores
    # convert the codes back to ascii
    print(scores_raw)
    i = 0
    j = 0
    k = 0
    temp = ""                                               #initiate variables to use in loops
    rows, cols = (score_count, 2)                           #Create empty scores 2D list 
    scores = [[0 for i in range(cols)] for j in range(rows)]
    while (i < len(scores_raw)):                            #populate scores with 1st 3 char = name, 3th = score
        if (j == 3):                                        #once name has 3 letters add it to list
            scores[k][0] = temp
            scores[k][1] = scores_raw[i]                    #add next item in scores which will be num of guesses
            k = k + 1
            i = i + 1
            j = 0
            temp = ""
            continue
        temp = temp + chr(scores_raw[i])                    #add charachters to temp until its full
        i += 1
        j += 1
    print(scores)
    # return back the results
    return score_count, scores                              #returns num of scores in score_count. return 2D list scores with name and score


# Save high scores
def save_scores(name, guess):
    score_count, scores = fetch_scores()
    scores.append([name, guess])                   #include new score
    scores.sort(key=sort_list)                     #sort list
    score_write = []
    for name_entry in scores:                      #turn 2D scores into 1D raw data list to be sent to eeprom
        i = 0
        for x in name_entry:
            if (i == 0):
                j = 0
                while (j < 3):
                    score_write.append(ord(x[j]))   #transform name to ASCII value and add to score_write
                    j += 1
            else:
                score_write.append(x)
            i += 1
    score_count = score_count + 1               #increment amount of scores
    eeprom.write_byte(0,score_count)            #Update total scores in reg 0 in EEEPROM
    eeprom.write_block(1, score_write)          #write all scores to eeprom
    pass

def sort_list(elem):        #used when sorting lists
    return elem[1]

# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1) 


num = generate_number()


# Increase button pressed
def btn_increase_pressed():
    temp = count.get_value() # get count value for LEDs
    GPIO.output(LED_value[0], temp & 0x01)
    GPIO.output(LED_value[1], temp & 0x02)
    GPIO.output(LED_value[2], temp & 0x04)  # set respective pins high or low
    count.increment()
    if count.get_value() > 7:  # reset count if too high
        count.reset()
    pass


# Guess button
def btn_guess_pressed():
    global num
    global guesses
    start_time = time.time()  # for long button press
    diff = 0
    while (GPIO.input(btn_submit) == 0) and (diff < 2):  # while button pulled low and not held too long..
        now_time = time.time()
        diff = - start_time + now_time  # get diff in time
    if diff < 2:  # if less than 2 second press do this
        guesses += 1
        guess = count.get_value()
        # Compare the actual value with the user value displayed on the LEDs
        diff1 = guess - num
        diff1 = abs(diff1)
        accuracy_leds(num, guess)
        trigger_buzzer(diff1)
        if diff1 == 0:  # if guess corrctly
            GPIO.output(LED_value, GPIO.LOW)
            GPIO.output(LED_accuracy, GPIO.LOW)
            GPIO.output(buzzer, GPIO.HIGH)
            sguess = str(guesses)
            print("You Won in only " + sguess + " guesses!\n")
            name = input("Enter your name: ")
            while len(name) != 3:
                print("your name should be 3 letters long!\n")
                name = input("Try again!")          
            save_scores(name, guess)
            os.execl(sys.executable, sys.executable, * sys.argv)
        # elif diff1 == 1:                                        # if guess is close to correct
            # print("off by 1")
        # elif diff1 == 2:
            # print("off by 2")
        # elif diff1 == 3:
            # print("off by 3")
    else:
        # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
        os.execl(sys.executable, sys.executable, * sys.argv)
    pass


# LED Brightness
def accuracy_leds(answer, guess):  # receives answer and guess value

    if answer >= guess: 
        temp = guess/answer*100  # use this form if ans > guess
    elif answer - guess == 0:
        LED_pwm.ChangeDutyCycle(0)  # set duty cycle to zero if correct
    else:
        temp = ((8-guess)/(8-answer))*100  # else use this

    LED_pwm.ChangeDutyCycle(temp)  # update duty cycle
    pass

# Sound Buzzer
def trigger_buzzer(off):  # triggers being given a value by how far off it is

    buzzer_pwm.ChangeDutyCycle(50)  #ensure buzzer has a duty cycle
    if off == 0:
        GPIO.output(buzzer, GPIO.LOW)   # set low if correct
    elif off == 1:
        buzzer_pwm.ChangeFrequency(4)
    elif off == 2:
        buzzer_pwm.ChangeFrequency(2)
    elif off == 3:
        buzzer_pwm.ChangeFrequency(1)  # update frequencies based on guess
    else:
        GPIO.output(buzzer, GPIO.HIGH)  # else keep it high
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