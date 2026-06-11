import math
from enum import Enum, auto
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped


class Phase(Enum):
    DRIVING = auto()
    TURNING = auto()


class SquareDriver(Node):
    SPEED: float = 0.2
    TURN_RATE: float = 0.5
    SIDE_LENGTH: float = 1.0
    TIMER_PERIOD: float = 0.05

    def __init__(self) -> None:
        super().__init__('square_driver')
        self.publisher_ = self.create_publisher(TwistStamped, '/cmd_vel', 10)
        self.timer = self.create_timer(self.TIMER_PERIOD, self.control_loop)
        self.phase: Phase = Phase.DRIVING
        self.phase_elapsed: float = 0.0
        self.sides_completed: int = 0
        self.drive_duration = self.SIDE_LENGTH / self.SPEED
        self.turn_duration = (math.pi / 2.0) / self.TURN_RATE
        self.get_logger().info('SquareDriver started.')

    def control_loop(self) -> None:
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        if self.phase is Phase.DRIVING:
            msg.twist.linear.x = self.SPEED
            self.phase_elapsed += self.TIMER_PERIOD
            if self.phase_elapsed >= self.drive_duration:
                self._switch_to(Phase.TURNING)
        else:
            msg.twist.angular.z = self.TURN_RATE
            self.phase_elapsed += self.TIMER_PERIOD
            if self.phase_elapsed >= self.turn_duration:
                self.sides_completed += 1
                self.get_logger().info(f'Side {self.sides_completed} complete.')
                self._switch_to(Phase.DRIVING)
        self.publisher_.publish(msg)

    def _switch_to(self, next_phase: Phase) -> None:
        self.phase = next_phase
        self.phase_elapsed = 0.0
        self.get_logger().info(f'-> Phase: {next_phase.name}')


def main(args=None) -> None:
    rclpy.init(args=args)
    node = SquareDriver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
