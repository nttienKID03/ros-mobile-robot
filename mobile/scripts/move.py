from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import QProcess

class MoveBaseControl(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.move_base_process = None

    def initUI(self):
        self.setWindowTitle("Move Base Controller")
        self.setGeometry(100, 100, 300, 200)

        self.btn_start = QPushButton("Start Move Base", self)
        self.btn_stop = QPushButton("Stop Move Base", self)

        self.btn_start.clicked.connect(self.start_move_base)
        self.btn_stop.clicked.connect(self.stop_move_base)

        layout = QVBoxLayout()
        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_stop)
        self.setLayout(layout)

    def start_move_base(self):
        if not self.move_base_process:
            self.move_base_process = QProcess(self)
            self.move_base_process.start("bash", ["-c", "roslaunch mobile move_base.launch"])
            print("🚀 Move Base started!")

    def stop_move_base(self):
        if self.move_base_process:
            self.move_base_process.terminate()
            self.move_base_process.waitForFinished()
            self.move_base_process = None
            print("🛑 Move Base stopped!")

if __name__ == "__main__":
    app = QApplication([])
    window = MoveBaseControl()
    window.show()
    app.exec_()
