#!/usr/bin/env python3
import sys
import rospy
from PyQt5.QtCore import Qt
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QGridLayout, QTabWidget
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

# **Import lại HMI có sẵn**
from hmi import RobotMonitor  # Đảm bảo file hmi.py có class RobotMonitor

class RobotControlGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Robot Control Panel")
        self.setGeometry(100, 100, 1200, 800)  

        # **ROS Node**
        rospy.init_node("robot_teleop_gui", anonymous=True)
        self.pub = rospy.Publisher("/cmd_vel", Twist, queue_size=100)
        self.vel_msg = Twist()

        # **Tạo Tab**
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # **Tab 1: Điều Khiển Robot**
        self.control_tab = QWidget()
        self.tabs.addTab(self.control_tab, "Điều Khiển")

        control_layout = QVBoxLayout()

        # **Nút Multi Goal**
        self.btn_goal = QPushButton("Multi Goal")
        self.btn_goal.clicked.connect(self.run_goal_sender)
        control_layout.addWidget(self.btn_goal)

        # **Nút mở HMI**
        self.btn_hmi = QPushButton("Xem Dữ Liệu")
        self.btn_hmi.clicked.connect(self.show_data_tab)  # Chỉnh sửa
        control_layout.addWidget(self.btn_hmi)

        # **Nút điều khiển robot**
        grid_layout = QGridLayout()

        self.btn_forward = QPushButton("W (Tiến)")
        self.btn_backward = QPushButton("S (Lùi)")
        self.btn_left = QPushButton("A (Trái)")
        self.btn_right = QPushButton("D (Phải)")

        # Gán sự kiện nhấn và thả
        self.btn_forward.pressed.connect(lambda: self.move_robot(0.2, 0))
        self.btn_forward.released.connect(self.stop_robot)

        self.btn_backward.pressed.connect(lambda: self.move_robot(-0.2, 0))
        self.btn_backward.released.connect(self.stop_robot)

        self.btn_left.pressed.connect(lambda: self.move_robot(0, 0.5))
        self.btn_left.released.connect(self.stop_robot)

        self.btn_right.pressed.connect(lambda: self.move_robot(0, -0.5))
        self.btn_right.released.connect(self.stop_robot)

        # Sắp xếp layout
        grid_layout.addWidget(self.btn_left, 1, 0)
        grid_layout.addWidget(self.btn_forward, 0, 1)
        grid_layout.addWidget(self.btn_backward, 2, 1)
        grid_layout.addWidget(self.btn_right, 1, 2)

        control_layout.addLayout(grid_layout)
        self.control_tab.setLayout(control_layout)

        # **Tab 2: Nhúng lại HMI**
        self.data_tab = RobotMonitor()
        self.tabs.addTab(self.data_tab, "Dữ Liệu Robot")

        # **ROS Subscriber**
        rospy.Subscriber("/odom", Odometry, self.odom_callback)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_W:
            self.move_robot(0.2, 0)
        elif key == Qt.Key_S:
            self.move_robot(-0.2, 0)
        elif key == Qt.Key_A:
            self.move_robot(0, 0.5)
        elif key == Qt.Key_D:
            self.move_robot(0, -0.5)
        elif key == Qt.Key_Escape:
            self.showNormal()  # Nhấn ESC để thoát full màn hình

    def keyReleaseEvent(self, event):
        key = event.key()
        if key in [Qt.Key_W, Qt.Key_S, Qt.Key_A, Qt.Key_D]:
            self.stop_robot()

    def move_robot(self, linear, angular):
        """Di chuyển robot với vận tốc truyền vào"""
        self.vel_msg.linear.x = linear
        self.vel_msg.angular.z = angular
        self.pub.publish(self.vel_msg)

    def stop_robot(self):
        """Dừng robot khi thả nút"""
        self.vel_msg.linear.x = 0
        self.vel_msg.angular.z = 0
        self.pub.publish(self.vel_msg)

    def run_goal_sender(self):
        """Chạy chương trình gửi mục tiêu"""
        subprocess.Popen(["rosrun", "mobile", "multi_goal_nav.py"])

    def show_data_tab(self):
        """Chuyển sang tab dữ liệu + Full màn hình"""
        self.tabs.setCurrentIndex(1)
        self.showFullScreen()  # Full màn hình khi mở dữ liệu

    def odom_callback(self, msg):
        """Cập nhật dữ liệu vào HMI"""
        self.data_tab.odom_callback(msg)  # Gửi dữ liệu cho HMI luôn

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RobotControlGUI()
    window.show()
    sys.exit(app.exec_())
