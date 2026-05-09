import RPi.GPIO as GPIO
import time
import sys

BIT_0 = 24
BIT_1 = 8
BIT_2 = 7
MAIN_PED_BUTTON = 25
CROSS_PED_BUTTON = 22

main_ped_requested = False
cross_ped_requested = False

def main_ped_callback(channel):
    global main_ped_requested
    print(f"\n[Model 2] Main road pedestrian button (GPIO {channel}) pressed!")
    main_ped_requested = True

def cross_ped_callback(channel):
    global cross_ped_requested
    print(f"\n[Model 2] Crossroad pedestrian button (GPIO {channel}) pressed!")
    cross_ped_requested = True

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Output
    GPIO.setup([BIT_0, BIT_1, BIT_2], GPIO.OUT)
    GPIO.output([BIT_0, BIT_1, BIT_2], GPIO.LOW)
    
    # Input
    GPIO.setup([MAIN_PED_BUTTON, CROSS_PED_BUTTON], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    # 500ms debounce
    GPIO.add_event_detect(MAIN_PED_BUTTON, GPIO.RISING, callback=main_ped_callback, bouncetime=500)
    GPIO.add_event_detect(CROSS_PED_BUTTON, GPIO.RISING, callback=cross_ped_callback, bouncetime=500)

def set_state(code):
    """Sends the 3-bit code to the corresponding GPIO pins"""
    GPIO.output(BIT_0, code & 0b001)
    GPIO.output(BIT_1, (code & 0b010) >> 1)
    GPIO.output(BIT_2, (code & 0b100) >> 2)

def state_machine():
    global main_ped_requested, cross_ped_requested
    
    while True:
        # STATE 1: Green (Main) / Red (Crossroad)
        set_state(1)
        main_ped_requested = False
        start_time = time.time()
        while (time.time() - start_time) < 20.0:
            if main_ped_requested and (time.time() - start_time) >= 10.0:
                break
            time.sleep(0.1)

        # STATE 2: Yellow (Main) / Red (Crossroad)
        set_state(2)
        time.sleep(2.0)

        # STATE 4: Red (Main) / Red (Crossroad)
        set_state(4)
        time.sleep(2.0)

        # STATE 5: Red (Main) / Green (Crossroad)
        set_state(5)
        cross_ped_requested = False
        start_time = time.time()
        while (time.time() - start_time) < 10.0:
            # Green min 5s, max 10s
            if cross_ped_requested and (time.time() - start_time) >= 5.0:
                break
            time.sleep(0.1)

        # STATE 6: Red (Main) / Yellow (Crossroad)
        set_state(6)
        time.sleep(2.0)

        # STATE 4: Red (Main) / Red (Crossroad)
        set_state(4)
        time.sleep(2.0)

if __name__ == '__main__':
    try:
        print("Starting Traffic Light Model 2 (Press CTRL+C to exit)")
        setup()
        state_machine()
    except KeyboardInterrupt:
        print("\nExiting Model 2...")
    finally:
        GPIO.cleanup()
        sys.exit(0)
