import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import PoseWithCovarianceStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
import numpy as np


class ExplorerNode(Node):
    def __init__(self):
        super().__init__('explorer')
        self.get_logger().info("Explorer Node Started")

        # Subscriber to the map topic
        self.map_sub = self.create_subscription(
            OccupancyGrid, '/map', self.map_callback, 10)

        # Subscriber to the robot's pose 
        self.pose_sub = self.create_subscription(
            PoseWithCovarianceStamped, '/amcl_pose', self.pose_callback, 10)

        # Action client for navigation
        self.nav_to_pose_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.visited_frontiers = set()
        self.map_data = None
        self.robot_position = (0, 0)  # (row, col) in map coordinates

        # Flag to prevent multiple simultaneous navigation goals
        self.navigation_active = False

        # Timer for periodic exploration
        self.timer = self.create_timer(5.0, self.explore)

    def map_callback(self, msg):
        self.map_data = msg
        self.get_logger().info("Map received")

    def pose_callback(self, msg: PoseWithCovarianceStamped):
        """
        Update robot position from AMCL pose.
        """
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y

        if self.map_data:
            # Convert world coords to map indices
            col = int((x - self.map_data.info.origin.position.x) / self.map_data.info.resolution)
            row = int((y - self.map_data.info.origin.position.y) / self.map_data.info.resolution)
            self.robot_position = (row, col)

    def navigate_to(self, x, y):
        """
        Send navigation goal to Nav2.
        """
        if self.navigation_active:
            self.get_logger().info("Navigation already in progress, skipping new goal.")
            return

        goal_msg = PoseStamped()
        goal_msg.header.frame_id = 'map'
        goal_msg.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.position.x = x
        goal_msg.pose.position.y = y
        goal_msg.pose.orientation.w = 1.0 

        nav_goal = NavigateToPose.Goal()
        nav_goal.pose = goal_msg

        self.get_logger().info(f"Navigating to goal: x={x:.2f}, y={y:.2f}")

        self.nav_to_pose_client.wait_for_server()
        self.navigation_active = True

        send_goal_future = self.nav_to_pose_client.send_goal_async(nav_goal)
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().warning("Goal rejected!")
            self.navigation_active = False
            return

        self.get_logger().info("Goal accepted")
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.navigation_complete_callback)

    def navigation_complete_callback(self, future):
        """
        Callback to handle the result of the navigation action.
        """
        try:
            result = future.result().result
            self.get_logger().info(f"Navigation completed with result: {result}")
        except Exception as e:
            self.get_logger().error(f"Navigation failed: {e}")
        finally:
            self.navigation_active = False

    def find_frontiers(self, map_array):
        """
        Detect frontiers in the occupancy grid map.
        """
        frontiers = []
        rows, cols = map_array.shape

        for r in range(1, rows - 1):
            for c in range(1, cols - 1):
                if map_array[r, c] == 0:  # Free cell
                    neighbors = map_array[r-1:r+2, c-1:c+2].flatten()
                    if -1 in neighbors:
                        frontiers.append((r, c))

        self.get_logger().info(f"Found {len(frontiers)} frontiers")
        return frontiers

    def choose_frontier(self, frontiers):
        """
        Choose the closest frontier to the robot.
        """
        robot_row, robot_col = self.robot_position
        min_distance = float('inf')
        chosen_frontier = None

        for frontier in frontiers:
            if frontier in self.visited_frontiers:
                continue

            distance = np.sqrt((robot_row - frontier[0])**2 + (robot_col - frontier[1])**2)
            if distance < min_distance:
                min_distance = distance
                chosen_frontier = frontier

        if chosen_frontier:
            self.visited_frontiers.add(chosen_frontier)
            self.get_logger().info(f"Chosen frontier: {chosen_frontier}")
        else:
            self.get_logger().warning("No valid frontier found")

        return chosen_frontier

    def explore(self):
        if self.map_data is None:
            self.get_logger().warning("No map data available")
            return

        if self.navigation_active:
            self.get_logger().info("Currently navigating, skipping exploration step")
            return

        map_array = np.array(self.map_data.data).reshape(
            (self.map_data.info.height, self.map_data.info.width))

        frontiers = self.find_frontiers(map_array)

        if not frontiers:
            self.get_logger().info("No frontiers found. Exploration complete!")
            return

        chosen_frontier = self.choose_frontier(frontiers)

        if not chosen_frontier:
            self.get_logger().warning("No frontiers to explore")
            return

        goal_x = chosen_frontier[1] * self.map_data.info.resolution + self.map_data.info.origin.position.x
        goal_y = chosen_frontier[0] * self.map_data.info.resolution + self.map_data.info.origin.position.y

        self.navigate_to(goal_x, goal_y)


def main(args=None):
    rclpy.init(args=args)
    explorer_node = ExplorerNode()

    try:
        explorer_node.get_logger().info("Starting exploration...")
        rclpy.spin(explorer_node)
    except KeyboardInterrupt:
        explorer_node.get_logger().info("Exploration stopped by user")
    finally:
        explorer_node.destroy_node()
        rclpy.shutdown()
