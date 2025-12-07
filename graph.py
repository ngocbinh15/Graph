import heapq
from collections import deque

class Graph:
    def __init__(self):
        self.adj = {}
        self.directed = False

    def add_vertex(self, u):
        if u not in self.adj: self.adj[u] = []

    def add_edge(self, u, v, w=1):
        if u not in self.adj: self.add_vertex(u)
        if v not in self.adj: self.add_vertex(v)
        for i, (neighbor, weight) in enumerate(self.adj[u]):
            if neighbor == v:
                self.adj[u][i] = (v, w)
                if not self.directed:
                    for j, (n2, w2) in enumerate(self.adj[v]):
                        if n2 == u: self.adj[v][j] = (u, w)
                return
        self.adj[u].append((v, w))
        if not self.directed: self.adj[v].append((u, w))

    def remove_edge(self, u, v):
        if u in self.adj: self.adj[u] = [(n, w) for n, w in self.adj[u] if n != v]
        if not self.directed and v in self.adj: self.adj[v] = [(n, w) for n, w in self.adj[v] if n != u]

    def get_path_str(self, parent_map, current):
        path = []
        curr = current
        while curr is not None:
            path.append(str(curr))
            curr = parent_map.get(curr)
        return " -> ".join(reversed(path))

    def add_path_highlight_steps(self, steps, path_nodes, path_str):
        if not path_nodes: return
        steps.append(('highlight_path_node', path_nodes[0], None, "Tô màu đường đi", path_str, "Hoàn tất", -1))
        for i in range(len(path_nodes) - 1):
            u, v = path_nodes[i], path_nodes[i+1]
            steps.append(('highlight_path_edge', u, v, f"Đường đi: {u} -> {v}", path_str, "Hoàn tất", -1))
            steps.append(('highlight_path_node', v, None, "Tô màu đường đi", path_str, "Hoàn tất", -1))

    def calculate_cost_from_parent(self, parent, start, end):
        cost = 0
        curr = end
        while curr != start:
            p = parent.get(curr)
            if p is None: return 0
            w_found = 0
            if p in self.adj:
                for v, w in self.adj[p]:
                    if v == curr: w_found = w; break
            cost += w_found
            curr = p
        return cost

    def calculate_cost_from_stack(self, stack):
        cost = 0
        for i in range(len(stack) - 1):
            u, v = stack[i], stack[i+1]
            if u in self.adj:
                for neighbor, w in self.adj[u]:
                    if neighbor == v: cost += w; break
        return cost

    def bfs(self, start_node, end_node=None):
        steps = []
        visited = set()
        queue = deque([start_node])
        visited.add(start_node)
        parent = {start_node: None}
        
        queue_str = f"[{start_node}]"
        path_str = str(start_node)
        
        steps.append(('visit', start_node, None, f"Bắt đầu BFS", path_str, queue_str, 0))

        while queue:
            steps.append(('check_loop', None, None, "Kiểm tra hàng đợi", path_str, str(list(queue)), 1))
            u = queue.popleft()
            path_str = self.get_path_str(parent, u)
            steps.append(('processing', u, None, f"Lấy {u} ra", path_str, str(list(queue)), 2))
            
            if end_node is not None:
                if u == end_node:
                    steps.append(('visit', u, None, f"Đã tìm thấy {u}!", path_str, "[]", 3))
                    final_path = []
                    curr = end_node
                    while curr is not None:
                        final_path.append(curr)
                        curr = parent[curr]
                    final_path.reverse()
                    self.add_path_highlight_steps(steps, final_path, path_str)
                    cost = self.calculate_cost_from_parent(parent, start_node, end_node)
                    return steps, cost

            if u in self.adj:
                sorted_neighbors = sorted(self.adj[u])
                for v, w in sorted_neighbors:
                    steps.append(('check_edge', u, v, f"Xét {v}", path_str, str(list(queue)), 4))
                    if v not in visited:
                        visited.add(v)
                        parent[v] = u
                        queue.append(v)
                        steps.append(('traverse', u, v, f"Duyệt cạnh ({u}, {v})", path_str, str(list(queue)), 6))
                        steps.append(('visit', v, None, f"Thêm {v} vào Queue", path_str, str(list(queue)), 6))
        
        if end_node: steps.append(('not_found', start_node, None, f"Không tìm thấy {end_node}!", path_str, "[]", 7))
        return steps, 0

    def dfs(self, start_node, end_node=None):
        steps = []
        visited = set()
        path_stack = [] 
        total_nodes = len(self.adj)

        def get_path_str_dfs(): return " -> ".join(map(str, path_stack))

        def _dfs_recursive(u):
            visited.add(u)
            path_stack.append(u)
            steps.append(('processing', u, None, f"Xét đỉnh {u}", get_path_str_dfs(), str(path_stack), 1))
            
            is_target_found = (end_node is not None and u == end_node)
            is_all_visited = (end_node is None and len(visited) == total_nodes)

            if is_target_found or is_all_visited:
                msg = f"Tìm thấy đích {u}!" if is_target_found else "Đã duyệt hết!"
                steps.append(('visit', u, None, msg, get_path_str_dfs(), "Hoàn tất", 2))
                return True 

            if u in self.adj:
                sorted_neighbors = sorted(self.adj[u], key=lambda x: x[0])
                for v, w in sorted_neighbors:
                    steps.append(('check_edge', u, v, f"Xét {v}", get_path_str_dfs(), str(path_stack), 3))
                    if v not in visited:
                        steps.append(('traverse', u, v, f"Đệ quy xuống {v}", get_path_str_dfs(), str(path_stack), 5))
                        if _dfs_recursive(v): return True
                        steps.append(('backtrack', u, v, f"Quay lui về {u}", get_path_str_dfs(), str(path_stack), 8))
                        steps.append(('processing', u, None, f"Tiếp tục xét {u}", get_path_str_dfs(), str(path_stack), 3))
                    else:
                        steps.append(('check_edge', u, v, f"{v} đã thăm -> Bỏ qua", get_path_str_dfs(), str(path_stack), 7))
            
            path_stack.pop()
            steps.append(('visit', u, None, f"Duyệt xong {u}", get_path_str_dfs(), str(path_stack), 8))
            return False

        found = _dfs_recursive(start_node)
        
        cost = 0
        if found:
            self.add_path_highlight_steps(steps, path_stack, get_path_str_dfs())
            cost = self.calculate_cost_from_stack(path_stack)
        elif end_node is not None:
            steps.append(('not_found', start_node, None, f"Không tìm thấy {end_node}!", "[]", "[]", 8))
            
        return steps, cost

    def dijkstra(self, start_node, end_node=None):
        steps = []
        dist = {node: float('inf') for node in self.adj}
        dist[start_node] = 0
        pq = [(0, start_node)]
        parent = {start_node: None}
        
        def get_pq_str(): return str([(d,n) for d,n in sorted(pq)])

        steps.append(('visit', start_node, 0, f"Khởi tạo", str(start_node), get_pq_str(), 0))

        while pq:
            steps.append(('check_loop', None, None, "Check PQ", self.get_path_str(parent, pq[0][1] if pq else None), get_pq_str(), 1))
            d, u = heapq.heappop(pq)
            path_str = self.get_path_str(parent, u)
            steps.append(('processing', u, None, f"Lấy {u} (d={d})", path_str, get_pq_str(), 2))
            
            if d > dist[u]: continue
            
            if end_node is not None and u == end_node:
                steps.append(('visit', u, None, f"Đã tìm thấy {u}!", path_str, "[]", 4))
                final_path = []
                curr = end_node
                while curr is not None:
                    final_path.append(curr)
                    curr = parent[curr]
                final_path.reverse()
                self.add_path_highlight_steps(steps, final_path, path_str)
                return steps, d

            if u in self.adj:
                for v, weight in sorted(self.adj[u], key=lambda x: x[0]):
                    steps.append(('check_edge', u, v, f"Xét {v} (w={weight})", path_str, get_pq_str(), 5))
                    if dist[u] + weight < dist[v]:
                        old = dist[v]
                        dist[v] = dist[u] + weight
                        heapq.heappush(pq, (dist[v], v))
                        parent[v] = u
                        steps.append(('traverse', u, v, f"Relax: {old}->{dist[v]}", path_str, get_pq_str(), 7))
                        steps.append(('update_dist', v, dist[v], f"Push PQ", path_str, get_pq_str(), 7))
        
        if end_node is not None:
            steps.append(('not_found', start_node, None, f"Không tìm thấy {end_node}!", path_str, "[]", 8))
            
        return steps, 0