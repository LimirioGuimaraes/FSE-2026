import RPi.GPIO as GPIO
import time
import sys

# Pin Configuration - Model 1
GREEN_LED = 17
YELLOW_LED = 18
RED_LED = 23
MAIN_PED_BUTTON = 1
CROSS_PED_BUTTON = 12

# Interrupt flag
pedestrian_requested = False

def button_callback(channel):
    global pedestrian_requested
    print(f"\n[Model 1] Pedestrian button pressed on GPIO {channel}!")
    pedestrian_requested = True

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Output configuration
    GPIO.setup([GREEN_LED, YELLOW_LED, RED_LED], GPIO.OUT)
    GPIO.output([GREEN_LED, YELLOW_LED, RED_LED], GPIO.LOW)
    
    # Input configuration (Pull-Down: normally low, active high)
    GPIO.setup([MAIN_PED_BUTTON, CROSS_PED_BUTTON], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    # Interrupt configuration with 200ms debounce
    GPIO.add_event_detect(MAIN_PED_BUTTON, GPIO.RISING, callback=button_callback, bouncetime=200)
    GPIO.add_event_detect(CROSS_PED_BUTTON, GPIO.RISING, callback=button_callback, bouncetime=200)

def set_leds(green, yellow, red):
    GPIO.output(GREEN_LED, green)
    GPIO.output(YELLOW_LED, yellow)
    GPIO.output(RED_LED, red)

def state_machine():
    global pedestrian_requested
    
    while True:
        # GREEN STATE
        set_leds(GPIO.HIGH, GPIO.LOW, GPIO.LOW)
        pedestrian_requested = False
        start_time = time.time()
        
        # Max duration: 10s, Min duration: 5s
        while (time.time() - start_time) < 10.0:
            if pedestrian_requested and (time.time() - start_time) >= 5.0:
                break # Exit green state after 5s if button was pressed
            time.sleep(0.1)
            
        # YELLOW STATE
        set_leds(GPIO.LOW, GPIO.HIGH, GPIO.LOW)
        pedestrian_requested = False # Ignore presses during yellow
        time.sleep(2.0)
        
        # RED STATE
        set_leds(GPIO.LOW, GPIO.LOW, GPIO.HIGH)
        pedestrian_requested = False # Ignore presses during red
        time.sleep(10.0)

if __name__ == '__main__':
    try:
        print("Starting Traffic Light Model 1 (Press CTRL+C to exit)")
        setup()
        state_machine()
    except KeyboardInterrupt:
        print("\nExiting Model 1...")
    finally:
        GPIO.cleanup()
        sys.exit(0)
