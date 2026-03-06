#!/usr/bin/env python3
import rospy
import sys
import tf.transformations as tf_trans
import math
import numpy as np
from nav_msgs.msg import Odometry
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGridLayout
from PyQt5.QtCore import QTimer
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class RobotMonitor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Robot Monitor")
        self.setGeometry(100, 100, 1200, 800)

        # Biến lưu dữ liệu
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.v = 0.0
        self.w = 0.0
        self.time_data = []
        self.x_data = []
        self.y_data = []
        self.v_data = []
        self.w_data = []
        self.yaw_data = []
        self.max_time_window = 15  # Giữ dữ liệu trong vòng 15 giây gần nhất

        # Tạo giao diện chính
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout chính
        main_layout = QGridLayout()
        self.central_widget.setLayout(main_layout)

        # Bên trái: Hiển thị số liệu
        self.label_x = QLabel("X: 0.0 m")
        self.label_y = QLabel("Y: 0.0 m")
        self.label_v = QLabel("Vận tốc dài: 0.0 m/s")
        self.label_w = QLabel("Vận tốc góc: 0.0 rad/s")
        self.label_yaw = QLabel("Góc quay Yaw: 0.0°")

        data_layout = QVBoxLayout()
        data_layout.addWidget(self.label_x)
        data_layout.addWidget(self.label_y)
        data_layout.addWidget(self.label_v)
        data_layout.addWidget(self.label_w)
        data_layout.addWidget(self.label_yaw)

        # Bên phải: 4 biểu đồ trong layout 2x2
        self.figure, self.axes = plt.subplots(2, 2, figsize=(12, 12))

        self.ax1 = self.axes[0, 0]
        self.ax2 = self.axes[0, 1]
        self.ax3 = self.axes[1, 0]
        self.ax4 = self.axes[1, 1]

        self.setup_plots()  # Thiết lập ban đầu cho biểu đồ

        self.canvas = FigureCanvas(self.figure)

        # Thêm vào layout chính
        main_layout.addLayout(data_layout, 0, 0)
        main_layout.addWidget(self.canvas, 0, 1)

        # **Di chuyển rospy.init_node() lên trên trước khi gọi rospy.get_time()**
        if not rospy.core.is_initialized():  # Kiểm tra nếu ROS chưa khởi tạo thì mới khởi tạo
            rospy.init_node("robot_monitor", anonymous=True)


        # **Sửa lỗi: Lấy mốc thời gian sau khi ROS đã khởi tạo**
        self.start_time = rospy.get_time()

        rospy.Subscriber("/odom", Odometry, self.odom_callback)

        # Timer cập nhật giao diện
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(100)

    def setup_plots(self):
        """Cấu hình ban đầu cho các biểu đồ"""
        self.ax1.set_title("Vị trí Robot (X, Y)")
        self.ax1.set_xlabel("X (m)")
        self.ax1.set_ylabel("Y (m)")
        self.ax1.xaxis.set_major_locator(MultipleLocator(0.5))
        self.ax1.yaxis.set_major_locator(MultipleLocator(0.5))
        self.ax1.grid(True)

        self.ax2.set_title("")
        self.ax2.set_xlabel("Thời gian (s)")
        self.ax2.set_ylabel("Vận tốc dài (m/s)")
        self.ax2.set_ylim(0, 0.3)
        self.ax2.yaxis.set_major_locator(MultipleLocator(0.08))
        self.ax2.grid(True)

        self.ax3.set_title("")
        self.ax3.set_xlabel("Thời gian (s)")
        self.ax3.set_ylabel("Vận tốc góc (rad/s)")
        self.ax3.set_ylim(-2.0, 2.0)
        self.ax3.yaxis.set_major_locator(MultipleLocator(0.5))
        self.ax3.grid(True)

        self.ax4.set_title("")
        self.ax4.set_xlabel("Thời gian (s)")
        self.ax4.set_ylabel("Yaw (°)")
        self.ax4.yaxis.set_major_locator(MultipleLocator(30))
        self.ax4.grid(True)

    def odom_callback(self, msg):
        """Nhận dữ liệu từ ROS topic"""
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        self.vx = msg.twist.twist.linear.x
        self.vy = msg.twist.twist.linear.y
        self.v = math.sqrt(self.vx**2 + self.vy**2)
        self.w = msg.twist.twist.angular.z

        # Lấy góc quay yaw từ quaternion
        orientation_q = msg.pose.pose.orientation
        quaternion = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
        _, _, yaw = tf_trans.euler_from_quaternion(quaternion)
        self.yaw = yaw * 180 / 3.1416  # Chuyển radian sang độ

        # Lấy thời gian hiện tại
        current_time = rospy.get_time() - self.start_time
        self.time_data.append(current_time)
        self.x_data.append(self.x)
        self.y_data.append(self.y)
        self.v_data.append(self.v)
        self.w_data.append(self.w)
        self.yaw_data.append(self.yaw)

        # Xóa dữ liệu cũ để đảm bảo chỉ hiển thị trong 15 giây gần nhất
        while len(self.time_data) > 0 and self.time_data[-1] - self.time_data[0] > self.max_time_window:
            self.time_data.pop(0)
            self.v_data.pop(0)
            self.w_data.pop(0)
            self.yaw_data.pop(0)

    def update_ui(self):
        """Cập nhật giao diện và vẽ đồ thị"""
        self.label_x.setText(f"X: {self.x:.2f} m")
        self.label_y.setText(f"Y: {self.y:.2f} m")
        self.label_v.setText(f"Vận tốc dài: {self.v:.2f} m/s")
        self.label_w.setText(f"Vận tốc góc: {self.w:.2f} rad/s")
        self.label_yaw.setText(f"Góc quay Yaw: {self.yaw:.2f}°")

        # Xóa và vẽ lại đồ thị
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.ax4.clear()
        self.setup_plots()

        if self.x_data and self.y_data:
            self.ax1.scatter(self.x_data[-1], self.y_data[-1], color="red", s=100, label="Vị trí hiện tại")  # Dấu chấm đỏ

        # **Sửa lỗi: Đảm bảo x_data và y_data có cùng độ dài**
        min_length = min(len(self.x_data), len(self.y_data))
        x_plot = self.x_data[:min_length]
        y_plot = self.y_data[:min_length]

        self.ax1.plot(x_plot, y_plot, color="blue", linewidth=1)
        self.ax2.plot(self.time_data, self.v_data, color="green", linewidth=1)
        self.ax3.plot(self.time_data, self.w_data, color="purple", linewidth=1)
        self.ax4.plot(self.time_data, self.yaw_data, color="red", linewidth=1)

        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RobotMonitor()
    window.show()
    sys.exit(app.exec_())
