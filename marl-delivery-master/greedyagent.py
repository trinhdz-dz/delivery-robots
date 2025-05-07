# import numpy as np
# thay đổi run_bfs để nhận thêm blocked set
def run_bfs(grid, start, goal, blocked=None):
    n_rows, n_cols = len(grid), len(grid[0])
    if blocked is None: blocked = set()

    queue = [(goal, [])]
    visited = {goal}
    d = {goal: 0}

    while queue:
        current, path = queue.pop(0)
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nxt = (current[0]+dx, current[1]+dy)
            if (0 <= nxt[0] < n_rows and 0 <= nxt[1] < n_cols
               and nxt not in visited
               and grid[nxt[0]][nxt[1]] == 0
               and nxt not in blocked):
                visited.add(nxt)
                d[nxt] = d[current] + 1
                queue.append((nxt, path+[nxt]))

    if start not in d:
        return 'S', 100000

    actions = ['U','D','L','R']
    for idx,(dx,dy) in enumerate([(-1,0),(1,0),(0,-1),(0,1)]):
        nxt = (start[0]+dx, start[1]+dy)
        if nxt in d and d[nxt] == d[start]-1:
            return actions[idx], d[nxt]
    return 'S', d[start]

class GreedyAgents:

    def __init__(self):
        self.agents = []
        self.packages = []
        self.packages_free = []
        self.n_robots = 0
        self.state = None

        self.is_init = False

    def init_agents(self, state):
        self.state = state
        self.n_robots = len(state['robots'])
        self.map = state['map']
        self.robots = [(robot[0]-1, robot[1]-1, 0) for robot in state['robots']]
        self.robots_target = ['free'] * self.n_robots
        self.packages += [(p[0], p[1]-1, p[2]-1, p[3]-1, p[4]-1, p[5]) for p in state['packages']]

        self.packages_free = [True] * len(self.packages)

    def update_move_to_target(self, robot_id, target_package_id, phase='start'):
        # tính blocked từ các robot khác
        blocked = { (r,c) for idx,(r,c,_) in enumerate(self.robots) if idx!=robot_id }
        pkg = self.packages[target_package_id]
        target_p = (pkg[1],pkg[2]) if phase=='start' else (pkg[3],pkg[4])
        # nếu goal nằm trong blocked thì cho phép đi vào
        if target_p in blocked:
            blocked.remove(target_p)

        # tính distance thủ công cho nhanh
        if phase=='start':
            manh = abs(target_p[0]-self.robots[robot_id][0]) + abs(target_p[1]-self.robots[robot_id][1])
        else:
            manh = abs(target_p[0]-self.robots[robot_id][0]) + abs(target_p[1]-self.robots[robot_id][1])

        if manh>=1:
            move, dist = run_bfs(self.map,
                (self.robots[robot_id][0],self.robots[robot_id][1]),
                target_p, blocked)
            pkg_act = '1' if dist==0 and phase=='start' else '2' if dist==0 else '0'
        else:
            move = 'S'
            pkg_act = '1' if phase=='start' else '2'

        return move, pkg_act
    
    def update_inner_state(self, state):
        # Update robot positions and states
        for i in range(len(state['robots'])):
            prev = self.robots[i]  # (r, c, carrying)
            robot = state['robots'][i]
            self.robots[i] = (robot[0]-1, robot[1]-1, robot[2])
            # pickup event
            if prev[2] == 0 and self.robots[i][2] != 0:
                pkg_id = self.robots[i][2]
                self.packages_free[pkg_id-1] = False
                self.robots_target[i] = pkg_id
            # drop/delivered event
            if prev[2] != 0 and self.robots[i][2] == 0:
                pkg_id = prev[2]
                # đã giao thì giữ False để không pick lại
                self.packages_free[pkg_id-1] = False
                self.robots_target[i] = 'free'
        
        # Append newly waiting packages (no duplicates by pkg_id)
        existing_ids = {pkg[0] for pkg in self.packages}
        for p in state['packages']:
            if p[0] not in existing_ids:
                pkg = (p[0], p[1]-1, p[2]-1, p[3]-1, p[4]-1, p[5])
                self.packages.append(pkg)
                self.packages_free.append(True)
                existing_ids.add(p[0])
    def get_actions(self, state):
        if self.is_init == False:
            # This mean we have invoke the init agents, use the update_inner_state to update the state
            self.is_init = True
            self.update_inner_state(state)

        else:
            self.update_inner_state(state)

        actions = []
        print("State robot: ", self.robots)
        # Start assigning a greedy strategy
        for i in range(self.n_robots):
            # Step 1: Check if the robot is already assigned to a package
            if self.robots_target[i] != 'free':
                
                closest_package_id = self.robots_target[i]
                # Step 1b: Check if the robot has reached the package
                if self.robots[i][2] != 0:
                    # Move to the target points
                    
                    move, action = self.update_move_to_target(i, closest_package_id-1, 'target')
                    actions.append((move, str(action)))
                else:  
                    # Step 1c: Continue to move to the package
                    move, action = self.update_move_to_target(i, closest_package_id-1)    
                    actions.append((move, str(action)))
            else:
                # Step 2: Find a package to pick up
                # Find the closest package
                closest_package_id = None
                closed_distance = 1000000
                for j in range(len(self.packages)):
                    if not self.packages_free[j]:
                        continue

                    pkg = self.packages[j]                
                    d = abs(pkg[1]-self.robots[i][0]) + abs(pkg[2]-self.robots[i][1])
                    if d < closed_distance:
                        closed_distance = d
                        closest_package_id = pkg[0]

                if closest_package_id is not None:
                    self.packages_free[closest_package_id-1] = False
                    self.robots_target[i] = closest_package_id
                    move, action = self.update_move_to_target(i, closest_package_id-1)    
                    actions.append((move, str(action)))
                else:
                    actions.append(('S', '0'))

        print("N robots = ", len(self.robots))
        print("Actions = ", actions)
        print(self.robots_target)
        return actions
