# Drive Forward

import motor, motor_pair
from hub import port
from hub import light_matrix
import distance_sensor
import runloop

async def main():
    await motor.run_for_time(port.E, 1000, 200)
    
runloop.run(main())
