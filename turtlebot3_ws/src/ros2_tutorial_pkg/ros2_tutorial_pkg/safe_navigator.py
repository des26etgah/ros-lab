import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSDurabilityPolicy, QoSReliabilityPolicy
from geometry_msgs.msg import TwistStamped
from sensor_msgs.msg import LaserScan
from enum import Enum, auto


CMD_QOS = QoSProfile(
    depth=10,
    reliability=QoSReliabilityPolicy.RELIABLE,
    durability=QoSDurabilityPolicy.VOLATILE,
)


class State(Enum):
    FORWARD  = auto()
    BACKUP   = auto()
    TURN     = auto()


class SafeNavigator(Node):
    SAFETY_THRESHOLD: float = 0.35   # stop if closer than this
    NOMINAL_SPEED:    float = 0.2    # m/s forward
    BACKUP_SPEED:     float = -0.1   # m/s reverse
    TURN_RATE:        float = 0.8    # rad/s
    BACKUP_TIME:      float = 1.0    # seconds to reverse
    TURN_TIME:        float = 2.0    # seconds to turn (~90 deg)
    PUBLISH_RATE:     float = 0.1    # 10 Hz

    def __init__(self) -> None:
        super().__init__('safe_navigator')
        self.vel_pub = self.create_publisher(TwistStamped, '/cmd_vel', CMD_QOS)
        self.create_subscription(LaserScan, '/scan', self._scan_cb, 10)
        self.timer = self.create_timer(self.PUBLISH_RATE, self._publish_cmd)

        self._min_distance: float = float('inf')
        self._front_blocked: bool = False
        self._state: State = State.FORWARD
        self._state_elapsed: float = 0.0
        # alternate turn direction each time to avoid spinning in place
        self._turn_sign: float = 1.0

        self.get_logger().info('SafeNavigator ready.')

    def _scan_cb(self, msg: LaserScan) -> None:
        ranges = np.array(msg.ranges, dtype=float)
        valid = ranges[
            np.isfinite(ranges) &
            (ranges > msg.range_min) &
            (ranges < msg.range_max)
        ]
        if valid.size == 0:
            return

        self._min_distance = float(valid.min())

        # only consider the front 60 deg arc for blocking
        total = len(ranges)
        front_idx = list(range(0, total // 12)) + list(range(11 * total // 12, total))
        front = ranges[front_idx]
        front_valid = front[np.isfinite(front) & (front > msg.range_min)]
        self._front_blocked = (
            front_valid.size > 0 and float(front_valid.min()) < self.SAFETY_THRESHOLD
        )

    def _publish_cmd(self) -> None:
        cmd = TwistStamped()
        cmd.header.stamp = self.get_clock().now().to_msg()

        if self._state is State.FORWARD:
            if self._front_blocked:
                self.get_logger().warn(
                    f'Obstacle at {self._min_distance:.2f} m — backing up.')
                self._switch_to(State.BACKUP)
            else:
                cmd.twist.linear.x = self.NOMINAL_SPEED

        elif self._state is State.BACKUP:
            cmd.twist.linear.x = self.BACKUP_SPEED
            self._state_elapsed += self.PUBLISH_RATE
            if self._state_elapsed >= self.BACKUP_TIME:
                self._switch_to(State.TURN)

        elif self._state is State.TURN:
            cmd.twist.angular.z = self._turn_sign * self.TURN_RATE
            self._state_elapsed += self.PUBLISH_RATE
            if self._state_elapsed >= self.TURN_TIME:
                self._turn_sign *= -1.0   # alternate direction next time
                self._switch_to(State.FORWARD)

        self.vel_pub.publish(cmd)

    def _switch_to(self, state: State) -> None:
        self._state = state
        self._state_elapsed = 0.0
        self.get_logger().info(f'→ State: {state.name}')

    def stop(self) -> None:
        cmd = TwistStamped()
        cmd.header.stamp = self.get_clock().now().to_msg()
        self.vel_pub.publish(cmd)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = SafeNavigator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
