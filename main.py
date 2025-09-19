"""
Тестовые данные для ввода.
2 1
0.0 0.0 0.0
1.5 0.0 0.0
-170 170 90 45
-120 120 90 45
-120 120 90 45
-170 170 90 45
-120 120 90 45
-170 170 90 45
0.1 0.2
0.5 0.5 0.5 1.0 1.0 1.0 500
"""
import math

class Scheduler:
    def __init__(self):
        self.num_robots = 0
        self.num_ops = 0
        self.bases = []
        self.joint_limits = []
        self.tool_clearance = 0.0
        self.safe_dist = 0.0
        self.ops = []
        self.schedules = []

    def load_data(self, lines):
        lines = [l.strip() for l in lines if l.strip()]
        self.num_robots, self.num_ops = map(int, lines[0].split())
        self.bases = [tuple(map(float, lines[i].split())) for i in range(1, 1 + self.num_robots)]
        self.joint_limits = [tuple(map(float, lines[i].split())) for i in range(1 + self.num_robots, 7 + self.num_robots)]
        self.tool_clearance, self.safe_dist = map(float, lines[7 + self.num_robots].split())
        ops_start = 8 + self.num_robots
        self.ops = [(tuple(map(float, d[:3])), tuple(map(float, d[3:6])), float(d[6])/1000) for d in [lines[i].split() for i in range(ops_start, ops_start + self.num_ops)]]

    def is_reachable(self, point, base):
        dist = math.sqrt(sum((p - b)**2 for p, b in zip(point, base)))
        return dist <= 2.0

    def assign_ops(self):
        assignments = [[] for _ in range(self.num_robots)]
        for op_idx, (pick, place, t) in enumerate(self.ops):
            best_robot = -1
            best_dist = float('inf')
            for r in range(self.num_robots):
                if self.is_reachable(pick, self.bases[r]) and self.is_reachable(place, self.bases[r]):
                    dist = math.sqrt(sum((p - b)**2 for p, b in zip(self.bases[r], pick)))
                    if dist < best_dist:
                        best_dist = dist
                        best_robot = r
            if best_robot != -1:
                assignments[best_robot].append((pick, place, t))
        return assignments

    def calc_time(self, p1, p2):
        dist = math.sqrt(sum((a - b)**2 for a, b in zip(p1, p2)))
        speed = 1.0
        return dist / speed

    def generate_traj(self, robot_id, ops):
        traj = []
        curr_time = 0.0
        curr_pos = self.bases[robot_id]
        traj.append((0, *curr_pos))
        for pick, place, t in ops:
            move_t = self.calc_time(curr_pos, pick)
            curr_time += move_t
            traj.append((int(curr_time*1000), *pick))
            curr_time += t
            traj.append((int(curr_time*1000), *pick))
            move_t = self.calc_time(pick, place)
            curr_time += move_t
            traj.append((int(curr_time*1000), *place))
            curr_time += t
            traj.append((int(curr_time*1000), *place))
            curr_pos = place
        return traj

    def get_pos_at_t(self, traj, t):
        t_ms = t * 1000
        for i in range(len(traj)-1):
            t1, x1, y1, z1 = traj[i]
            t2, x2, y2, z2 = traj[i+1]
            if t1 <= t_ms <= t2:
                if t1 == t2:
                    return (x1, y1, z1)
                frac = (t_ms - t1) / (t2 - t1)
                return (x1 + frac*(x2-x1), y1 + frac*(y2-y1), z1 + frac*(z2-z1))
        return traj[-1][1:]

    def check_collisions(self):
        if not any(self.schedules):
            return True
        max_t = max(wp[0] for sch in self.schedules for wp in sch) / 1000.0
        step = 0.05
        t = 0.0
        while t <= max_t + step:
            pos = [self.get_pos_at_t(sch, t) if sch else self.bases[i] for i, sch in enumerate(self.schedules)]
            for i in range(self.num_robots):
                for j in range(i+1, self.num_robots):
                    dist = math.sqrt(sum((a-b)**2 for a,b in zip(pos[i], pos[j])))
                    if dist < self.safe_dist + 2*self.tool_clearance:
                        return False
            t += step
        return True

    def resolve_collisions(self):
        attempts = 0
        while not self.check_collisions() and attempts < 10:
            delay_ms = 200 * (attempts + 1)
            for r in range(1, self.num_robots):
                self.schedules[r] = [(old_t + delay_ms, x, y, z) for old_t, x, y, z in self.schedules[r]]
            attempts += 1

    def solve(self, lines):
        self.load_data(lines)
        assigns = self.assign_ops()
        self.schedules = [self.generate_traj(r, assigns[r]) for r in range(self.num_robots)]
        self.resolve_collisions()
        makespan = max((wp[0] for sch in self.schedules for wp in sch), default=0)
        out = [str(makespan)]
        for r, sch in enumerate(self.schedules):
            out.append(f'R{r+1} {len(sch)}')
            for t, x, y, z in sch:
                out.append(f'{t} {x:.6f} {y:.6f} {z:.6f}')
        return out

def main():
    input_lines = []
    while True:
        line = input().strip()
        if not line:
            break
        input_lines.append(line)
    scheduler = Scheduler()
    results = scheduler.solve(input_lines)
    for line in results:
        print(line)

if __name__ == '__main__':
    main()