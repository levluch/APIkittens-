from PySide6.QtWidgets import QWidget, QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPen, QBrush, QColor
from desktop.ui_py.ui_results_visual_page import Ui_results_visual_page


class ResultsVisualPage(QWidget, Ui_results_visual_page):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.scene = QGraphicsScene(self)
        self.graphicsView.setScene(self.scene)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.current_time = 0
        self.makespan = 0
        self.robots = {}
        self.operations = []
        self.robot_bases = []
        self.manipulators = {}
        self.scale_factor = 10
        self.is_animating = False
        self.step_size = 50  # Smaller step size for smoother animation

        self.init_ui()

    def init_ui(self):
        self.play_pushButton.clicked.connect(self.start_animation)
        self.pause_pushButton.clicked.connect(self.pause_animation)
        self.reset_pushButton.clicked.connect(self.reset_animation)
        self.time_horizontalSlider.valueChanged.connect(self.slider_moved)

    def display_results(self, results, operations=None, robot_bases=None):
        self.makespan, self.robots = self.parse_results(results)
        self.operations = operations or []
        self.robot_bases = robot_bases or []
        self.time_horizontalSlider.setMaximum(self.makespan)
        self.makespan_label.setText(f"Makespan: {self.makespan} мс")
        self.reset_animation()
        self.draw_scene()

    def parse_results(self, results):
        makespan = int(results[0])
        robots = {}
        i = 1
        while i < len(results):
            r_id, m = results[i].split()
            m = int(m)
            robots[r_id] = []
            for j in range(i + 1, i + m + 1):
                t, x, y, z = map(float, results[j].split())
                robots[r_id].append({'t': int(t), 'x': x, 'y': y, 'z': z})
            i += m + 1
        return makespan, robots

    def draw_scene(self):
        self.scene.clear()
        all_x = [wp['x'] for r in self.robots.values() for wp in r] + \
                [op['pick'][0] for op in self.operations] + \
                [op['place'][0] for op in self.operations] + \
                [base[0] for base in self.robot_bases]
        all_y = [wp['y'] for r in self.robots.values() for wp in r] + \
                [op['pick'][1] for op in self.operations] + \
                [op['place'][1] for op in self.operations] + \
                [base[1] for base in self.robot_bases]
        min_x, max_x = (min(all_x, default=0) - 10, max(all_x, default=10)) if all_x else (-10, 10)
        min_y, max_y = (min(all_y, default=0) - 10, max(all_y, default=10)) if all_y else (-10, 10)
        self.scene.setSceneRect(min_x * self.scale_factor, min_y * self.scale_factor,
                               (max_x - min_x) * self.scale_factor, (max_y - min_y) * self.scale_factor)

        for base in self.robot_bases:
            self.scene.addEllipse(base[0] * self.scale_factor - 5, base[1] * self.scale_factor - 5,
                                 10, 10, QPen(Qt.black), QBrush(Qt.black))

        for r_id, waypoints in self.robots.items():
            color = QColor(Qt.blue) if r_id == 'R1' else QColor(Qt.green)
            for i in range(len(waypoints) - 1):
                wp1, wp2 = waypoints[i], waypoints[i + 1]
                self.scene.addLine(wp1['x'] * self.scale_factor, wp1['y'] * self.scale_factor,
                                  wp2['x'] * self.scale_factor, wp2['y'] * self.scale_factor,
                                  QPen(color, 1))

        for op in self.operations:
            self.scene.addEllipse(op['pick'][0] * self.scale_factor - 3, op['pick'][1] * self.scale_factor - 3,
                                 6, 6, QPen(Qt.red), QBrush(Qt.red))
            self.scene.addEllipse(op['place'][0] * self.scale_factor - 3, op['place'][1] * self.scale_factor - 3,
                                 6, 6, QPen(Qt.darkGreen), QBrush(Qt.darkGreen))

        # Initialize manipulators dynamically based on robots
        self.manipulators = {r_id: self.scene.addEllipse(0, 0, 8, 8, QPen(color), QBrush(color))
                            for r_id, color in [(r_id, QColor(Qt.blue) if r_id == 'R1' else QColor(Qt.green))
                                                for r_id in self.robots.keys()]}
        self.update_positions()

    def start_animation(self):
        if self.current_time >= self.makespan:
            self.reset_animation()
        self.is_animating = True
        self.timer.start(100)  # Slower timer interval: 1000ms

    def pause_animation(self):
        self.is_animating = False
        self.timer.stop()

    def reset_animation(self):
        self.is_animating = False
        self.timer.stop()
        self.current_time = 0
        self.time_horizontalSlider.setValue(0)
        self.time_label.setText(f"Текущее время: {self.current_time} мс")
        self.update_positions()

    def slider_moved(self, value):
        self.current_time = value
        self.time_label.setText(f"Текущее время: {self.current_time} мс")
        self.update_positions()

    def update_animation(self):
        if self.is_animating:
            self.current_time += self.step_size
            if self.current_time > self.makespan:
                self.current_time = self.makespan
                self.pause_animation()
            self.time_horizontalSlider.setValue(self.current_time)
            self.time_label.setText(f"Текущее время: {self.current_time} мс")
            self.update_positions()

    def update_positions(self):
        if not self.manipulators:  # Avoid KeyError if no manipulators
            return
        for r_id, waypoints in self.robots.items():
            if r_id in self.manipulators:  # Check if manipulator exists
                pos = self.interpolate_position(waypoints, self.current_time)
                self.manipulators[r_id].setRect(pos[0] * self.scale_factor - 4,
                                              pos[1] * self.scale_factor - 4, 8, 8)

    def interpolate_position(self, waypoints, t):
        if not waypoints:
            return 0, 0
        for i in range(len(waypoints) - 1):
            if waypoints[i]['t'] <= t <= waypoints[i + 1]['t']:
                wp1, wp2 = waypoints[i], waypoints[i + 1]
                frac = (t - wp1['t']) / (wp2['t'] - wp1['t']) if wp2['t'] != wp1['t'] else 0
                x = wp1['x'] + frac * (wp2['x'] - wp1['x'])
                y = wp1['y'] + frac * (wp2['y'] - wp1['y'])
                return x, y
        return waypoints[-1]['x'], waypoints[-1]['y']