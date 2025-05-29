# To run this clock, open your terminal or command prompt,
# navigate to the directory where this file (clock.py) is saved,
# and then type the following command and press Enter:
#
# python clock.py
#
# The clock will start displaying the current time and update every second.
# To stop the clock, press Ctrl+C.

import time

def display_time():
    """Displays the current time in HH:MM:SS format, updating every second."""
    try:
        while True:
            current_time = time.strftime('%H:%M:%S')
            print(current_time, end='\r')  # Use \r to overwrite the previous line
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nClock stopped.")

if __name__ == "__main__":
    display_time()
