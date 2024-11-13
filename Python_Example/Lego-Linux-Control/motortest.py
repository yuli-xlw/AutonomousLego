# Drive Forward

import motor, motor_pair
from hub import port
from hub import light_matrix
import distance_sensor
import runloop

async def main():
    await motor.run_to_absolute_position(port.E, 0, 200, direction=motor.SHORTEST_PATH, stop=motor.HOLD)
    motor_pair.pair(motor_pair.PAIR_1, port.F, port.C)
    light_matrix.write('After')
    motor_pair.move(motor_pair.PAIR_1, 0, velocity=360)
    while (distance_sensor.distance(port.D) > 10):
        await runloop.sleep_ms(1)
    motor_pair.stop(motor_pair.PAIR_1)
    motor_pair.move_for_time(motor_pair.PAIR_1, 2000, 0) # time, steering
    await motor.run_to_absolute_position(port.E, 47, 200, direction=motor.SHORTEST_PATH, stop=motor.HOLD)
    await motor.run_to_absolute_position(port.E, 318, 200, direction=motor.SHORTEST_PATH, stop=motor.HOLD)
    await motor.run_to_absolute_position(port.E, 0, 200, direction=motor.SHORTEST_PATH, stop=motor.HOLD)

runloop.run(main())
