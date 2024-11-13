# Drive Forward

import motor, motor_pair
from hub import port
from hub import light_matrix
import distance_sensor
import runloop

async def main():
    await motor.run_to_absolute_position(port.E, 47, 200, direction=motor.SHORTEST_PATH, stop=motor.HOLD)
    await motor.run_to_absolute_position(port.E, 318, 200, direction=motor.SHORTEST_PATH, stop=motor.HOLD)
    await motor.run_to_absolute_position(port.E, 0, 200, direction=motor.SHORTEST_PATH, stop=motor.HOLD)

runloop.run(main())
