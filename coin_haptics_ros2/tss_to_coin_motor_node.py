#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from std_msgs.msg import Bool
from std_msgs_stamped.msg import Float64Stamped
from tactile_sensor_msgs.msg import TactileSensor
from rcl_interfaces.msg import SetParametersResult
from std_srvs.srv import Trigger
from collections import deque
import numpy as np


class TSStoCoinMotorNode(Node):
    def __init__(self):
        super().__init__('tss_to_coin_motor_node')

        # ---------------- Parameters ----------------
        self.declare_parameter("sensor_hand", 'right')
        self.declare_parameter("finger_name", "default_finger")
        self.declare_parameter("sensor_topic", "/taxel_1")
        self.declare_parameter("sensor_feature_val_index", 1)
        self.declare_parameter("tss_min", 0.0)
        self.declare_parameter("tss_max", 0.07)    # 0.084
        self.declare_parameter("tss_deadband_threshold", 0.003) # 0009

        # ---------------- Read parameters ----------------
        self.sensor_hand = self.get_parameter("sensor_hand").value
        self.finger_name = self.get_parameter("finger_name").value
        self.sensor_topic = self.get_parameter("sensor_topic").value
        self.sensor_feature_val_index = self.get_parameter("sensor_feature_val_index").value
        self.tss_min = self.get_parameter("tss_min").value
        self.tss_max = self.get_parameter("tss_max").value
        self.tss_deadband_threshold = self.get_parameter("tss_deadband_threshold").value

        # ---------------- Publisher ----------------
        self.stim_pub = self.create_publisher(
            Float64Stamped,
            f"/coin_motor/{self.sensor_hand}/{self.finger_name}",
            10
        )

        # ---------------- Subscriber ----------------
        self.sensor_sub = self.create_subscription(
            TactileSensor,
            self.sensor_topic,
            self.sensor_callback,
            10
        )

        # ---------------- Baseline logic ----------------
        self.baseline_window = deque(maxlen=50)
        self.baseline_value = None
        self.baselining = True
        self.sensor_value = 0.0

        # ---------------- Baseline-safe callback group ----------------
        self.baseline_callback_group = MutuallyExclusiveCallbackGroup()

        # ---------------- Timer ----------------
        self.timer = self.create_timer(
            1.0 / 30.0,
            self.publish_stim_callback,
            callback_group=self.baseline_callback_group
        )

        # ---------------- Zero service ----------------
        self.zero_service = self.create_service(
            Trigger,
            f'/{self.sensor_hand}/{self.finger_name}/zero',
            self.zero_service_callback,
            callback_group=self.baseline_callback_group
        )

        # ---------------- Zero feedback ----------------
        self.zero_feedback_pub = self.create_publisher(
            Bool,
            f'/{self.sensor_hand}/{self.finger_name}/zero_feedback',
            10
        )

        # ---------------- Dynamic parameters ----------------
        self.add_on_set_parameters_callback(self.parameter_callback)

        self.get_logger().info(
            f"TSStoCoinMotorNode initialized for: {self.sensor_hand} Hand - {self.finger_name}"
        )

    # ================= Callbacks =================

    def sensor_callback(self, msg: TactileSensor):
        try:
            raw_val = msg.feature_values[self.sensor_feature_val_index]
        except IndexError:
            self.get_logger().warn("Feature index out of range.")
            return

        if self.baselining:
            self.baseline_window.append(raw_val)
            if len(self.baseline_window) == self.baseline_window.maxlen:
                self.baseline_value = sum(self.baseline_window) / len(self.baseline_window)
                self.baselining = False

                feedback_msg = Bool()
                feedback_msg.data = True
                self.zero_feedback_pub.publish(feedback_msg)

                self.get_logger().info(
                    f"[{self.finger_name}] Baseline established: "
                    f"{self.baseline_value:.5f}"
                )
            return

        self.sensor_value = max(raw_val - self.baseline_value, 0.0)

    def publish_stim_callback(self):
        val = self.sensor_value

        if val <= self.tss_deadband_threshold:
            stim_val = 0.0
        else:
            stim_val = np.interp(
                val,
                [self.tss_min, self.tss_max],
                [0.0, 1.0]
            )
            stim_val = float(np.clip(stim_val, 0.0, 1.0))

        msg = Float64Stamped()
        msg.data = stim_val
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.finger_name
        self.stim_pub.publish(msg)

        self.get_logger().info(
            f"[{self.finger_name}] Stim {stim_val:.3f} | "
            f"TSS {val:.5f}"
        )

    def zero_service_callback(self, request, response):
        self.get_logger().info(
            f"[{self.finger_name}] Zero service called. Resetting baseline."
        )

        self.baseline_window.clear()
        self.baseline_value = None
        self.baselining = True

        response.success = True
        response.message = "Baseline reset successfully."
        return response

    def parameter_callback(self, params):
        for param in params:
            if param.name == "tss_min":
                self.tss_min = param.value
            elif param.name == "tss_max":
                self.tss_max = param.value
            elif param.name == "tss_deadband_threshold":
                self.tss_deadband_threshold = param.value

        return SetParametersResult(successful=True)


def main(args=None):
    rclpy.init(args=args)
    node = TSStoCoinMotorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
