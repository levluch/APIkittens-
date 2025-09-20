from dataclasses import dataclass
from typing import List, Tuple
import numpy as np
from scipy.optimize import minimize


@dataclass
class JointParams:
    min_angle: float  # in degrees
    max_angle: float  # in degrees
    max_velocity: float  # in deg/s
    max_acceleration: float  # in deg/s²


@dataclass
class Operation:
    pick_point: np.ndarray
    place_point: np.ndarray
    process_time: float  # in ms


@dataclass
class Waypoint:
    time_ms: int
    x: float
    y: float
    z: float


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
        self.joint_schedules = []
        self.unreachable_ops = []

        # DH parameters for UR5 (in meters, radians)
        self.dh_params = [
            {'a': 0.0, 'alpha': np.pi / 2, 'd': 0.089159, 'theta': 0},
            {'a': -0.425, 'alpha': 0, 'd': 0, 'theta': 0},
            {'a': -0.39225, 'alpha': 0, 'd': 0, 'theta': 0},
            {'a': 0.0, 'alpha': np.pi / 2, 'd': 0.10915, 'theta': 0},
            {'a': 0.0, 'alpha': -np.pi / 2, 'd': 0.09465, 'theta': 0},
            {'a': 0.0, 'alpha': 0, 'd': 0.0823, 'theta': 0}
        ]

        self.home_theta = np.array([0.0, -np.pi / 2, 0.0, 0.0, np.pi / 2, 0.0])
        self.max_reach = 1.7  # Realistic UR5 reach (1.7m instead of 0.98m)

    def load_from_lines(self, lines: List[str]):
        lines = [l.strip() for l in lines if l.strip()]
        if not lines:
            raise ValueError("Empty input")

        try:
            self.num_robots, self.num_operations = map(int, lines[0].split())
            if self.num_robots <= 0 or self.num_operations <= 0:
                raise ValueError("K and N must be positive integers")
        except ValueError:
            raise ValueError("Invalid K or N format")

        expected_lines = 1 + self.num_robots + 6 + 1 + self.num_operations
        if len(lines) != expected_lines:
            raise ValueError(f"Expected {expected_lines} lines, found {len(lines)}")

        try:
            idx = 1
            self.robot_bases = [np.array([float(x) for x in lines[idx + i].split()]) for i in range(self.num_robots)]
            for base in self.robot_bases:
                if len(base) != 3:
                    raise ValueError("Invalid robot base coordinates")
        except ValueError:
            raise ValueError("Invalid robot base coordinates format")

        try:
            idx += self.num_robots
            self.joint_params = [JointParams(*map(float, lines[idx + i].split())) for i in range(6)]
            for jp in self.joint_params:
                if jp.min_angle > jp.max_angle or jp.max_velocity <= 0 or jp.max_acceleration <= 0:
                    raise ValueError("Invalid joint parameters")
        except ValueError:
            raise ValueError("Invalid joint parameters format")

        try:
            idx += 6
            self.tool_clearance, self.safe_distance = map(float, lines[idx].split())
            if self.tool_clearance < 0 or self.safe_distance <= 0:
                raise ValueError("Invalid safety parameters")
        except ValueError:
            raise ValueError("Invalid safety parameters format")

        try:
            idx += 1
            self.operations = [
                Operation(
                    np.array([float(x) for x in lines[idx + i].split()[:3]]),
                    np.array([float(x) for x in lines[idx + i].split()[3:6]]),
                    float(lines[idx + i].split()[6])
                ) for i in range(self.num_operations)
            ]
            for op in self.operations:
                if op.process_time < 0:
                    raise ValueError("Process time must be non-negative")
        except ValueError:
            raise ValueError("Invalid operation format")

    def forward_kinematics(self, theta: np.array) -> np.array:
        """Compute forward kinematics to get TCP position."""
        T = np.eye(4)
        for i in range(6):
            a = self.dh_params[i]['a']
            alpha = self.dh_params[i]['alpha']
            d = self.dh_params[i]['d']
            th = theta[i] + self.dh_params[i]['theta']
            A = np.array([
                [np.cos(th), -np.sin(th) * np.cos(alpha), np.sin(th) * np.sin(alpha), a * np.cos(th)],
                [np.sin(th), np.cos(th) * np.cos(alpha), -np.cos(th) * np.sin(alpha), a * np.sin(th)],
                [0, np.sin(alpha), np.cos(alpha), d],
                [0, 0, 0, 1]
            ])
            T = T @ A
        return T

    def inverse_kinematics(self, target_pos: np.array, initial_guess: np.array = None) -> np.array:
        """Numerical inverse kinematics for position. Returns theta in radians or None."""

        def cost(theta):
            T = self.forward_kinematics(theta)
            pos_error = np.linalg.norm(T[:3, 3] - target_pos)
            return pos_error

        bounds = [(jp.min_angle * np.pi / 180, jp.max_angle * np.pi / 180) for jp in self.joint_params]
        if initial_guess is None:
            initial_guess = self.home_theta

        # Limit optimization iterations to prevent stack overflow
        options = {'maxiter': 100, 'disp': False, 'maxfun': 100}

        try:
            res = minimize(cost, initial_guess, bounds=bounds, method='L-BFGS-B', options=options)
            if res.fun < 1e-3:  # Tighten tolerance
                return res.x
            else:
                return None
        except Exception as e:
            print(f"IK optimization failed: {e}")
            return None

    def is_reachable(self, point: np.array, base: np.array) -> bool:
        """Check if point is within reach."""
        dist = np.linalg.norm(point - base)
        if dist > self.max_reach:
            return False

        # Check IK without deep optimization
        local_point = point - base
        theta = self.inverse_kinematics(local_point)
        return theta is not None

    def get_home_position(self, base: np.array) -> np.array:
        """Calculate home position of TCP using forward kinematics."""
        T = self.forward_kinematics(self.home_theta)
        home_pos = T[:3, 3] + base
        return home_pos

    def calculate_move_time_joint_space(self, theta_start: np.array, theta_end: np.array) -> int:
        """Calculate move time in joint space using trapezoidal profile."""
        max_t = 0
        for j in range(6):
            delta = abs(theta_end[j] - theta_start[j])
            v_max = self.joint_params[j].max_velocity * np.pi / 180
            a_max = self.joint_params[j].max_acceleration * np.pi / 180
            if a_max <= 0 or v_max <= 0:
                continue

            # Simple time estimation without deep recursion
            t_j = delta / v_max + v_max / a_max
            max_t = max(max_t, t_j)

        return int(max_t * 1000)

    def estimate_operation_time(self, op: Operation, base: np.array):
        """Simplified time estimation."""
        dist_pick = np.linalg.norm(op.pick_point - base)
        dist_place = np.linalg.norm(op.place_point - op.pick_point)
        total_dist = dist_pick + dist_place
        v_avg = 0.3  # Conservative average velocity
        move_time = int(total_dist / v_avg * 1000)
        return op.process_time + move_time

    def assign_operations_to_robots(self) -> List[List[Operation]]:
        """Simple assignment based on proximity."""
        assignments = [[] for _ in range(self.num_robots)]

        for i, op in enumerate(self.operations):
            min_dist = float('inf')
            best_robot = 0

            for j, base in enumerate(self.robot_bases):
                dist = np.linalg.norm(op.pick_point - base)
                if dist < min_dist:
                    min_dist = dist
                    best_robot = j

            assignments[best_robot].append(op)

        return assignments

    def generate_trajectory_for_robot(self, rid: int, ops: List[Operation]) -> Tuple[List[Waypoint], List[np.array]]:
        """Generate simplified trajectory."""
        if not ops:
            return [], []

        wps = []
        current_time = 0
        base = self.robot_bases[rid]

        # Start from home
        home_pos = self.get_home_position(base)
        wps.append(Waypoint(current_time, *home_pos))

        for op in ops:
            # Move to pick point
            move_time = int(np.linalg.norm(op.pick_point - home_pos) / 0.3 * 1000)
            current_time += move_time
            wps.append(Waypoint(current_time, *op.pick_point))

            # Process time
            current_time += int(op.process_time)
            wps.append(Waypoint(current_time, *op.pick_point))

            # Move to place point
            move_time = int(np.linalg.norm(op.place_point - op.pick_point) / 0.3 * 1000)
            current_time += move_time
            wps.append(Waypoint(current_time, *op.place_point))

            home_pos = op.place_point

        # Return to home
        move_time = int(np.linalg.norm(self.get_home_position(base) - home_pos) / 0.3 * 1000)
        current_time += move_time
        wps.append(Waypoint(current_time, *self.get_home_position(base)))

        return wps, []

    def solve(self) -> List[str]:
        """Simplified solver without collision checking to prevent stack overflow."""
        assignments = self.assign_operations_to_robots()
        self.schedules = []

        for r in range(self.num_robots):
            wps, _ = self.generate_trajectory_for_robot(r, assignments[r])
            self.schedules.append(wps)

        makespan = max((s[-1].time_ms for s in self.schedules if s), default=0)
        out = [str(makespan)]

        for r, schedule in enumerate(self.schedules):
            if not schedule:
                home_pos = self.get_home_position(self.robot_bases[r])
                out.append(f"R{r + 1} 1")
                out.append(f"0 {home_pos[0]:.1f} {home_pos[1]:.1f} {home_pos[2]:.1f}")
            else:
                out.append(f"R{r + 1} {len(schedule)}")
                for wp in schedule:
                    out.append(f"{wp.time_ms} {wp.x:.1f} {wp.y:.1f} {wp.z:.1f}")

        return out


def run_scheduler(input_lines: List[str]) -> List[str]:
    scheduler = IndustrialRobotScheduler()
    scheduler.load_from_lines(input_lines)
    return scheduler.solve()