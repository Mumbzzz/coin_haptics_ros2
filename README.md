# coin_haptics_ros2

ROS 2 package for controlling coin vibration motors using taxel-based tactile feedback.

This package processes tactile sensor data (taxel) and converts it into motor stimulation commands for coin vibration motors driven by an Arduino controller.

---

## Installation

### 1. Create a ROS 2 workspace

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws
```

### 2. Clone this repository

```bash
git clone https://github.com/Mumbzzz/coin_haptics_ros2.git src/coin_haptics_ros2
```

### 3. Install dependencies

This repository depends on several packages from the Biomechatronics Lab.
They can be installed automatically using the provided `.repos` file.

```bash
vcs import src < src/coin_haptics_ros2/dependencies.repos
```

### 4. Build the workspace

```bash
colcon build
```

### 5. Source the workspace

```bash
source install/setup.bash
```

---

## Dependencies

The following repositories are automatically pulled using `dependencies.repos`:

* sensor_skin_ros2
* std_msgs_stamped
* tactile_sensor_msgs

If `vcstool` is not installed:

```bash
sudo apt install python3-vcstool
```

---

## Nodes

### tss_to_coin_motor_node

Processes taxel data per finger and publishes normalized stimulation values.

### coin_motor_serial_node

Aggregates stimulation commands and streams them over serial to the Arduino motor controller.

---

## Hardware

* Arduino Uno
* Adafruit 5648 MOSFET drivers
* TPS62827 3.3V buck converter
* 3V coin vibration motors

---

## System Diagram

```
Taxel Sensor
      ↓
tss_to_coin_motor_node
      ↓
/coin_motor/<hand>/<finger>
      ↓
coin_motor_serial_node
      ↓
Serial
      ↓
Arduino PWM
      ↓
Coin Motor
```

---

## Finger ↔ Motor ↔ Taxel Mapping

The system uses a fixed motor ordering defined in the Arduino firmware:

```cpp
const int motorPins[NUM_MOTORS] = {3, 5, 6, 9, 10};
```

Each finger must be wired and launched according to the mapping below.

| Motor Index | Arduino Pin | Finger | ROS Output Topic           | Expected Taxel Topic |
| ----------- | ----------- | ------ | -------------------------- | -------------------- |
| 0           | D3          | thumb  | `/coin_motor/right/thumb`  | `/taxel_0`           |
| 1           | D5          | index  | `/coin_motor/right/index`  | `/taxel_1`           |
| 2           | D6          | middle | `/coin_motor/right/middle` | `/taxel_2`           |
| 3           | D9          | ring   | `/coin_motor/right/ring`   | `/taxel_3`           |
| 4           | D10         | pinky  | `/coin_motor/right/pinky`  | `/taxel_4`           |

---

## Data Flow

For each finger:

```
taxel topic
    ↓
tss_to_coin_motor_node
    ↓
/coin_motor/<hand>/<finger>
    ↓
coin_motor_serial_node
    ↓
Arduino PWM pin
    ↓
motor
```

---
## Running the System

### Start the Serial Motor Node

Before launching any finger processing nodes, start the serial node that communicates with the Arduino motor controller.

```bash
ros2 run coin_haptics_ros2 coin_motor_serial_node
```
This node:
* Subscribes to `/coin_motor/<hand>/<finger>` topics
* Aggregates stimulation values
* Streams motor commands over serial to the Arduino controller


### Start the TSS to Coin Motor Node

Each finger requires a `tss_to_coin_motor_node` instance that converts tactile sensor data into motor stimulation.

Example launch:
```bash
ros2 run coin_haptics_ros2 tss_to_coin_motor_node --ros-args
```
| Parameter                  | Description                                                     | Default          |
| -------------------------- | --------------------------------------------------------------- | ---------------- |
| `sensor_hand`              | Hand identifier used in topic naming                            | `right`          |
| `finger_name`              | Finger associated with this node instance                       | `default_finger` |
| `sensor_topic`             | Topic providing tactile sensor data                             | `/taxel_1`       |
| `sensor_feature_val_index` | Index of the tactile feature value used from the sensor message | `1`              |
| `tss_min`                  | Minimum tactile value used for scaling                          | `0.0`            |
| `tss_max`                  | Maximum tactile value used for scaling                          | `0.07`           |
| `tss_deadband_threshold`   | Deadband threshold below which stimulation is zero              | `0.003`          |

Each finger should run its own node instance with the appropriate parameters.

### Sensor Zero Calibration

Each `tss_to_coin_motor_node` provides a service to reset the tactile sensor baseline.  
Ensure the sensor is **not being touched**, then call:

```bash
ros2 service call /<hand>/<finger>/zero std_srvs/srv/Trigger
```

This resets the baseline used by the tactile processing node and begins collecting new reference samples.

---

## Example: Launch a Single Finger Node

Example for the **index finger**:

```bash
ros2 run coin_haptics_ros2 coin_motor_serial_node
ros2 run coin_haptics_ros2 tss_to_coin_motor_node \
  --ros-args \
  -p sensor_hand:=right \
  -p finger_name:=index \
  -p sensor_topic:=/taxel_1
```

if necessary, 
```bash
ros2 service call /right/index/zero std_srvs/srv/Trigger
```

This configuration assumes:

* The index motor driver is wired to **Arduino D5**
* The index taxel publishes on **/taxel_1**

---

## Notes

* The motor index is determined strictly by the Arduino pin order.
* Do not change the motor order unless the Arduino firmware and serial node are updated together.
* For single-motor testing on D3, use `finger_name:=thumb`.

---

## Repository Structure

```
coin_haptics_ros2
├── coin_haptics_ros2
├── dependencies.repos
├── README.md
├── package.xml
├── setup.py
├── setup.cfg
└── test
```

