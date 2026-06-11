import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped


class VelocityPublisher(Node):
    LINEAR_X: float = 0.2
    ANGULAR_Z: float = 0.5
    TIMER_PERIOD: float = 0.1

    def __init__(self) -> None:
        super().__init__('velocity_publisher')
        self.publisher_ = self.create_publisher(TwistStamped, '/cmd_vel', 10)
        self.timer = self.create_timer(self.TIMER_PERIOD, self.publish_velocity)
        self.counter: int = 0
        self.get_logger().info('VelocityPublisher started.')

    def publish_velocity(self) -> None:
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.twist.linear.x = self.LINEAR_X
        msg.twist.angular.z = self.ANGULAR_Z
        self.publisher_.publish(msg)
        self.counter += 1
        if self.counter % 10 == 0:
            self.get_logger().info(
                f'[{self.counter:5d}] linear.x={msg.twist.linear.x:.2f}  angular.z={msg.twist.angular.z:.2f}'
            )


def main(args=None) -> None:
    rclpy.init(args=args)
    node = VelocityPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
