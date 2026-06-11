import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class LaserSubscriber(Node):
    SAFETY_THRESHOLD: float = 0.35

    def __init__(self) -> None:
        super().__init__('laser_subscriber')
        self.subscription = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10)
        self.min_distance: float = float('inf')
        self.scan_count: int = 0
        self.get_logger().info('LaserSubscriber started.')

    def scan_callback(self, msg: LaserScan) -> None:
        self.scan_count += 1
        ranges = np.array(msg.ranges, dtype=float)
        valid = ranges[
            np.isfinite(ranges) &
            (ranges > msg.range_min) &
            (ranges < msg.range_max)
        ]
        if valid.size == 0:
            self.get_logger().warn('All ranges invalid.')
            return
        self.min_distance = float(valid.min())
        self.get_logger().info(
            f'[scan {self.scan_count:5d}] nearest: {self.min_distance:.3f} m')
        if self.min_distance < self.SAFETY_THRESHOLD:
            self.get_logger().warn(
                f'Obstacle within safety threshold! {self.min_distance:.3f} m')


def main(args=None) -> None:
    rclpy.init(args=args)
    node = LaserSubscriber()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
