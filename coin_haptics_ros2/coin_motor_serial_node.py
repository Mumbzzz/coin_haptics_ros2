#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs_stamped.msg import Float64Stamped
import serial
import threading

FINGER_TO_MOTOR = {
    "thumb":  0,
    "index":  1,
    "middle": 2,
    "ring":   3,
    "pinky":  4,
}

class CoinMotorSerialNode(Node):
    def __init__(self):
        super().__init__("coin_motor_serial_node")

        self.declare_parameter("serial_port", "/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_03536373332351B0D250-if00")
        self.declare_parameter("baud", 115200)
        self.declare_parameter("sensor_hand", "right")

        port = self.get_parameter("serial_port").value
        baud = self.get_parameter("baud").value
        self.sensor_hand = self.get_parameter("sensor_hand").value

        self.ser = serial.Serial(port, baud, timeout=0.01)
        self.lock = threading.Lock()
        self.stim = [0.0] * 5

        for finger, idx in FINGER_TO_MOTOR.items():
            self.create_subscription(
                Float64Stamped,
                f"/coin_motor/{self.sensor_hand}/{finger}",
                lambda msg, i=idx: self.update(i, msg.data),
                10
            )

        self.timer = self.create_timer(1.0 / 30.0, self.send)

        self.get_logger().info("CoinMotorSerialNode started")

    def update(self, index, value):
        self.stim[index] = max(0.0, min(1.0, value))

    def send(self):
        with self.lock:
            line = ",".join(f"{v:.3f}" for v in self.stim) + "\n"
            self.ser.write(line.encode("ascii"))

def main():
    rclpy.init()
    node = CoinMotorSerialNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
