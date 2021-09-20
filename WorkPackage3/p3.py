# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
import time
import sys

# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game


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


class count():            
    def __init__(self):      
        self.cnt = 0

    def setvalue(self):
        self.cnt += 1
    
    def get(self):
        return self.cnt

    def reset(self):
        self.cnt = 0

last_pressed = 0
GPIO.setmode(GPIO.BOARD)            
GPIO.setup(LED_accuracy, GPIO.OUT)
GPIO.setup(buzzer, GPIO.OUT)
LED_pwm = GPIO.PWM(LED_accuracy, 1000)
buzzer_pwm = GPIO.PWM(buzzer, 1000)
count = count()


def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    print("There are {} scores. Here are the top 3!".format(count))
    # print out the scores in the required format
    scores = raw_data
    if (count == 0):                                      
        print("sadly there are non :(")
    else:
        scores.sort(key=sort_list)                   
        i = 0
        for entry in scores:                            
            if (i == 3):
                break
            print("{} - {} took {} guesses".format((i + 1),entry[0],entry[1]))
            i += 1
    pass


def callback1(channel):
    print("Button increase detected")
    btn_increase_pressed()
    pass


def callback2(channel):
    print("Button Submit detected")
    btn_guess_pressed()
    pass


# Setup Pins
def setup():


                                        
    for x in LED_value:
      GPIO.setup(x, GPIO.OUT)

    GPIO.setup(btn_submit, GPIO.IN, pull_up_down=GPIO.PUD_UP)   #set push buttons to inputs and pulldown
    GPIO.setup(btn_increase, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    for x in LED_value:
      GPIO.output(x, GPIO.LOW)

    GPIO.output(buzzer, GPIO.LOW)

    last_pressed=0

    LED_pwm.start(0)
    buzzer_pwm.start(0)
    GPIO.add_event_detect(btn_submit, GPIO.FALLING, callback=callback1, bouncetime=500)        #inturrupt when increase button is pressed
    GPIO.add_event_detect(btn_increase, GPIO.FALLING, callback=callback2, bouncetime=500)   #inturreupt when sumbit button is pressed
    pass



def fetch_scores():

    score_count = None

    score_count = eeprom.read_byte(0)   
    scores = []
    rows, cols = (score_count, 2) 
    new_scores = [[0 for i in range(cols)] for j in range(rows)]
    scores = eeprom.read_block(1,score_count*4)
    #print(scores)
    i = 0
    k = 0
    while (i<len(scores)):
        name = ""
        j =0
        while(j<3):
            name = name + chr(scores[i])
            i= i+1
            j=j+1
        new_scores[k][0] = name
        new_scores[k][1] = scores[i]
        i=i+1
        name = ""
        k=k+1
    #print(new_scores)
    return score_count, new_scores                              #returns num of scores in score_count. return 2D list scores with name and score



def save_scores():

    # fetch scores
    score_count, scores = fetch_scores()

    # include new score
    more = 1 #trueq
    found = 0 #false
    guess = count.get()
    while more:
      name = input("Enter your name : ")

      if len(name) < 4:
         more = 0
      else:
         print("Your name should not have more than 3 letters!!")

     ## own comment: checking if the user already exists on the leaderboard so that you could just update the score that they already have
    for i in scores:
      n = scores[0]

      if(name == n):
         scores[i] = score[name,guess]
         found = 1
         break
    if not found:
        scores.append([name,guess])
    
    
    scores.sort(key=sort_list)
    score_write = []
    size = len(scores)
    #print(size)
    for i in range(size):
      new = list(scores[i][0])
      for j in new:
          score_write.append(ord(j))
      value = scores[i][1]
      score_write.append(value)

    score_count = score_count + 1
    eeprom.write_byte(0,score_count)
    size = (score_count)
    j=0
    for i in range(size):
        array = score_write[j:j+4]
        j=j+4
        #print(array)
        eeprom.write_block(i+1, array)
    pass

def sort_list(elem):        
    return elem[1]

# Generate guess number
def generate_number():
    return random.randint(1, pow(2, 3)-1)


num = generate_number()


# Increase button pressed
def btn_increase_pressed():
    value = count.get() 
    GPIO.output(LED_value[0], value & 0x01)
    GPIO.output(LED_value[1], value & 0x02)
    GPIO.output(LED_value[2], value & 0x04)  
    count.setvalue()
    if count.get() > 7:  # reset 
        count.reset()
    pass


# Guess button
def btn_guess_pressed():
    start_time = time.time()  
    while GPIO.input(btn_submit) == GPIO.LOW:
        time.sleep(0.01)

    length = (time.time())-start_time
    if length > 1:  #clears GPIO and take to main menu
        print ("Hold & Press")
        for x in LED_value:
            GPIO.output(x, GPIO.LOW)
        GPIO.output(buzzer, GPIO.LOW)

        GPIO.output(LED_accuracy, GPIO.LOW)

       #GPIO.remove_event_detect(btn_increase)
        #GPIO.remove_event_detect(btn_submit)

        os.execl(sys.executable, sys.executable, * sys.argv)
    else:
        print ("Short Press")
        guess = count.get()
        #print(guess)
        #print(num)
        difference = abs(guess -num)
        accuracy_leds(num, guess)
        trigger_buzzer(difference)
        if difference==0 :
            GPIO.remove_event_detect(btn_increase)
            GPIO.remove_event_detect(btn_submit)
            end_of_game = True
            print("Well Done! Correct Guess!")
            save_scores()
            time.sleep(0.03)
            os.execl(sys.executable, sys.executable, * sys.argv)

    pass


# LED Brightness
def accuracy_leds(secretvalue, guess):  

    if secretvalue >= guess:
        temp = guess/secretvalue*100  
    elif secretvalue- guess == 0:
        LED_pwm.ChangeDutyCycle(0)  
    else:
        temp = ((8-guess)/(8-secretvalue))*100  

    LED_pwm.ChangeDutyCycle(temp) 
    pass

# Sound Buzzer
def trigger_buzzer(difference):  

    buzzer_pwm.ChangeDutyCycle(50)  
    if difference == 0:
        GPIO.output(buzzer, GPIO.LOW)   
    elif difference == 1:
        buzzer_pwm.ChangeFrequency(4)
    elif difference == 2:
        buzzer_pwm.ChangeFrequency(2)
    elif difference == 3:
        buzzer_pwm.ChangeFrequency(1)  
    else:
        GPIO.output(buzzer, GPIO.HIGH)  
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