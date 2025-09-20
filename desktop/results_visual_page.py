from PySide6.QtWidgets import QWidget, QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem
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
        self.coord_labels = {}  # {r_id: QGraphicsTextItem for coordinates}
        self.base_labels = []  # List of QGraphicsTextItem for bases
        self.pick_place_labels = []  # List of QGraphicsTextItem for pick/place points
        self.scale_factor = 10
        self.view_scale = 1.0  # Initial view scale (100%)
        self.is_animating = False
        self.step_size = 50  # Smaller step size for smoother animation

        self.init_ui()

    def init_ui(self):
        self.play_pushButton.clicked.connect(self.start_animation)
        self.pause_pushButton.clicked.connect(self.pause_animation)
        self.reset_pushButton.clicked.connect(self.reset_animation)
        self.time_horizontalSlider.valueChanged.connect(self.slider_moved)
        self.scale_slider.valueChanged.connect(self.scale_changed)
        self.view_speed_slider.valueChanged.connect(self.change_speed_timer)

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
        self.base_labels = []
        self.pick_place_labels = []
        self.coord_labels = {}
        self.manipulators = {}

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

        # Draw robot bases with labels
        for idx, base in enumerate(self.robot_bases):
            ellipse = self.scene.addEllipse(base[0] * self.scale_factor - 5, base[1] * self.scale_factor - 5,
                                            10, 10, QPen(Qt.darkGray, 1), QBrush(Qt.darkGray))
            label = self.scene.addText(f"База R{idx + 1}")
            label.setDefaultTextColor(Qt.darkGray)
            label.setPos(base[0] * self.scale_factor + 5, base[1] * self.scale_factor + 5)
            self.base_labels.append(label)

        # Draw trajectories
        for r_id, waypoints in self.robots.items():
            # Generate unique color for each robot
            hue = (int(r_id[1:]) - 1) * 137 % 360  # Golden angle for color distribution
            color = QColor.fromHsv(hue, 200, 200)
            pen = QPen(color, 1)
            pen.setWidthF(1.5)  # Slightly thicker line for visibility
            for i in range(len(waypoints) - 1):
                wp1, wp2 = waypoints[i], waypoints[i + 1]
                self.scene.addLine(wp1['x'] * self.scale_factor, wp1['y'] * self.scale_factor,
                                   wp2['x'] * self.scale_factor, wp2['y'] * self.scale_factor,
                                   pen)

        # Draw pick/place points with labels
        for idx, op in enumerate(self.operations):
            pick_ellipse = self.scene.addEllipse(op['pick'][0] * self.scale_factor - 3,
                                                 op['pick'][1] * self.scale_factor - 3,
                                                 6, 6, QPen(Qt.red, 1), QBrush(Qt.red))
            place_ellipse = self.scene.addEllipse(op['place'][0] * self.scale_factor - 3,
                                                  op['place'][1] * self.scale_factor - 3,
                                                  6, 6, QPen(Qt.darkGreen, 1), QBrush(Qt.darkGreen))
            pick_label = self.scene.addText(f"Захват {idx + 1}")
            pick_label.setDefaultTextColor(Qt.red)
            pick_label.setPos(op['pick'][0] * self.scale_factor + 5, op['pick'][1] * self.scale_factor + 5)
            place_label = self.scene.addText(f"Установка {idx + 1}")
            place_label.setDefaultTextColor(Qt.darkGreen)
            place_label.setPos(op['place'][0] * self.scale_factor + 5, op['place'][1] * self.scale_factor + 5)
            self.pick_place_labels.append(pick_label)
            self.pick_place_labels.append(place_label)

        # Initialize manipulators and coord labels dynamically
        for r_id in self.robots.keys():
            # Generate unique color
            hue = (int(r_id[1:]) - 1) * 137 % 360
            color = QColor.fromHsv(hue, 200, 200)
            manipulator = self.scene.addEllipse(0, 0, 8, 8, QPen(color, 1), QBrush(color))
            self.manipulators[r_id] = manipulator

            coord_label = self.scene.addText(f"{r_id}: (0, 0, 0)")
            coord_label.setDefaultTextColor(color)
            self.coord_labels[r_id] = coord_label

        self.update_positions()

    def change_speed_timer(self):
        if self.is_animating:
            self.timer.start(100 - self.view_speed_slider.value())

    def start_animation(self):
        if self.current_time >= self.makespan:
            self.reset_animation()
        self.is_animating = True

        self.change_speed_timer()

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
        if not self.manipulators:
            return
        for r_id, waypoints in self.robots.items():
            if r_id in self.manipulators:
                pos = self.interpolate_position(waypoints, self.current_time)
                base_size = 8
                z = self.interpolate_z(waypoints, self.current_time)
                size = base_size + z / 10  # Adjust size based on Z (scale as needed)
                self.manipulators[r_id].setRect(pos[0] * self.scale_factor - size / 2,
                                                pos[1] * self.scale_factor - size / 2,
                                                size, size)
                # Update coord label
                self.coord_labels[r_id].setPlainText(f"{r_id}: ({pos[0]:.1f}, {pos[1]:.1f}, {z:.1f})")
                self.coord_labels[r_id].setPos(pos[0] * self.scale_factor + 5, pos[1] * self.scale_factor + 5)

    @staticmethod
    def interpolate_position(waypoints, t):
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

    @staticmethod
    def interpolate_z(waypoints, t):
        if not waypoints:
            return 0
        for i in range(len(waypoints) - 1):
            if waypoints[i]['t'] <= t <= waypoints[i + 1]['t']:
                wp1, wp2 = waypoints[i], waypoints[i + 1]
                frac = (t - wp1['t']) / (wp2['t'] - wp1['t']) if wp2['t'] != wp1['t'] else 0
                z = wp1['z'] + frac * (wp2['z'] - wp1['z'])
                return z
        return waypoints[-1]['z']

    def scale_changed(self, value):
        scale = value / 100.0  # Convert to scale factor (0.5 to 2.0)
        self.graphicsView.scale(scale / self.view_scale, scale / self.view_scale)
        self.view_scale = scale
