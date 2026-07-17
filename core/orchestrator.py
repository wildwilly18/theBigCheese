from core.map import Map
from entities.npc import NPC
from entities.player import Player
import numpy as np

import heapq
import math
from enum import Enum

from dataclasses import dataclass, field


class SearchType(str, Enum):
    FORWARD = "forward"
    DIJKSTRA = "dijkstra"
    A_STAR = "a_star"


@dataclass
class Orchestrator:
    map : Map
    num_actors : int = 0
    actors : list[NPC] = field(default_factory=list)
    player: Player | None = None

    def __len__(self):
        return len(self.actors)
    
    def __getitem__(self, key):
        return self.actors[key]

    def loop(self, dt:float = 0.01) -> None:
        if self.num_actors > 0:
            for actor in self.actors:
                actor.update(dt)

    def add_actor(self, id :int, x: float, y: float, psi: float):
        actor = NPC(self.map, id, x, y, psi)
        self.actors.append(actor)
        self.num_actors = len(self.actors)
        print(f"Added Actor of id: {id} at x: {x} y: {y} with heading {psi}")

    def get_actor_by_id(self, actor_id: int) -> NPC:
        for actor in self.actors:
            if actor.id == actor_id:
                return actor
        raise ValueError(f"Actor id {actor_id} not found")

    def set_player(self, player: Player) -> None:
        self.player = player

    def plan_actor_to_goal(
        self,
        actor_id: int,
        goal_x: float,
        goal_y: float,
        manhattan: bool = True,
        search_type: SearchType | str = SearchType.A_STAR,
    ):
        if isinstance(search_type, str):
            try:
                search_type = SearchType(search_type.lower())
            except ValueError as exc:
                valid = [s.value for s in SearchType]
                raise ValueError(f"Unknown search_type '{search_type}'. Valid options: {valid}") from exc

        actor = self.get_actor_by_id(actor_id)
        x_start = actor.x
        y_start = actor.y

        if search_type == SearchType.FORWARD:
            path = self.forward_search(x_start, y_start, goal_x, goal_y, self.map)
        elif search_type == SearchType.DIJKSTRA:
            path = self.dijkstra_search(x_start, y_start, goal_x, goal_y, self.map)
        elif search_type == SearchType.A_STAR:
            path = self.a_star_search(x_start, y_start, goal_x, goal_y, self.map)
        else:
            valid = [s.value for s in SearchType]
            raise ValueError(f"Unknown search_type '{search_type}'. Valid options: {valid}")

        actor.path = path

    def forward_search(self, x_start: float, y_start: float, x_goal: float, y_goal: float, map: Map, manhattan: bool=True) -> np.ndarray:
        x_idx_start, y_idx_start = self.map.idx_idy_from_xy(x_start, y_start)
        start_idx = self.flatten_idx(x_idx_start, y_idx_start)

        x_idx_goal, y_idx_goal = self.map.idx_idy_from_xy(x_goal, y_goal)
        goal_idx = self.flatten_idx(x_idx_goal, y_idx_goal)

        #Action Space, Manhatten
        if manhattan:
            actions = [(0,1),(1,0),(0,-1),(-1,0)]
        else:
            actions = [(0,1),(1,0),(0,-1),(-1,0), (1,1), (1,-1), (-1,-1), (-1,1)]

        frontier = [start_idx]

        # Visited set
        visited = {start_idx: None}
        count = 0
        max_count = len(self.map.x_breakpoints) * len(self.map.y_breakpoints)

        while len(frontier) > 0:
            x = frontier.pop(0)
            count = count + 1
            if count >= max_count:
                break

            #at goal break loop.
            if x == goal_idx:
                break
            
            xx, yy = self.unflatten_idx(x)
            
            for ux, uy in actions:
                xx_n = xx + ux
                yy_n = yy + uy

                in_bounds = 0 <= xx_n < len(self.map.x_breakpoints) and 0 <= yy_n < len(self.map.y_breakpoints)
                if not in_bounds:
                    continue

                x_n = self.flatten_idx(xx_n, yy_n)
                inZone = self.map.point_in_zone(xx_n, yy_n)

                if x_n not in visited and inZone:
                    visited[x_n] = x
                    frontier.append(x_n)

        # Raise error if not able to find a goal point. 
        if goal_idx not in visited:
            raise ValueError(f"No path found from ({x_start}, {y_start}) to ({x_goal}, {y_goal})")

        path_indexes = [goal_idx]

        next_idx = visited[path_indexes[-1]]

        while next_idx is not None:
            path_indexes.append(next_idx)

            #Increment to the next index
            next_idx = visited[path_indexes[-1]]

        path_indexes.reverse()

        path_points = []
        for i, path_index in enumerate(path_indexes):
            if (i % 50 == 0) or i == (len(path_indexes) - 1):
                x, y = self.map.x_y_from_idx(path_index)
                path_points.append([x, y])

        path = np.array(path_points, dtype=float)

        return path


    def dijkstra_search(self, x_start: float, y_start: float, x_goal: float, y_goal: float, map: Map, manhattan: bool=True) -> np.ndarray:
        idx_start, idy_start = map.idx_idy_from_xy(x_start, y_start)
        index_start = self.flatten_idx(idx_start, idy_start)

        idx_goal, idy_goal = map.idx_idy_from_xy(x_goal, y_goal)
        index_goal = self.flatten_idx(idx_goal, idy_goal)

        if manhattan:
            actions = [(0,1),(1,0),(0,-1),(-1,0)]
        else:
            actions = [(0,1),(1,0),(0,-1),(-1,0), (1,1), (1,-1), (-1,-1), (-1,1)]

        visited = {index_start: None}
        cost_to_come = {index_start: 0}

        frontier = [(0, index_start)] # (Priority, Node)
    
        while frontier:
            _, current = heapq.heappop(frontier)

            if current == index_goal:
                break

            for ux, uy in actions:
                xx, yy = self.unflatten_idx(current)

                xx_n = xx + ux
                yy_n = yy + uy

                x_n = self.flatten_idx(xx_n, yy_n)

                inZone = self.map.point_in_zone(xx_n, yy_n)

                if not inZone:
                    continue

                u_cost = math.sqrt(ux**2 + uy**2)
                new_cost = cost_to_come[current] + u_cost
                
                if x_n not in cost_to_come or new_cost < cost_to_come[x_n]:
                    cost_to_come[x_n] = new_cost
                    visited[x_n]      = current
                    heapq.heappush(frontier, (new_cost, x_n)) 
                
        if index_goal not in cost_to_come:
            raise ValueError(f"No path found from ({x_start}, {y_start}) to ({x_goal}, {y_goal})")

        path_indexes = [index_goal]

        next_idx = visited[path_indexes[-1]]

        while next_idx is not None:
            path_indexes.append(next_idx)

            #Increment to the next index
            next_idx = visited[path_indexes[-1]]

        path_indexes.reverse()

        path_points = []
        for i, path_index in enumerate(path_indexes):
            if (i % 50 == 0) or i == (len(path_indexes) - 1):
                x, y = self.map.x_y_from_idx(path_index)
                path_points.append([x, y])

        path = np.array(path_points, dtype=float)

        return path

    def a_star_search(self, x_start: float, y_start: float, x_goal: float, y_goal: float, map: Map, manhattan: bool=False) -> np.ndarray:
        idx_start, idy_start = map.idx_idy_from_xy(x_start, y_start)
        start_id = self.flatten_idx(idx_start, idy_start)

        idx_end, idy_end = map.idx_idy_from_xy(x_goal, y_goal)
        index_goal = self.flatten_idx(idx_end, idy_end)
        
        start_cost = math.sqrt((idx_end - idx_start)**2 + (idy_end - idy_start)**2)

        visited = {start_id : None}
        cost_f  = {start_id : start_cost}
        cost_g  = {start_id : 0}

        frontier = [(start_cost, start_id)] # (priority, node)

        if manhattan:
            actions = [(0,1),(1,0),(0,-1),(-1,0)]
        else:
            actions = [(0,1),(1,0),(0,-1),(-1,0),(1,1),(1,-1),(-1,-1),(-1,1)]

        while frontier:
            f_current, current = heapq.heappop(frontier)

            xx, yy = self.unflatten_idx(current)

            # Ignore outdated heap entries for this node.
            if f_current > cost_f.get(current, float("inf")):
                continue

            if current == index_goal:
                break

            for ux, uy in actions:
                x_n = xx + ux
                y_n = yy + uy

                inZone = map.point_in_zone(x_n, y_n)

                if not inZone:
                    continue

                cost_to_come = math.hypot((ux),(uy)) + cost_g[current]

                cost_to_go = math.hypot((idx_end - x_n),(idy_end - y_n))

                total_cost = cost_to_come + cost_to_go

                idx_n = self.flatten_idx(x_n, y_n)

                if idx_n not in cost_f or total_cost < cost_f[idx_n]:
                    cost_f[idx_n] = total_cost
                    cost_g[idx_n] = cost_to_come
                    visited[idx_n] = current
                    heapq.heappush(frontier, (total_cost, idx_n))

        if index_goal not in cost_f:
            raise ValueError(f"No path found from ({x_start}, {y_start}) to ({x_goal}, {y_goal})")

        path_indexes = [index_goal]

        next_idx = visited[path_indexes[-1]]

        while next_idx is not None:
            path_indexes.append(next_idx)

            #Increment to the next index
            next_idx = visited[path_indexes[-1]]

        path_indexes.reverse()

        path_points = []
        for i, path_index in enumerate(path_indexes):
            if (i % 50 == 0) or i == (len(path_indexes) - 1):
                x, y = self.map.x_y_from_idx(path_index)
                path_points.append([x, y])

        path = np.array(path_points, dtype=float)

        return path

    # Search utility tools
    def flatten_idx(self, idx: int, idy: int) -> int:
        num_y_bpts = len(self.map.y_breakpoints)
        return(idx * num_y_bpts + idy)

    def unflatten_idx(self, index: int) -> tuple[int, int]:
        num_y_bpts = len(self.map.y_breakpoints)

        xx = index // num_y_bpts
        yy = index % num_y_bpts

        return(xx, yy)

