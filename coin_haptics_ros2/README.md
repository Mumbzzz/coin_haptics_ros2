# coin_haptics_ros2

ROS 2 package for taxel-driven coin vibration motors.

## Nodes

### tss_to_coin_motor_node
Processes taxel data per finger and publishes normalized stimulation values.

### coin_motor_serial_node
Aggregates stimulation commands and streams them over serial to the Arduino motor controller.

## Hardware

- Arduino Uno
- Adafruit 5648 MOSFET drivers
- TPS62827 3.3V buck converter
- 3V coin vibration motors

## Status

Single-motor bring-up complete. Multi-motor scaling in progress.

## Finger ↔ Motor ↔ Taxel Mapping

The system uses a fixed motor ordering defined in the Arduino firmware:
cpp const int motorPins[NUM_MOTORS] = {3, 5, 6, 9, 10};
`

Each finger must be wired and launched according to the mapping below.

| Motor Index | Arduino Pin | Finger | ROS Output Topic           | Expected Taxel Topic |
| ----------- | ----------- | ------ | -------------------------- | -------------------- |
| 0           | D3          | thumb  | `/coin_motor/right/thumb`  | `/taxel_0`           |
| 1           | D5          | index  | `/coin_motor/right/index`  | `/taxel_1`           |
| 2           | D6          | middle | `/coin_motor/right/middle` | `/taxel_2`           |
| 3           | D9          | ring   | `/coin_motor/right/ring`   | `/taxel_3`           |
| 4           | D10         | pinky  | `/coin_motor/right/pinky`  | `/taxel_4`           |

### Data Flow

For each finger:
taxel topic → tss_to_coin_motor_node → /coin_motor/right/<finger> → coin_motor_serial_node → Arduino PWM pin → motor
---

## Example: Launch a Single Finger Node

Example for the **index finger**:
bash ros2 run coin_haptics_ros2 tss_to_coin_motor_node \ --ros-args \ -p sensor_hand:=right \ -p finger_name:=index \ -p sensor_topic:=/taxel_1
This configuration assumes:

* The index motor driver is wired to **Arduino D5**
* The index taxel publishes on **/taxel_1**
* The serial node is already running

---

## Notes

* The motor index is determined strictly by the Arduino pin order.
* Do not change the motor order unless the Arduino firmware and serial node are updated together.
* For single-motor testing on D3, use `finger_name:=thumb`.
---
