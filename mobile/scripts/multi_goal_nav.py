#!/usr/bin/env python3
import rospy
import yaml
import actionlib
import tf
import os
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from geometry_msgs.msg import Quaternion, PoseStamped, Point
from nav_msgs.msg import Path, Odometry
from visualization_msgs.msg import Marker
from tf.transformations import quaternion_from_euler

def load_waypoints(file_path):
    """ Đọc danh sách waypoints từ file YAML """
    with open(file_path, 'r') as f:
        waypoints = yaml.safe_load(f)['waypoints']
    return waypoints

def publish_path(waypoints):
    """ Xuất đường đi dự kiến lên RViz """
    planned_path_pub = rospy.Publisher("/planned_path", Path, queue_size=50)
    rospy.sleep(1)  # Chờ publisher khởi động
    path = Path()
    path.header.frame_id = "map"

    for wp in waypoints:
        pose = PoseStamped()
        pose.header.frame_id = "map"
        pose.pose.position.x = wp['x']
        pose.pose.position.y = wp['y']
        q = quaternion_from_euler(0, 0, wp['yaw'])
        pose.pose.orientation = Quaternion(*q)
        path.poses.append(pose)

    planned_path_pub.publish(path)
    rospy.loginfo("Quỹ đạo mong muốn đã gửi đến RViz.")

def publish_waypoints(waypoints):
    """ Hiển thị waypoint ban đầu bằng Marker hình tròn """
    marker_pub = rospy.Publisher("/waypoints_marker", Marker, queue_size=50)
    rospy.sleep(1)  # Chờ publisher khởi động

    for i, wp in enumerate(waypoints):
        marker = Marker()
        marker.header.frame_id = "map"
        marker.ns = "waypoints"
        marker.id = i
        marker.type = Marker.SPHERE  # Hình tròn
        marker.action = Marker.ADD
        marker.pose.position.x = wp['x']
        marker.pose.position.y = wp['y']
        marker.scale.x = 0.07  # Kích thước 7cm
        marker.scale.y = 0.07
        marker.scale.z = 0.07
        marker.color.r = 0.0
        marker.color.g = 1.0  # Xanh lá
        marker.color.b = 0.0
        marker.color.a = 1.0  # Hiển thị rõ ràng
        marker_pub.publish(marker)

    rospy.loginfo("Đã xuất waypoint lên RViz.")

def send_goal(client, x, y, yaw, tf_listener, arrived_pub):
    """ Gửi goal đến move_base và đợi hoàn thành """
    goal = MoveBaseGoal()
    goal.target_pose.header.frame_id = "map"
    goal.target_pose.header.stamp = rospy.Time.now()

    goal.target_pose.pose.position.x = x
    goal.target_pose.pose.position.y = y
    q = quaternion_from_euler(0, 0, yaw)
    goal.target_pose.pose.orientation = Quaternion(*q)

    rospy.loginfo(f"Đang di chuyển đến: x={x}, y={y}, yaw={yaw}")
    client.send_goal(goal)

    # Đợi move_base hoàn thành trước khi gửi goal tiếp theo
    client.wait_for_result()
    result = client.get_state()

    if result == 3:  # 3 = SUCCEEDED
        rospy.loginfo("Đã đến nơi!")
        publish_arrived_marker(tf_listener, arrived_pub)  # Đánh dấu vị trí từ base_footprint
    else:
        rospy.logwarn("Không đến được goal! Đang thử lại...")


def publish_arrived_marker(tf_listener, arrived_pub):
    """ Đánh dấu vị trí thực tế của robot (base_footprint) khi đến waypoint """
    try:
        # Lấy vị trí hiện tại của base_footprint trong hệ tọa độ map
        (trans, rot) = tf_listener.lookupTransform("map", "base_footprint", rospy.Time(0))
        x, y = trans[0], trans[1]

        marker = Marker()
        marker.header.frame_id = "map"
        marker.ns = "arrived_points"
        marker.id = int(x * 100 + y * 100)  # ID duy nhất cho mỗi điểm
        marker.type = Marker.SPHERE  # Hình tròn
        marker.action = Marker.ADD
        marker.pose.position.x = x
        marker.pose.position.y = y
        marker.scale.x = 0.07  # Kích thước nhỏ 7cm
        marker.scale.y = 0.07
        marker.scale.z = 0.07
        marker.color.r = 1.0  # Màu đỏ
        marker.color.g = 0.0
        marker.color.b = 0.0
        marker.color.a = 1.0  # Hiển thị rõ ràng

        arrived_pub.publish(marker)
        rospy.loginfo(f"Đánh dấu thực tế đã đến: x={x}, y={y}")

    except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
        rospy.logwarn("Không thể lấy vị trí từ base_footprint!")


def odom_callback(msg):
    """ Cập nhật quỹ đạo đã đi vào /odom_path """
    global odom_path, odom_path_pub
    pose = PoseStamped()
    pose.header.stamp = rospy.Time.now()
    pose.header.frame_id = "map"
    pose.pose = msg.pose.pose
    odom_path.poses.append(pose)  # Lưu lại toàn bộ quỹ đạo đã đi

    odom_path_pub.publish(odom_path)  # Xuất quỹ đạo đã đi lên RViz

def main():
    rospy.init_node("multi_goal_nav")

    global odom_path_pub, odom_path
    odom_path_pub = rospy.Publisher("/odom_path", Path, queue_size=100)
    arrived_pub = rospy.Publisher("/arrived_marker", Marker, queue_size=100)
    odom_path = Path()
    odom_path.header.frame_id = "map"

    rospy.Subscriber("/odom", Odometry, odom_callback)

    client = actionlib.SimpleActionClient("move_base", MoveBaseAction)
    rospy.loginfo("Đang chờ move_base...")
    client.wait_for_server()
    rospy.loginfo("Kết nối move_base thành công!")

    file_path = rospy.get_param("~waypoints_file", os.path.expanduser("~/catkin_ws/src/mobile/config/waypoints.yaml"))
    if not os.path.exists(file_path):
        rospy.logerr(f"❌ Không tìm thấy tệp: {file_path}")
    else:
        rospy.loginfo(f"✅ Đã tìm thấy tệp: {file_path}")
    waypoints = load_waypoints(file_path)

    publish_path(waypoints)  # Xuất planned_path
    publish_waypoints(waypoints)  # Xuất marker waypoint

    # Khởi tạo TF listener để lấy vị trí của base_footprint
    tf_listener = tf.TransformListener()
    rospy.sleep(2)  # Chờ TF ổn định

    # Gửi tất cả waypoint liên tục
    for wp in waypoints:
        send_goal(client, wp['x'], wp['y'], wp['yaw'], tf_listener, arrived_pub)
        rospy.sleep(0.5)  # Chờ 0.5 giây để tránh bị gián đoạn

    rospy.loginfo("Hoàn thành quỹ đạo!")
    rospy.spin()  # Node chạy liên tục để cập nhật đường đi


if __name__ == "__main__":
    main()
