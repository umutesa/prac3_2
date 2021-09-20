# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
import math
import time

# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game
guess = 0
secret_value = 0 #generate a random number

# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzer = None
eeprom = ES2EEPROMUtils.ES2EEPROM()
last_pressed = 0
led_pwm = None
buzzer_pwm = None

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


def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    print("There are {} scores. Here are the top 3!".format(count))
    # print out the scores in the required format
    if (count==0):
      printf("No high score to display")
    else :
      raw_data.sort(key=sort_list)
      for i in range(3):
        for x in raw_data:
          print("{} - {} took {} guesses".format((i + 1),x[0],x[1]))
    pass


# Setup Pins
def setup():
    # Setup board mode
    secret_value = generate_number()
    guess = 0
    GPIO.setmode(GPIO.BOARD)
    # Setup regular GPIO
    #GPIO.setup
    for x in LED_value:
      GPIO.setup(x, GPIO.OUT)

    GPIO.setup(buzzer, GPIO.OUT)

    GPIO.setup(btn_increase, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(btn_submit, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(LED_accuracy,GPIO.OUT)
   
    # Setup PWM channels
    led_pwm = GPIO.PWM(LED_accuracy,1000)
    buzzer_pwm = GPIO.PWM(buzzer,1000)

    for x in LED_value :
      pwm = GPIO.PWM(x,1000)  #loop for eaach led
      pwm.start(0)	#set duty cylce to 5
    
    led_pwm.start(0)
    buzzer_pwm.start(0)

    # Setup debouncing and callbacks
    GPIO.add_event_detect(btn_increase, GPIO.FALLING, callback=callback_increase, bouncetime=200)
    GPIO.add_event_detect(btn_submit, GPIO.BOTH, callback=callback_submit, bouncetime=200)
    pass

def callback_increase(channel):
   milli_sec = int(round(time.time() * 100))
   if (milli_sec - last_pressed < 100):
      last_pressed = milli_sec
      print("Button increase detected")
      btn_increase_pressed()
   pass

def callback_submit(channel):
   milli_sec = int(round(time.time() * 100))
   if (milli_sec - last_pressed > 100 and milli_sec - last_pressed < 200): #press and hold
      end_of_game = True
      last_pressed = milli_sec
      GPIO.cleanup()
      main()
   elif (milli_sec - last_pressed > 100) :
      last_pressed = milli_sec
      print("Button Submitted detected")
      btn_guess_pressed()
   pass

# Load high scores
def fetch_scores():
    # get however many scores there are
    score_count = None

    score_count = eeprom.read_byte(0)   #gets the score count
    scores = []
    # Get the scores
    for x in range(1,score_count+1):
      scores.append(read_block(x,4))   #adds the score
    # convert the codes back to ascii
    for x in range(len(scores)):
      for y in range(len(scores[i])):
         scores[x][y] = char(scores[x][y])


    # return back the results
    return score_count, scores


# Save high scores
def save_scores():
    # fetch scores
    score_count, scores = fetch_scores()
    # include new score
    more = 1 #true
    found = 0 #false

    while more:
      name = input("Enter your name")

      if len(name) < 4:
         more = false
      else:
         println("Your name should not have more than 3 letters")

     ## own comment: checking if the user already exists on the leaderboard so that you could just update the score that they already have
    for i in scores:
      n = i[0] + i[1] +i[2]

      if(name == n):
         i[3] = i[3] + 1
         found = 1
         break

    if not found:
      new = []
      new = list(name)
      new.append(1)
      scores.append(new)

    # sort

    scores.sort(key=lambda x: x[3])

    # update total amount of scores
    score_count = len(scores)

    # write new scores
    eeprom.write_block(0,[score_count])

    for i in range(score_count):
      eeprom.write_block(i+1, scores[i])
    pass


# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)


# Increase button pressed
def btn_increase_pressed():
    # Increase the value shown on the LEDs
    # You can choose to have a global variable store the user's current guess,
    # or just pull the value off the LEDs when a user makes a guess

    GPIO.output(LED_value[0], guess & 0x01)
    GPIO.output(LED_value[1], guess & 0x02)
    GPIO.output(LED_value[2], guess & 0x04)

    guess = guess + 1
    if guess > 7:
      guess=0
    pass


# Guess button
def btn_guess_pressed():
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

    Accuracy_leds()
    differnce_value = abs(secret_value-guess)
    if (difference_value==0):

      for x in LED_value:
        GPIO.output(x,0)

      GPIO.output(buzzer_pin, 1)

      end_of_game = True
      print("Well Done! Correct Guess!")

      save_scores()

    elif (difference_value<4) :
      trigger_buzzer()
    pass


# LED Brightness
def accuracy_leds():
    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%

    if (guess>secret_value):
      duty_cycle = (8-guess)/(8-secret_value)*100
    elif ((guess-secret_value)==0):
      duty_cycle = 0
    else :
      duty_cycle = guess/secret_value*100

    pwm.ChangeDutyCycle(duty_cycle)

    pass

# Sound Buzzer
def trigger_buzzer():
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second

    buzzer_pwm.ChangeDutyCycle(50)
    off_value = abs(secret_value-guess)
    if (off_value == 3) :
      buzzer.stop()
      buzzer.start(50)
      buzzer.ChangeFrequency(1)
      sleep(1)
    elif (off_value == 2) :
      buzzer.stop()
      buzzer.start(50)
      buzzer.ChangeFrequency(2)
      sleep(1)
    elif (off_value == 1) :
      buzzer.stop()
      buzzer.start(50)
      buzzer.ChangeFrequency(4)
      sleep(1)
    else :
      buzzer.stop()
      buzzer.start(50)
      buzzer.ChangeDutyCycle(0)

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
