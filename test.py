import math
from dataclasses import dataclass
from typing import List, Tuple
import numpy as np
from scipy.optimize import minimize

try:
    import pulp
    PULP_AVAILABLE = True
except ImportError:
    PULP_AVAILABLE = False

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


class Vector3:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = float(x), float(y), float(z)

    def __add__(self, o):
        return Vector3(self.x + o.x, self.y + o.y, self.z + o.z)

    def to_tuple(self):
        return (self.x, self.y, self.z)


class Matrix4:
    def __init__(self, data=None):
        self.data = np.eye(4, dtype=float) if data is None else np.array(data, dtype=float)

    def multiply(self, other):
        return Matrix4(np.dot(self.data, other.data))

    def get_translation(self):
        v = self.data[0:3, 3]
        return Vector3(v[0], v[1], v[2])

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

        # DH-параметры UR5-подобного манипулятора
        self.dh_params = [
            [0.0, math.pi / 2, 0.089159, 0.0],
            [-0.425, 0.0, 0.0, 0.0],
            [-0.39225, 0.0, 0.0, 0.0],
            [0.0, math.pi / 2, 0.10915, 0.0],
            [0.0, -math.pi / 2, 0.09465, 0.0],
            [0.0, 0.0, 0.0823, 0.0]
        ]

        self.segment_length = 0.05
        self.collision_dt_ms = 5
        self.max_collision_iterations = 200

    # Загрузка данных
    def load_from_lines(self, lines: List[str]):
        lines = [l.strip() for l in lines if l.strip()]
        self.num_robots, self.num_operations = map(int, lines[0].split())

        idx = 1
        self.robot_bases = [tuple(map(float, lines[idx + i].split())) for i in range(self.num_robots)]
        idx += self.num_robots

        self.joint_params = [JointParams(*map(float, lines[idx + i].split())) for i in range(6)]
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

    # Математика: FK, IK
    def dh_transform(self, a, alpha, d, theta):
        ct, st, ca, sa = math.cos(theta), math.sin(theta), math.cos(alpha), math.sin(alpha)
        return Matrix4([
            [ct, -st * ca, st * sa, a * ct],
            [st, ct * ca, -ct * sa, a * st],
            [0.0, sa, ca, d],
            [0.0, 0.0, 0.0, 1.0]
        ])

    def forward_kinematics(self, joints_deg, robot_id):
        T = Matrix4()
        joints_rad = [math.radians(j) for j in joints_deg]
        for i in range(6):
            a, alpha, d, theta_off = self.dh_params[i]
            T = T.multiply(self.dh_transform(a, alpha, d, joints_rad[i] + theta_off))
        return (Vector3(*self.robot_bases[robot_id]) + T.get_translation()).to_tuple()

    def numeric_jacobian(self, joints_rad, robot_id, eps=1e-6):
        base = np.array(self.forward_kinematics([math.degrees(x) for x in joints_rad], robot_id))
        J = np.zeros((3, 6))
        for i in range(6):
            p = joints_rad.copy()
            p[i] += eps
            J[:, i] = (np.array(self.forward_kinematics([math.degrees(x) for x in p], robot_id)) - base) / eps
        return J

    def ik_cost(self, joints_rad, target, current, robot_id):
        pos = np.array(self.forward_kinematics([math.degrees(x) for x in joints_rad], robot_id))
        err = np.linalg.norm(pos - target)
        smooth = np.linalg.norm(joints_rad - current) if current is not None else 0
        try:
            s = np.linalg.svd(self.numeric_jacobian(joints_rad, robot_id), compute_uv=False)
            sing = 1e3 / (1e-8 + np.min(s)) if np.min(s) < 1e-3 else 0
        except Exception:
            sing = 0
        return err + 0.05 * smooth + 1e-6 * sing

    def solve_ik(self, target, current_joints, robot_id):
        target = np.array(target)
        init = np.zeros(6) if current_joints is None else np.radians(current_joints)
        bounds = [(math.radians(p.min_angle), math.radians(p.max_angle)) for p in self.joint_params]
        res = minimize(self.ik_cost, init, args=(target, init, robot_id), bounds=bounds,
                       method='L-BFGS-B', options={'maxiter': 200})
        if res.success:
            sol = np.degrees(res.x)
            for i, a in enumerate(sol):
                if not (self.joint_params[i].min_angle <= a <= self.joint_params[i].max_angle):
                    return None
            return list(sol)
        return None

    def joint_time(self, delta, idx):
        p = self.joint_params[idx]
        v, a = math.radians(p.max_velocity), math.radians(p.max_acceleration)
        s = abs(delta)
        t_acc = v / a
        s_acc = 0.5 * a * t_acc ** 2
        if 2 * s_acc >= s:
            return 2 * math.sqrt(s / a)
        return 2 * t_acc + (s - 2 * s_acc) / v

    def move_time(self, start, end, rid, start_joints=None):
        if start_joints is None:
            start_joints = self.robot_states[rid].joints
        s = self.solve_ik(start, start_joints, rid) or start_joints
        e = self.solve_ik(end, s, rid)
        if e is None:
            return float("inf")
        return max(self.joint_time(abs(math.radians(e[i] - s[i])), i) for i in range(6)) * 1000

    # Назначение операций
    def assign_operations_to_robots(self):
        N, K = self.num_operations, self.num_robots
        reachable = [[False] * K for _ in range(N)]
        cost = [[float("inf")] * K for _ in range(N)]
        for i, op in enumerate(self.operations):
            for r in range(K):
                if self.solve_ik(op.pick_point, self.robot_states[r].joints, r) and \
                   self.solve_ik(op.place_point, self.robot_states[r].joints, r):
                    reachable[i][r] = True
                    cost[i][r] = self.move_time(self.robot_bases[r], op.pick_point, r) + \
                                 self.move_time(op.pick_point, op.place_point, r) + op.process_time * 2

        if PULP_AVAILABLE:
            prob = pulp.LpProblem("assign", pulp.LpMinimize)
            x = {(i, r): pulp.LpVariable(f"x_{i}_{r}", cat="Binary") for i in range(N) for r in range(K)}
            makespan = pulp.LpVariable("makespan", lowBound=0)
            prob += makespan
            for i in range(N):
                prob += sum(x[(i, r)] for r in range(K)) == 1
            for r in range(K):
                prob += sum(cost[i][r] * x[(i, r)] for i in range(N)) <= makespan
            for i in range(N):
                for r in range(K):
                    if not reachable[i][r]:
                        prob += x[(i, r)] == 0
            prob.solve(pulp.PULP_CBC_CMD(msg=False))
            res = [[] for _ in range(K)]
            for i in range(N):
                for r in range(K):
                    if pulp.value(x[(i, r)]) > 0.5:
                        res[r].append(self.operations[i])
            return res

        res = [[] for _ in range(K)]
        times = [0] * K
        pos = [self.robot_bases[r] for r in range(K)]
        for op in self.operations:
            best, bestt = None, float("inf")
            for r in range(K):
                if not reachable[self.operations.index(op)][r]:
                    continue
                t = times[r] + self.move_time(pos[r], op.pick_point, r) + \
                    self.move_time(op.pick_point, op.place_point, r) + op.process_time * 2
                if t < bestt:
                    best, bestt = r, t
            res[best].append(op)
            times[best] = bestt
            pos[best] = op.place_point
        return res

    # Траектории
    def interpolate(self, a, b):
        d = math.dist(a, b)
        n = max(1, int(d / self.segment_length))
        return [(a[0] + (b[0] - a[0]) * t / n,
                 a[1] + (b[1] - a[1]) * t / n,
                 a[2] + (b[2] - a[2]) * t / n) for t in range(1, n + 1)]

    def generate_trajectory_for_robot(self, rid, ops):
        wps = []
        t = 0
        pos = self.robot_states[rid].position
        joints = self.robot_states[rid].joints
        wps.append(Waypoint(t, *pos))
        for op in ops:
            for pt in self.interpolate(pos, op.pick_point):
                t += int(self.move_time(pos, pt, rid, joints))
                wps.append(Waypoint(t, *pt))
                pos = pt
                joints = self.solve_ik(pt, joints, rid) or joints
            t += int(op.process_time)
            wps.append(Waypoint(t, *op.pick_point))
            for pt in self.interpolate(op.pick_point, op.place_point):
                t += int(self.move_time(pos, pt, rid, joints))
                wps.append(Waypoint(t, *pt))
                pos = pt
                joints = self.solve_ik(pt, joints, rid) or joints
            t += int(op.process_time)
            wps.append(Waypoint(t, *op.place_point))
            pos = op.place_point
        return wps

    # Коллизии
    def get_pos_at(self, sched, t):
        if not sched:
            return (0, 0, 0)
        if t <= sched[0].time_ms:
            return (sched[0].x, sched[0].y, sched[0].z)
        for i in range(len(sched) - 1):
            if sched[i].time_ms <= t <= sched[i + 1].time_ms:
                f = (t - sched[i].time_ms) / (sched[i + 1].time_ms - sched[i].time_ms)
                return (sched[i].x + f * (sched[i + 1].x - sched[i].x),
                        sched[i].y + f * (sched[i + 1].y - sched[i].y),
                        sched[i].z + f * (sched[i + 1].z - sched[i].z))
        return (sched[-1].x, sched[-1].y, sched[-1].z)

    def check_collisions(self):
        min_safe = self.safe_distance + 2 * self.tool_clearance
        windows = [(s[0].time_ms, s[-1].time_ms) if s else (0, 0) for s in self.schedules]
        for r1 in range(self.num_robots):
            for r2 in range(r1 + 1, self.num_robots):
                if windows[r1][1] < windows[r2][0] or windows[r2][1] < windows[r1][0]:
                    continue
                t = max(windows[r1][0], windows[r2][0])
                while t <= min(windows[r1][1], windows[r2][1]):
                    if math.dist(self.get_pos_at(self.schedules[r1], t),
                                 self.get_pos_at(self.schedules[r2], t)) < min_safe:
                        return False
                    t += self.collision_dt_ms
        return True

    def resolve_collisions(self):
        it = 0
        while not self.check_collisions() and it < self.max_collision_iterations:
            for r in range(self.num_robots):
                for wp in self.schedules[r]:
                    wp.time_ms += 200
            it += 1
        if not self.check_collisions():
            raise ValueError("Не удалось устранить коллизии")

    # Основной solve
    def solve(self) -> List[str]:
        assign = self.assign_operations_to_robots()
        self.schedules = [self.generate_trajectory_for_robot(r, assign[r]) for r in range(self.num_robots)]

        if self.num_robots > 1 and not self.check_collisions():
            self.resolve_collisions()

        makespan = max(s[-1].time_ms for s in self.schedules if s)
        out = [str(makespan)]

        for r, s in enumerate(self.schedules):
            if not s:
                bx, by, bz = self.robot_bases[r]
                out.append(f"R{r + 1} 1")
                out.append(f"0 {bx:.1f} {by:.1f} {bz:.1f}")
            else:
                out.append(f"R{r + 1} {len(s)}")
                for wp in s:
                    out.append(f"{wp.time_ms} {wp.x:.1f} {wp.y:.1f} {wp.z:.1f}")

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
