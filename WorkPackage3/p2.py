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


class Counter():            #counter class created for ease of use
    def __init__(self):      #definitions self explanitory
        self.cnt = 0

    def increment(self):
        self.cnt += 1

    def reset(self):
        self.cnt = 0

    def get_value(self):
        return self.cnt
last_pressed = 0
count = Counter()
GPIO.setmode(GPIO.BOARD)            #set PWM pins
GPIO.setup(LED_accuracy, GPIO.OUT)
GPIO.setup(buzzer, GPIO.OUT)
LED_pwm = GPIO.PWM(LED_accuracy, 1000)
buzzer_pwm = GPIO.PWM(buzzer, 1000)

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
   # if (guesses==1 or guesses == 0):
    #    last_pressed =0
    #milli_sec = int(time.time())
    #print(milli_sec)
    #print(last_pressed)
    #if (milli_sec - last_pressed > 100):
     # last_pressed = milli_sec
    print("Button increase detected")
    btn_increase_pressed()


    pass


def callback2(channel):
    #milli_sec = int((time.time()))
    #if ((guesses==1 or guesses == 0)):
     #   last_pressed =0
    #if (milli_sec - last_pressed > 100 and milli_sec - last_pressed < 200): #press and hold
     # end_of_game = True
      #last_pressed = milli_sec
      #GPIO.cleanup()
      #main()
    #if (milli_sec - last_pressed > 100) :
     # last_pressed = milli_sec
    print("Button Submitted detected")
    btn_guess_pressed()



    pass


# Setup Pins
def setup():


    #GPIO.setmode(GPIO.BOARD)            #set PWM pins
    #GPIO.setup(LED_accuracy, GPIO.OUT)
    #GPIO.setup(buzzer, GPIO.OUT)


                                            #pin setup
    for x in LED_value:
      GPIO.setup(x, GPIO.OUT)

    GPIO.setup(btn_submit, GPIO.IN, pull_up_down=GPIO.PUD_UP)   #set push buttons to inputs and pulldown
    GPIO.setup(btn_increase, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    for x in LED_value:
      GPIO.output(x, GPIO.LOW)

    GPIO.output(buzzer, GPIO.LOW)

    last_pressed = 0

    #LED_pwm = GPIO.PWM(LED_accuracy, 1000)
    #buzzer_pwm = GPIO.PWM(buzzer, 1000)
    LED_pwm.start(0)
    buzzer_pwm.start(0)
    GPIO.add_event_detect(btn_submit, GPIO.FALLING, callback=callback1, bouncetime=500)        #inturrupt when increase button is pressed
    GPIO.add_event_detect(btn_increase, GPIO.FALLING, callback=callback2, bouncetime=500)   #inturreupt when sumbit button is pressed
    # Setup debouncing and callbacks
    pass


# Load high scores
def fetch_scores():
    # get however many scores there are

    score_count = None

    score_count = eeprom.read_byte(0)   #gets the score count
    scores = []
    rows, cols = (score_count, 2) 
    new_scores = [[0 for i in range(cols)] for j in range(rows)]
    scores = eeprom.read_block(1,score_count*4)
    print(scores)
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
    # return back the results
    #print(new_scores)
    return score_count, new_scores                              #returns num of scores in score_count. return 2D list scores with name and score


# Save high scores
def save_scores():

    # fetch scores
    score_count, scores = fetch_scores()

    # include new score
    more = 1 #trueq
    found = 0 #false
    guess = count.get_value()
    while more:
      name = input("Enter your name")

      if len(name) < 4:
         more = 0
      else:
         print("Your name should not have more than 3 letters")

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
    print(size)
    for i in range(size):
      new = list(scores[i][0])
      for j in new:
          score_write.append(ord(j))
      value = scores[i][1]
      score_write.append(value)

    print(score_write)
    print("Score Write")
    print(score_count)
    print("Score Cout before") 
    score_count = score_count + 1
    eeprom.write_byte(0,score_count)
    v = eeprom.read_byte(0)           #Update total scores in reg 0 in EEEPROM
    print(v)
    print("score")
    #eeprom.clear(2048)
    size = (score_count)
    j=0
    for i in range(size):
        array = score_write[j:j+4]
        j=j+4
        print(array)
        eeprom.write_block(i+1, array)
    g = eeprom.read_block(1,score_count*4)
    print(g)
    print("block")

    pass

def sort_list(elem):        #used when sorting lists
    return elem[1]

# Generate guess number
def generate_number():
    return random.randint(1, pow(2, 3)-1)


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
    #global num
    #global guesses
    start_time = time.time()  # for long button press
    time.sleep(0.01)
    while GPIO.input(btn_submit) == GPIO.LOW:
        time.sleep(0.01)
    


    length = (time.time())-start_time
    print(length)    
    if length > 3:
        print ("Long Press")
        #guesses += 1
        guess = count.get_value()
        difference = abs(guess -num)
        accuracy_leds(num, guess)
        trigger_buzzer(difference)
        if difference == 0 :
            end_of_game = True
            print("Well Done! Correct Guess!")
            save_scores()

    else:
        print ("Short Press")
        #guesses += 1
        guess = count.get_value()
        print(guess)
        print(num)
        difference = abs(guess -num)
        accuracy_leds(num, guess)
        trigger_buzzer(difference)
        if difference==0 :
         end_of_game = True
         print("Well Done! Correct Guess!")
         save_scores()

    pass




    #diff = 0

    #while (GPIO.input(btn_submit) == 0) and (diff < 2):  # while button pulled low and not held too long..
     #   now_time = time.time()
      #  diff = - start_time + now_time  # get diff in time
    #if diff < 2:  # if less than 2 second press do this
     #   guesses += 1
      #  guess = count.get_value()
        # Compare the actual value with the user value displayed on the LEDs
       # diff1 = guess - num
        #diff1 = abs(diff1)
        #accuracy_leds(num, guess)
        #trigger_buzzer(diff1)
        #if diff1 == 0:  # if guess corrctly
         #   GPIO.output(LED_value, GPIO.LOW)
          #  GPIO.output(LED_accuracy, GPIO.LOW)
           # GPIO.output(buzzer, GPIO.HIGH)
            #sguess = str(guesses)
            #print("You Won in only " + sguess + " guesses!\n")
            #name = input("Enter your name: ")
            #while len(name) != 3:
             #   print("your name should be 3 letters long!\n")
              #  name = input("Try again!")
            #save_scores(name, guess)
            #os.execl(sys.executable, sys.executable, * sys.argv)

    #else:
        # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
     #   os.execl(sys.executable, sys.executable, * sys.argv)
    #pass


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