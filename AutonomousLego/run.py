# Drive Forward

import motor, motor_pair
from hub import port
from hub import light_matrix
import distance_sensor
import runloop

async def main():
    motor_pair.pair(motor_pair.PAIR_1, port.E, port.A)
    motor_pair.move(motor_pair.PAIR_1, 0, velocity=100)
    
runloop.run(main())
