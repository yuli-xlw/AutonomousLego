from pyboard import Pyboard


baudrate = 115200 # This is the standard board rate to communicate with the Lego Hub
# This is the port that the Hub identifies itself as when connected by wire to my laptop
device = '/dev/ttyACM0' 
wait= 0


# This one simply displays a message on the Hub with a wait to complete
def say_text_wait(pyb, sentence):
    command = f"""\
from hub import light_matrix
import runloop
async def main():
    await light_matrix.write('{sentence}')

runloop.run(main())
"""
    pyb.exec(command)



def main():
    # Setup the lego hub
    pyb = Pyboard(device, baudrate, wait)
    pyb.enter_raw_repl()


    #Sending commands to the hub
    say_text_wait(pyb, 'Starting')
    

    pyb.exit_raw_repl()
    pyb.close()


if __name__ == "__main__":
    main()