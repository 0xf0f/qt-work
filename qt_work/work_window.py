from . import qt

import threading
import multiprocessing

from .work_process import WorkProcess
from .qtextoutput import QTextOutput


class OutputThread(threading.Thread):
    class Signals(qt.QObject):
        output_received = qt.pyqtSignal(object)

    def __init__(self, output_queue: multiprocessing.Queue):
        super().__init__()
        self.setDaemon(True)
        self.output_queue = output_queue
        self.signals = OutputThread.Signals()

    def run(self):
        while True:
            output = self.output_queue.get(block=True)
            self.signals.output_received.emit(output)


class WorkProcessWaitThread(threading.Thread):
    class Signals(qt.QObject):
        finished = qt.pyqtSignal()

    def __init__(self, process: WorkProcess):
        super().__init__()
        self.setDaemon(True)

        self.process = process
        self.signals = WorkProcessWaitThread.Signals()

    def run(self):
        self.process.join()
        self.signals.finished.emit()


class WorkWindow(qt.QWidget):
    work_complete = qt.pyqtSignal()

    def __init__(self, input_queue, output_queue, process_type=WorkProcess):
        super().__init__()

        self.input_queue: multiprocessing.Queue = input_queue
        self.output_queue: multiprocessing.Queue = output_queue

        self.stdout = QTextOutput()
        self.stdout_queue: multiprocessing.Queue = multiprocessing.Queue()
        self.stdout_queue.cancel_join_thread()
        self.stdout_thread = OutputThread(self.stdout_queue)
        self.stdout_thread.signals.output_received.connect(self.stdout.write)
        self.stdout_thread.start()

        self.work_process = process_type(self.input_queue, self.output_queue, self.stdout_queue)
        self.work_process_wait_thread = WorkProcessWaitThread(self.work_process)
        # try:
        #     self.work_process_wait_thread.signals.finished.connect(self.work_complete.emit)
        # except AttributeError:
        #     pass

        self.pause_button = qt.QPushButton()
        self.pause_button.setCheckable(True)
        self.pause_button.setText('Pause')
        self.pause_button.toggled.connect(self.work_process.set_paused)

        self.vboxlayout = qt.QVBoxLayout(self)
        self.vboxlayout.addWidget(self.stdout)
        self.vboxlayout.addWidget(self.pause_button)

        self.setWindowTitle(self.work_process.name)
        # self.setMinimumHeight(256)
        # self.setWindowFlag(qt.constants.SubWindow)

    def closeEvent(self, event: qt.QCloseEvent):
        self.input_queue.cancel_join_thread()
        self.output_queue.cancel_join_thread()
        try:
            self.work_process.kill()
        except:
            pass

        super().closeEvent(event)

    def start_work(self):
        self.work_process.start()
        self.work_process_wait_thread.start()
