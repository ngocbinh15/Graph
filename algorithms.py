PSEUDOCODE = {
    'BFS': [ 
        "create queue Q; mark start visited", 
        "while Q not empty:", 
        "  u = Q.dequeue()", 
        "  if u == target: return found", 
        "  for v in neighbors(u):", 
        "    if v not visited:", 
        "      mark v visited; parent[v]=u; Q.enqueue(v)", 
        "return not found" 
    ],
    'DFS': [ 
        "DFS(u):", 
        "  mark u as visited", 
        "  if u == target: return found", 
        "  for v in neighbors(u):", 
        "    if v not visited:", 
        "      if DFS(v) == found: return found", 
        "    else: backtrack", 
        "  backtrack from u" 
    ],
    'Dijkstra': [ 
        "dist[start]=0; PQ.push(0, start)", 
        "while PQ not empty:", 
        "  d, u = PQ.pop()", 
        "  if d > dist[u]: continue", 
        "  if u == target: return found", 
        "  for v, w in neighbors(u):", 
        "    if dist[u]+w < dist[v]:", 
        "      dist[v] = dist[u]+w; PQ.push", 
        "return not found" 
    ]
}