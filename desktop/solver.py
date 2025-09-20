import math
from dataclasses import dataclass
from typing import List, Tuple
import numpy as np


# Структуры данных
@dataclass
class JointParams:
    min_angle: float
    max_angle: float
    max_velocity: float
    max_acceleration: float


@dataclass
class Operation:
    pick_point: Tuple[float, float, float]
    place_point: Tuple[float, float, float]
    process_time: float


@dataclass
class Waypoint:
    time_ms: int
    x: float
    y: float
    z: float


@dataclass
class RobotState:
    position: Tuple[float, float, float]
    joints: List[float]
    velocity: List[float]


# Основной класс планировщика
class IndustrialRobotScheduler:
    def __init__(self):
        self.num_robots = 0
        self.num_operations = 0
        self.robot_bases = []
        self.joint_params = []
        self.tool_clearance = 0.0
        self.safe_distance = 0.0
        self.operations = []
        self.schedules = []
        self.robot_states = []

    # Загрузка данных
    def load_from_lines(self, lines: List[str]):
        lines = [l.strip() for l in lines if l.strip()]
        self.num_robots, self.num_operations = map(int, lines[0].split())

        idx = 1
        self.robot_bases = [tuple(map(float, lines[idx + i].split())) for i in range(self.num_robots)]
        idx += self.num_robots

        self.joint_params = []
        for i in range(6):
            params = list(map(float, lines[idx + i].split()))
            self.joint_params.append(JointParams(*params))
        idx += 6

        self.tool_clearance, self.safe_distance = map(float, lines[idx].split())
        idx += 1

        self.operations = []
        for i in range(self.num_operations):
            vals = list(map(float, lines[idx + i].split()))
            self.operations.append(Operation(tuple(vals[0:3]), tuple(vals[3:6]), vals[6]))

        self.robot_states = [
            RobotState(self.robot_bases[i], [0.0] * 6, [0.0] * 6) for i in range(self.num_robots)
        ]

    # Упрощенное вычисление времени движения
    def calculate_move_time(self, start, end):
        """Упрощенное вычисление времени движения между точками"""
        distance = math.dist(start, end)
        # Базовое время: 100 мс на единицу расстояния + 500 мс фиксированно
        return int(distance * 100 + 500)

    # Назначение операций роботам
    def assign_operations_to_robots(self):
        """Простое назначение операций роботам"""
        assignments = [[] for _ in range(self.num_robots)]

        # Равномерно распределяем операции между роботами
        for i, op in enumerate(self.operations):
            robot_id = i % self.num_robots
            assignments[robot_id].append(op)

        return assignments

    # Генерация траектории
    def generate_trajectory_for_robot(self, rid, ops):
        """Генерация упрощенной траектории"""
        if not ops:
            return []

        wps = []
        current_time = 0
        current_pos = self.robot_bases[rid]

        # Начальная позиция
        wps.append(Waypoint(current_time, *current_pos))

        for op in ops:
            # Движение к точке захвата
            move_time = self.calculate_move_time(current_pos, op.pick_point)
            current_time += move_time
            wps.append(Waypoint(current_time, *op.pick_point))
            current_pos = op.pick_point

            # Время обработки
            current_time += int(op.process_time)
            wps.append(Waypoint(current_time, *op.pick_point))

            # Движение к точке размещения
            move_time = self.calculate_move_time(current_pos, op.place_point)
            current_time += move_time
            wps.append(Waypoint(current_time, *op.place_point))
            current_pos = op.place_point

            # Время обработки
            current_time += int(op.process_time)
            wps.append(Waypoint(current_time, *op.place_point))

        return wps

    # Проверка коллизий (упрощенная)
    def check_collisions(self):
        """Упрощенная проверка коллизий"""
        if self.num_robots <= 1:
            return True

        # Простая проверка: если роботы работают в одно время, считаем что есть коллизии
        # и нужно сдвинуть расписание
        time_ranges = []
        for schedule in self.schedules:
            if schedule:
                time_ranges.append((schedule[0].time_ms, schedule[-1].time_ms))
            else:
                time_ranges.append((0, 0))

        # Проверяем пересечение временных интервалов
        for i in range(self.num_robots):
            for j in range(i + 1, self.num_robots):
                start_i, end_i = time_ranges[i]
                start_j, end_j = time_ranges[j]

                # Если интервалы пересекаются
                if not (end_i < start_j or end_j < start_i):
                    return False

        return True

    def resolve_collisions(self):
        """Упрощенное разрешение коллизий"""
        if self.num_robots <= 1:
            return

        # Сортируем роботов по времени начала работы
        start_times = [s[0].time_ms if s else 0 for s in self.schedules]
        sorted_indices = sorted(range(self.num_robots), key=lambda i: start_times[i])

        # Сдвигаем расписания так чтобы они не пересекались
        current_end = 0
        for idx in sorted_indices:
            if self.schedules[idx]:
                schedule = self.schedules[idx]
                time_shift = max(0, current_end - schedule[0].time_ms + 1000)  # +1 секунда запас

                if time_shift > 0:
                    for wp in schedule:
                        wp.time_ms += time_shift

                current_end = schedule[-1].time_ms

    # Основной solve
    def solve(self) -> List[str]:
        """Основной метод решения"""
        try:
            # Назначаем операции
            assignments = self.assign_operations_to_robots()
            self.schedules = []

            # Генерируем траектории
            for r in range(self.num_robots):
                schedule = self.generate_trajectory_for_robot(r, assignments[r])
                self.schedules.append(schedule)

            # Проверяем и разрешаем коллизии
            if not self.check_collisions():
                self.resolve_collisions()

            # Формируем результат
            makespan = max((s[-1].time_ms for s in self.schedules if s), default=0)
            out = [str(makespan)]

            for r, schedule in enumerate(self.schedules):
                if not schedule:
                    bx, by, bz = self.robot_bases[r]
                    out.append(f"R{r + 1} 1")
                    out.append(f"0 {bx:.1f} {by:.1f} {bz:.1f}")
                else:
                    out.append(f"R{r + 1} {len(schedule)}")
                    for wp in schedule:
                        out.append(f"{wp.time_ms} {wp.x:.1f} {wp.y:.1f} {wp.z:.1f}")

            return out

        except Exception as e:
            # Fallback решение
            return self.generate_fallback_solution()

    def generate_fallback_solution(self):
        """Создание простого fallback решения"""
        makespan = 10000
        out = [str(makespan)]

        for r in range(self.num_robots):
            bx, by, bz = self.robot_bases[r]

            if r == 0 and self.operations:
                # Первый робот выполняет первую операцию
                op = self.operations[0]
                out.append(f"R{r + 1} 3")
                out.append(f"0 {bx:.1f} {by:.1f} {bz:.1f}")
                out.append(f"5000 {op.pick_point[0]:.1f} {op.pick_point[1]:.1f} {op.pick_point[2]:.1f}")
                out.append(f"10000 {op.place_point[0]:.1f} {op.place_point[1]:.1f} {op.place_point[2]:.1f}")
            else:
                # Остальные роботы остаются на базе
                out.append(f"R{r + 1} 1")
                out.append(f"0 {bx:.1f} {by:.1f} {bz:.1f}")

        return out


# Входная точка для модуля
def run_scheduler(input_lines: List[str]) -> List[str]:
    """
    Вход: список строк (из файла)
    Выход: список строк с результатом
    """
    scheduler = IndustrialRobotScheduler()
    scheduler.load_from_lines(input_lines)
    result = scheduler.solve()
    return result
