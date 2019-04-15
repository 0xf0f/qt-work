from . import qt
import sip
import multiprocessing

from typing import List, Set
from .work_window import WorkWindow


class ManagerWindow(qt.QWidget):
    def __init__(self):
        super().__init__()

        self.start_button = qt.QPushButton()
        self.start_button.setText('Start Work')
        self.start_button.clicked.connect(self.start_work)
        self.work_started = False

        def pause_all(paused):
            for window in self.work_windows:
                if not sip.isdeleted(window):
                    window.pause_button.setChecked(paused)

        self.pause_all_button = qt.QPushButton()
        self.pause_all_button.setCheckable(True)
        self.pause_all_button.setText('Pause')
        self.pause_all_button.toggled.connect(pause_all)

        self.rearrange_button = qt.QPushButton()
        self.rearrange_button.setText('Rearrange Windows')
        self.rearrange_button.clicked.connect(self.arrange_windows)

        self.mdiarea = qt.QMdiArea()
        self.mdiarea.setActivationOrder(qt.QMdiArea.CreationOrder)

        self.vboxlayout = qt.QVBoxLayout(self)
        self.vboxlayout.addWidget(self.start_button)
        self.vboxlayout.addWidget(self.pause_all_button)
        self.vboxlayout.addWidget(self.rearrange_button)
        self.vboxlayout.addWidget(self.mdiarea)

        self.input_queue = multiprocessing.Queue()
        self.output_queue = multiprocessing.Queue()

        self.queues: Set[multiprocessing.Queue] = set()
        self.work_windows: List[WorkWindow] = []
        # self.setFixedWidth(256)

    def start_work(self):
        if not self.work_started:
            self.start_button.setEnabled(False)
            self.work_started = True

            for window in self.work_windows:
                window.show()
                window.start_work()

            self.arrange_windows()

    def add_window(self, window: WorkWindow):
        self.work_windows.append(window)

        self.queues.add(window.input_queue)
        self.queues.add(window.output_queue)

        mdi_subwindow: qt.QMdiSubWindow = self.mdiarea.addSubWindow(window)
        mdi_subwindow.setWindowFlag(qt.constants.FramelessWindowHint)

    def add_process(self, process_type, input_queue=None, output_queue=None):
        if input_queue is None:
            input_queue = self.input_queue

        if output_queue is None:
            output_queue = self.output_queue

        self.add_window(
            WorkWindow(input_queue, output_queue, process_type)
        )

    def add_queue(self, queue: multiprocessing.Queue):
        self.queues.append(queue)

    def arrange_windows(self):
        self.mdiarea.tileSubWindows()
        for window in self.work_windows:
            window.stdout.verticalScrollBar().setValue(
                window.stdout.verticalScrollBar().maximum()
            )
    #     screen: qt.QScreen = qt.qApp.primaryScreen()
    #     screen_geometry: qt.QRect = screen.availableGeometry()
    #
    #     x = 0
    #     y = 0
    #
    #     for window in self.work_windows:
    #         window.show()
    #
    #         window.move(
    #             screen_geometry.topLeft() + qt.QPoint(x, y)
    #         )
    #
    #         x += window.frameGeometry().width()
    #         if x > screen_geometry.width():
    #             x = 0
    #             y += window.frameGeometry().height()
    #

    def closeEvent(self, event: qt.QCloseEvent):
        for queue in self.queues:
            queue.cancel_join_thread()

        for window in self.work_windows:
            if not sip.isdeleted(window):
                window.close()

        super().closeEvent(event)
    #
    # def changeEvent(self, event: qt.QWindowStateChangeEvent):
    #     if (
    #             event.type() == event.WindowStateChange and
    #             event.oldState() & qt.constants.WindowMinimized
    #     ) or (
    #             event.type() == event.WindowActivate
    #     ):
    #         for window in self.work_windows:  # type: qt.QWidget
    #             window.show()
    #             window.raise_()
    #
    #     super().changeEvent(event)
