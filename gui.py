import sys
import math
import random
import traceback
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget, 
                            QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
                            QTableWidget, QTableWidgetItem, QGraphicsView, 
                            QGraphicsScene, QHeaderView, QMessageBox, QInputDialog,
                            QSlider, QGroupBox, QListWidget, QSplitter, 
                            QTabWidget, QFileDialog, QGridLayout, QTextEdit)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPen, QBrush, QColor, QLinearGradient, QFont, QPainter, QPainterPath

from graph import Graph
from algorithms import PSEUDOCODE

STYLESHEET = """
    QMainWindow { background-color: #f0f2f5; }
    QGroupBox { font-weight: bold; border: 1px solid #dcdcdc; border-radius: 6px; margin-top: 10px; background-color: white; }
    QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #333; }
    QPushButton { background-color: #2196F3; color: white; border: none; border-radius: 4px; padding: 6px 12px; font-weight: bold; }
    QPushButton:hover { background-color: #1976D2; }
    QPushButton:disabled { background-color: #BDBDBD; }
    QPushButton#btn_reset { background-color: #FF5722; }
    QPushButton#btn_reset:hover { background-color: #E64A19; }
    QListWidget { background-color: #263238; color: #ECEFF1; border: 1px solid #cfd8dc; border-radius: 4px; font-family: 'Consolas', 'Monaco', monospace; }
    QListWidget::item:selected { background-color: #FDD835; color: #000000; font-weight: bold; }
    QTableWidget { background-color: white; border: 1px solid #cfd8dc; gridline-color: #eceff1; }
    QHeaderView::section { background-color: #eceff1; padding: 4px; border: none; font-weight: bold; }
    QTextEdit { 
        padding: 4px; 
        border: 1px solid #cfd8dc; 
        border-radius: 4px; 
        background-color: #fafafa; 
        font-family: 'Consolas', monospace;
        font-size: 13px;
    }
"""

class NodeItem:
    def __init__(self, v, x, y, r=24):
        self.v, self.x, self.y, self.r = v, x, y, r
        self.ellipse, self.label = None, None

    def add_to_scene(self, scene):
        grad = QLinearGradient(self.x-self.r, self.y-self.r, self.x+self.r, self.y+self.r)
        grad.setColorAt(0, QColor('#42a5f5')); grad.setColorAt(1, QColor('#1976d2'))
        self.ellipse = scene.addEllipse(self.x-self.r, self.y-self.r, 2*self.r, 2*self.r, QPen(QColor('#0D47A1'), 3), QBrush(grad))
        self.ellipse.setZValue(2)
        self.label = scene.addText(str(self.v))
        self.label.setDefaultTextColor(QColor('white'))
        self.label.setFont(QFont("Arial", 12, QFont.Bold))
        r = self.label.boundingRect()
        self.label.setPos(self.x - r.width()/2, self.y - r.height()/2)
        self.label.setZValue(3)

    def set_highlight(self, scene, mode='normal'):
        if not self.ellipse: return
        brush, color = QBrush(), QColor('white')
        if mode == 'processing': brush, color = QBrush(QColor('#ffeb3b')), QColor('#d84315')
        elif mode == 'visited': brush, color = QBrush(QColor('#CFD8DC')), QColor('black')
        elif mode == 'target': brush, color = QBrush(QColor('#f44336')), QColor('white')
        elif mode == 'path': brush, color = QBrush(QColor('#43A047')), QColor('white')
        else: 
            grad = QLinearGradient(self.x-self.r, self.y-self.r, self.x+self.r, self.y+self.r)
            grad.setColorAt(0, QColor('#42a5f5')); grad.setColorAt(1, QColor('#1976d2'))
            brush = QBrush(grad)
        self.ellipse.setBrush(brush)
        self.label.setDefaultTextColor(color)

class EdgeItem:
    def __init__(self, u, v, w, x1, y1, x2, y2, directed=False, curve_offset=0):
        self.u, self.v, self.weight = u, v, w
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
        self.directed, self.curve_offset = directed, curve_offset
        self.path_item, self.text_item, self.arrows = None, None, []

    def add_to_scene(self, scene):
        path = QPainterPath()
        path.moveTo(self.x1, self.y1)
        mx, my = (self.x1 + self.x2)/2, (self.y1 + self.y2)/2
        if self.curve_offset != 0:
            dx, dy = self.x2 - self.x1, self.y2 - self.y1
            dist = math.sqrt(dx**2 + dy**2) or 1
            nx, ny = -dy/dist, dx/dist
            cx, cy = mx + nx * self.curve_offset, my + ny * self.curve_offset
            path.quadTo(cx, cy, self.x2, self.y2)
            self.mid_x, self.mid_y = cx, cy
            self.angle = math.atan2(self.y2 - cy, self.x2 - cx)
        else:
            path.lineTo(self.x2, self.y2)
            self.mid_x, self.mid_y = mx, my
            self.angle = math.atan2(self.y2 - self.y1, self.x2 - self.x1)
        self.path_item = scene.addPath(path, QPen(QColor('#90A4AE'), 2))
        self.path_item.setZValue(0)
        if self.directed: self.draw_arrow(scene)
        self.draw_weight(scene)

    def draw_weight(self, scene):
        off = -10 if self.curve_offset > 0 else 10 if self.curve_offset < 0 else -10
        self.text_item = scene.addText(str(self.weight))
        self.text_item.setDefaultTextColor(QColor('#455A64'))
        self.text_item.setFont(QFont("Arial", 10, QFont.Bold))
        r = self.text_item.boundingRect()
        self.text_item.setPos(self.mid_x - r.width()/2, self.mid_y - r.height()/2 + off)
        self.text_item.setZValue(1)

    def draw_arrow(self, scene):
        ex = self.x2 - 24 * math.cos(self.angle)
        ey = self.y2 - 24 * math.sin(self.angle)
        for d in [-math.pi/6, math.pi/6]:
            ax, ay = ex - 12 * math.cos(self.angle + d), ey - 12 * math.sin(self.angle + d)
            l = scene.addLine(ex, ey, ax, ay, QPen(QColor('#90A4AE'), 2))
            l.setZValue(1); self.arrows.append(l)

    def set_highlight(self, scene, mode='normal'):
        if not self.path_item: return
        c, w = (QColor('#ff9800'), 4) if mode == 'highlight' else (QColor('#2962FF'), 5) if mode == 'path' else (QColor('#90A4AE'), 2)
        self.path_item.setPen(QPen(c, w))
        if self.text_item: self.text_item.setDefaultTextColor(QColor('#e65100') if mode!='normal' else QColor('#455A64'))
        for a in self.arrows: scene.removeItem(a)
        self.arrows = []
        if self.directed: 
            ex = self.x2 - 24 * math.cos(self.angle)
            ey = self.y2 - 24 * math.sin(self.angle)
            for d in [-math.pi/6, math.pi/6]:
                ax, ay = ex - 12 * math.cos(self.angle + d), ey - 12 * math.sin(self.angle + d)
                l = scene.addLine(ex, ey, ax, ay, QPen(c, 2))
                l.setZValue(1); self.arrows.append(l)

class GraphSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Graph Algorithms Simulator - Modular V3')
        self.setGeometry(100, 100, 1600, 900)
        self.setStyleSheet(STYLESHEET)
        
        self.graph = Graph()
        self.vertex_positions = {}  
        self.vertex_items = {}     
        self.edge_items = []       
        self.selected_vertices = [] 
        self.mode = 'add_vertex'    
        self.simulation_steps = []
        self.current_step_index = 0
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_step)
        self.init_ui()

    def init_ui(self):
        main_splitter = QSplitter(Qt.Horizontal)
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setBackgroundBrush(QBrush(QColor(255, 255, 255)))
        self.view.setMinimumWidth(800) 
        self.view.setMouseTracking(True)
        self.view.mousePressEvent = self.handle_mouse_press
        self.view.mouseMoveEvent = self.handle_mouse_move
        self.view.mouseReleaseEvent = self.handle_mouse_release
        self.dragging_vertex = None
        main_splitter.addWidget(self.view)

        right_panel = QWidget()
        right_panel.setMinimumWidth(400)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(10)

        # 1. Edit
        self.grp_edit = QGroupBox("1. Dữ liệu & Đồ thị")
        layout_edit = QVBoxLayout() 
        row_edit_1 = QHBoxLayout()
        self.btn_add_vertex = QPushButton('Thêm Đỉnh')
        self.btn_add_edge = QPushButton('Thêm Cạnh')
        row_edit_1.addWidget(self.btn_add_vertex)
        row_edit_1.addWidget(self.btn_add_edge)
        row_edit_2 = QHBoxLayout()
        self.btn_remove = QPushButton('Xóa')
        self.combo_directed = QComboBox()
        self.combo_directed.addItems(['Vô hướng', 'Có hướng'])
        row_edit_2.addWidget(self.btn_remove)
        row_edit_2.addWidget(self.combo_directed)
        self.btn_import = QPushButton('📂 Nhập từ File (.txt)')
        self.btn_import.setStyleSheet("background-color: #607D8B; color: white;")
        self.btn_import.clicked.connect(self.import_from_file)
        layout_edit.addLayout(row_edit_1)
        layout_edit.addLayout(row_edit_2)
        layout_edit.addWidget(self.btn_import)
        self.grp_edit.setLayout(layout_edit)
        right_layout.addWidget(self.grp_edit)

        # 2. Simulation (GRID LAYOUT FIX)
        self.grp_sim = QGroupBox("2. Cài đặt Mô phỏng")
        layout_sim = QGridLayout() 
        layout_sim.addWidget(QLabel("Thuật toán:"), 0, 0)
        self.combo_algorithm = QComboBox()
        self.combo_algorithm.addItems(['DFS', 'BFS', 'Dijkstra'])
        self.combo_algorithm.currentIndexChanged.connect(self.update_code_view)
        layout_sim.addWidget(self.combo_algorithm, 0, 1)
        layout_sim.addWidget(QLabel("Bắt đầu (Start):"), 1, 0)
        self.combo_start = QComboBox()
        self.combo_start.setMinimumWidth(80)
        layout_sim.addWidget(self.combo_start, 1, 1)
        layout_sim.addWidget(QLabel("Đích (End):"), 2, 0)
        self.combo_end = QComboBox()
        self.combo_end.setMinimumWidth(80)
        self.combo_end.addItem("Không (Duyệt hết)")
        layout_sim.addWidget(self.combo_end, 2, 1)
        hbox_run = QHBoxLayout()
        self.btn_run = QPushButton('KHỞI TẠO')
        self.btn_run.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;") 
        self.btn_reset = QPushButton('Reset')
        self.btn_reset.setObjectName("btn_reset")
        hbox_run.addWidget(self.btn_run)
        hbox_run.addWidget(self.btn_reset)
        layout_sim.addLayout(hbox_run, 3, 0, 1, 2)
        self.grp_sim.setLayout(layout_sim)
        right_layout.addWidget(self.grp_sim)
        
        # 3. Controls
        player_group = QGroupBox("3. Điều khiển chạy")
        layout_player = QHBoxLayout()
        layout_player.addWidget(QLabel("Tốc độ:"))
        self.slider_speed = QSlider(Qt.Horizontal)
        self.slider_speed.setMinimum(50)
        self.slider_speed.setMaximum(2000)
        self.slider_speed.setValue(500)
        self.slider_speed.setInvertedAppearance(True)
        layout_player.addWidget(self.slider_speed)
        self.btn_auto = QPushButton("▶ Tự động")
        self.btn_next = QPushButton("⏭ Bước")
        self.btn_next.setEnabled(False)
        self.btn_auto.setEnabled(False)
        layout_player.addWidget(self.btn_auto)
        layout_player.addWidget(self.btn_next)
        player_group.setLayout(layout_player)
        right_layout.addWidget(player_group)

        # 4. Tabs
        self.tabs = QTabWidget()
        
        # Tab 1: Code & Info (TEXT EDIT FIX)
        tab_code_widget = QWidget()
        tab_code_layout = QVBoxLayout(tab_code_widget)
        self.grp_code = QGroupBox("Mã Giả")
        l_c = QVBoxLayout(); self.list_code = QListWidget(); self.list_code.setFont(QFont("Consolas", 15)); l_c.addWidget(self.list_code); self.grp_code.setLayout(l_c)
        
        self.grp_info = QGroupBox("Trạng thái Biến")
        self.grp_info.setMinimumHeight(180) 
        l_i = QVBoxLayout()
        
        l_i.addWidget(QLabel("Đường đi (Path):"))
        self.txt_path = QTextEdit() 
        self.txt_path.setReadOnly(True)
        self.txt_path.setMaximumHeight(50) 
        self.txt_path.setStyleSheet("color: blue; font-weight: bold; border: 1px solid #ccc;")
        l_i.addWidget(self.txt_path)
        
        l_i.addWidget(QLabel("Cấu trúc dữ liệu (Queue/Stack/PQ):"))
        self.txt_struct = QTextEdit() 
        self.txt_struct.setReadOnly(True)
        self.txt_struct.setMaximumHeight(50) 
        self.txt_struct.setStyleSheet("color: #d32f2f; font-weight: bold; border: 1px solid #ccc;")
        l_i.addWidget(self.txt_struct)
        
        self.grp_info.setLayout(l_i)
        
        tab_code_layout.addWidget(self.grp_code, stretch=1)
        tab_code_layout.addWidget(self.grp_info, stretch=0)
        
        # Tab 2: Logs
        tab_log_widget = QWidget()
        l_log = QVBoxLayout(tab_log_widget)
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(['Loại', 'Chi tiết'])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        l_log.addWidget(self.table)

        # Tab 3: Compare
        tab_cmp = QWidget(); l_cmp = QVBoxLayout(tab_cmp)
        self.table_compare = QTableWidget(0, 6)
        self.table_compare.setHorizontalHeaderLabels(['#', 'Thuật toán', 'V / E', 'Số bước', 'Chi phí', 'Độ phức tạp'])
        self.table_compare.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.btn_clear_table = QPushButton("Xóa lịch sử"); 
        self.btn_clear_table.clicked.connect(lambda: self.table_compare.setRowCount(0))
        l_cmp.addWidget(self.table_compare); l_cmp.addWidget(self.btn_clear_table)
        
        self.tabs.addTab(tab_code_widget, "👁 Code")
        self.tabs.addTab(tab_log_widget, "📝 Nhật ký")
        self.tabs.addTab(tab_cmp, "📊 So sánh")
        
        right_layout.addWidget(self.tabs)

        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([1100, 500])
        self.setCentralWidget(main_splitter)
        
        # Connect Signals
        self.btn_add_vertex.clicked.connect(lambda: self.set_mode('add_vertex'))
        self.btn_add_edge.clicked.connect(lambda: self.set_mode('add_edge'))
        self.btn_remove.clicked.connect(lambda: self.set_mode('remove'))
        self.combo_directed.currentIndexChanged.connect(self.change_directed)
        self.btn_run.clicked.connect(self.start_simulation)
        self.btn_next.clicked.connect(self.next_step)
        self.btn_reset.clicked.connect(self.reset_visuals)
        self.btn_auto.clicked.connect(self.toggle_auto_run)
        
        self.update_code_view()

    # --- Force Layout ---
    def apply_force_layout(self, nodes, edges, iterations=50):
        width, height = 1100, 700
        center_x, center_y = 550, 350
        positions = {}
        for node in nodes:
            positions[node] = [center_x + random.uniform(-100, 100), center_y + random.uniform(-100, 100)]
        k = math.sqrt((width * height) / len(nodes)) * 1.2
        t = width / 10
        
        for i in range(iterations):
            disp = {node: [0, 0] for node in nodes}
            for v in nodes:
                for u in nodes:
                    if u != v:
                        dx = positions[v][0] - positions[u][0]
                        dy = positions[v][1] - positions[u][1]
                        dist = math.sqrt(dx*dx + dy*dy)
                        if dist < 0.01: dist = 0.01
                        force = (k * k) / dist
                        disp[v][0] += (dx / dist) * force
                        disp[v][1] += (dy / dist) * force
            for u, v, w in edges:
                if u not in positions or v not in positions: continue
                dx = positions[v][0] - positions[u][0]
                dy = positions[v][1] - positions[u][1]
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < 0.01: dist = 0.01
                force = (dist * dist) / k
                dx_norm = (dx / dist) * force
                dy_norm = (dy / dist) * force
                disp[v][0] -= dx_norm
                disp[v][1] -= dy_norm
                disp[u][0] += dx_norm
                disp[u][1] += dy_norm
            for v in nodes:
                dx = disp[v][0]
                dy = disp[v][1]
                dist = math.sqrt(dx*dx + dy*dy)
                if dist > 0:
                    limited_dist = min(dist, t)
                    positions[v][0] += (dx / dist) * limited_dist
                    positions[v][1] += (dy / dist) * limited_dist
                    positions[v][0] = min(width - 50, max(50, positions[v][0]))
                    positions[v][1] = min(height - 50, max(50, positions[v][1]))
            t *= 0.95
        return positions

    # --- Import ---
    def import_from_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Chọn file đồ thị", "", "Text Files (*.txt);;All Files (*)", options=options)
        if not file_name: return
        try:
            with open(file_name, 'r') as f:
                lines = [line.strip() for line in f if line.strip()]
            if not lines: raise ValueError("File rỗng!")

            self.graph = Graph()
            self.vertex_positions = {}
            self.vertex_items = {}
            self.edge_items = []
            self.scene.clear()
            self.graph.directed = (self.combo_directed.currentIndex() == 1)
            
            first_line_nums = list(map(int, lines[0].split()))
            is_matrix = False
            if len(lines) > 1 and len(lines) == len(first_line_nums): is_matrix = True
            nodes_set = set()
            edges_list = [] 

            if is_matrix:
                size = len(lines)
                for r in range(size):
                    row_vals = list(map(int, lines[r].split()))
                    nodes_set.add(r + 1)
                    for c in range(size):
                        weight = row_vals[c]
                        if weight > 0: edges_list.append((r + 1, c + 1, weight))
            else:
                start_idx = 0
                if len(first_line_nums) <= 2 and len(lines) > 1: start_idx = 1
                for i in range(start_idx, len(lines)):
                    parts = list(map(int, lines[i].split()))
                    if len(parts) >= 2:
                        u, v = parts[0], parts[1]
                        w = parts[2] if len(parts) > 2 else 1
                        nodes_set.add(u)
                        nodes_set.add(v)
                        edges_list.append((u, v, w))

            sorted_nodes = sorted(list(nodes_set))
            if not sorted_nodes: return
            new_positions = self.apply_force_layout(sorted_nodes, edges_list, iterations=100)
            
            for node, (x, y) in new_positions.items():
                self.graph.add_vertex(node)
                self.vertex_positions[node] = (x, y)
            for u, v, w in edges_list:
                self.graph.add_edge(u, v, w)

            self.redraw()
            self.update_node_lists()
            self.log_step("visit", f"Đã nhập {len(sorted_nodes)} đỉnh (Layout Tự động).")
            QMessageBox.information(self, "Thành công", "Đã nhập và tự động dàn trang đồ thị!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi đọc file: {str(e)}")

    def update_code_view(self):
        algo = self.combo_algorithm.currentText()
        self.list_code.clear()
        if algo in PSEUDOCODE: self.list_code.addItems(PSEUDOCODE[algo])

    def highlight_code_line(self, line_num):
        if line_num == -1: self.list_code.clearSelection(); return
        if 0 <= line_num < self.list_code.count(): self.list_code.setCurrentRow(line_num)

    def update_node_lists(self):
        current_start = self.combo_start.currentText()
        current_end = self.combo_end.currentText()
        self.combo_start.clear()
        self.combo_end.clear()
        self.combo_end.addItem("Không (Duyệt hết)")
        nodes = sorted(list(self.vertex_positions.keys()))
        for n in nodes:
            self.combo_start.addItem(str(n))
            self.combo_end.addItem(str(n))
        idx = self.combo_start.findText(current_start)
        if idx >= 0: self.combo_start.setCurrentIndex(idx)
        idx = self.combo_end.findText(current_end)
        if idx >= 0: self.combo_end.setCurrentIndex(idx)

    def handle_mouse_press(self, event):
        pos = self.view.mapToScene(event.pos())
        x, y = pos.x(), pos.y()
        v = self.get_vertex_at(x, y)
        if self.mode == 'add_vertex':
            if v is not None: self.dragging_vertex = v
            else:
                v_new = len(self.vertex_positions) + 1
                while v_new in self.vertex_positions: v_new += 1
                self.graph.add_vertex(v_new)
                self.vertex_positions[v_new] = (x, y)
                self.draw_vertex(v_new, x, y)
                self.update_node_lists()
        elif self.mode == 'add_edge':
            if v is not None:
                self.highlight_node(v, 'processing') 
                self.selected_vertices.append(v)
                if len(self.selected_vertices) == 2:
                    u, v2 = self.selected_vertices
                    if u != v2:
                        weight, ok = QInputDialog.getInt(self, "Trọng số cạnh", f"Nhập trọng số ({u}, {v2}):", value=1, min=1, max=100)
                        if ok:
                            self.graph.add_edge(u, v2, weight)
                            self.redraw()
                    self.selected_vertices = []
                    self.reset_visuals()
            else:
                self.selected_vertices = []
                self.reset_visuals()
        elif self.mode == 'remove':
            if v:
                self.remove_vertex(v)
                self.update_node_lists()
            else:
                u, v2 = self.get_edge_at(x, y)
                if u is not None:
                    self.graph.remove_edge(u, v2)
                    self.redraw()

    def handle_mouse_move(self, event):
        if self.dragging_vertex is not None:
            pos = self.view.mapToScene(event.pos())
            self.vertex_positions[self.dragging_vertex] = (pos.x(), pos.y())
            self.redraw()

    def handle_mouse_release(self, event):
        self.dragging_vertex = None

    def set_mode(self, mode):
        self.mode = mode
        self.selected_vertices = []
        self.reset_visuals()
        self.setWindowTitle(f'Mô phỏng - Chế độ: {mode}')

    def change_directed(self):
        self.graph.directed = (self.combo_directed.currentIndex() == 1)
        self.graph.adj = {} 
        self.vertex_positions = {}
        self.redraw()
        self.update_node_lists()

    def get_vertex_at(self, x, y):
        for v, (vx, vy) in self.vertex_positions.items():
            if (x - vx)**2 + (y - vy)**2 <= 24*24: return v
        return None

    def get_edge_at(self, x, y):
        return None, None 

    def draw_vertex(self, v, x, y):
        node = NodeItem(v, x, y)
        node.add_to_scene(self.scene)
        self.vertex_items[v] = node

    def draw_edge(self, u, v, w, curve_offset=0):
        if u not in self.vertex_positions or v not in self.vertex_positions: return
        x1, y1 = self.vertex_positions[u]
        x2, y2 = self.vertex_positions[v]
        edge = EdgeItem(u, v, w, x1, y1, x2, y2, self.graph.directed, curve_offset)
        edge.add_to_scene(self.scene)
        self.edge_items.append(edge)

    def remove_vertex(self, v):
        if v in self.vertex_positions:
            del self.vertex_positions[v]
            if v in self.graph.adj: del self.graph.adj[v]
            for u in self.graph.adj:
                self.graph.adj[u] = [x for x in self.graph.adj[u] if x[0] != v]
            self.redraw()

    def redraw(self):
        self.scene.clear()
        self.vertex_items.clear()
        self.edge_items.clear()
        existing_edges = set()
        for u in self.graph.adj:
            for v, w in self.graph.adj[u]: existing_edges.add((u, v))
        drawn_edges = set()
        
        for u in self.graph.adj:
            for v, w in self.graph.adj[u]:
                is_bidirectional = self.graph.directed and ((v, u) in existing_edges)
                should_draw = False
                curve_offset = 0
                if self.graph.directed:
                    should_draw = True
                    if is_bidirectional: curve_offset = 40
                else:
                    edge_key = tuple(sorted((u, v)))
                    if edge_key not in drawn_edges:
                        should_draw = True
                        drawn_edges.add(edge_key)
                if should_draw: self.draw_edge(u, v, w, curve_offset)
        for v, (x, y) in self.vertex_positions.items(): self.draw_vertex(v, x, y)

    def highlight_node(self, v, mode='normal'):
        if v in self.vertex_items: self.vertex_items[v].set_highlight(self.scene, mode)

    def highlight_edge(self, u, v, mode='normal'):
        for edge in self.edge_items:
            if self.graph.directed:
                if edge.u == u and edge.v == v: edge.set_highlight(self.scene, mode)
            else:
                if (edge.u == u and edge.v == v) or (edge.u == v and edge.v == u):
                    edge.set_highlight(self.scene, mode)

    def reset_visuals(self):
        self.timer.stop()
        self.btn_auto.setText("▶ Tự động")
        self.redraw()
        self.btn_next.setEnabled(False)
        self.btn_auto.setEnabled(False)
        self.table.setRowCount(0)
        self.txt_path.clear()
        self.txt_struct.clear()
        self.highlight_code_line(-1)

    # --- SIMULATION SAFETY ---
    def start_simulation(self):
        try:
            if not self.vertex_positions: return
            algo = self.combo_algorithm.currentText()
            try: start = int(self.combo_start.currentText())
            except ValueError:
                QMessageBox.warning(self, "Lỗi", "Chưa có đỉnh bắt đầu. Hãy chọn hoặc thêm đỉnh!")
                return
            end_node = None
            if self.combo_end.currentIndex() > 0:
                try: end_node = int(self.combo_end.currentText())
                except ValueError: pass
            
            self.reset_visuals()
            if end_node is not None: self.highlight_node(end_node, 'target')
            
            path_cost = 0
            if algo == 'DFS': self.simulation_steps, path_cost = self.graph.dfs(start, end_node)
            elif algo == 'BFS': self.simulation_steps, path_cost = self.graph.bfs(start, end_node)
            elif algo == 'Dijkstra': self.simulation_steps, path_cost = self.graph.dijkstra(start, end_node)
            
            self.update_compare_table(algo, start, end_node, len(self.simulation_steps), path_cost)

            self.current_step_index = 0
            self.btn_next.setEnabled(True)
            self.btn_auto.setEnabled(True)
            self.update_code_view()
            self.highlight_code_line(0)
            self.log_step("visit", f"Bắt đầu {algo} tại {start}")
            self.tabs.setCurrentIndex(0)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi Nghiêm Trọng", f"Đã xảy ra lỗi khi khởi tạo:\n{str(e)}\n\n{traceback.format_exc()}")

    def update_compare_table(self, algo, start, end, steps, cost):
        row = self.table_compare.rowCount()
        self.table_compare.insertRow(row)
        V = len(self.graph.adj)
        E = sum(len(v) for v in self.graph.adj.values())
        if not self.graph.directed: E //= 2
        
        theory = ""
        if algo in ['BFS', 'DFS']: theory = f"O(V+E) ~ {V+E}"
        elif algo == 'Dijkstra': theory = f"O((V+E)logV) ~ {int((V+E)*math.log2(V) if V>0 else 0)}"

        target_str = str(end) if end else "All"
        self.table_compare.setItem(row, 0, QTableWidgetItem(str(row + 1)))
        self.table_compare.setItem(row, 1, QTableWidgetItem(f"{algo} ({start}->{target_str})"))
        self.table_compare.setItem(row, 2, QTableWidgetItem(f"{V} / {E}"))
        self.table_compare.setItem(row, 3, QTableWidgetItem(str(steps)))
        self.table_compare.setItem(row, 4, QTableWidgetItem(str(cost) if cost > 0 else "-"))
        self.table_compare.setItem(row, 5, QTableWidgetItem(theory))

    def toggle_auto_run(self):
        if self.timer.isActive():
            self.timer.stop()
            self.btn_auto.setText("▶ Tiếp tục")
        else:
            self.timer.start(self.slider_speed.value())
            self.btn_auto.setText("⏸ Tạm dừng")

    def log_step(self, step_type, description):
        row = self.table.rowCount()
        self.table.insertRow(row)
        item_type = QTableWidgetItem(step_type)
        item_desc = QTableWidgetItem(description)
        bg_color, text_color = QColor('white'), QColor('black')
        if step_type == 'processing': bg_color, text_color = QColor('#FFF9C4'), QColor('#F57F17')
        elif step_type == 'visit': bg_color, text_color = QColor('#C8E6C9'), QColor('#2E7D32')
        elif step_type == 'traverse': bg_color, text_color = QColor('#E1F5FE'), QColor('#0277BD')
        elif step_type == 'check_edge': bg_color, text_color = QColor('#F5F5F5'), QColor('#616161')
        elif step_type == 'update_dist': bg_color, text_color = QColor('#FFE0B2'), QColor('#E65100')
        elif step_type == 'backtrack': bg_color, text_color = QColor('#F8BBD0'), QColor('#C2185B')
        elif 'highlight_path' in step_type: bg_color, text_color = QColor('#B9F6CA'), QColor('#1B5E20')
        elif step_type == 'check_loop': bg_color, text_color = QColor('#ECEFF1'), QColor('#546E7A')
        elif step_type == 'not_found': bg_color, text_color = QColor('#FFCDD2'), QColor('#B71C1C')
        
        item_type.setBackground(bg_color); item_type.setForeground(text_color)
        item_desc.setBackground(bg_color); item_desc.setForeground(text_color)
        self.table.setItem(row, 0, item_type); self.table.setItem(row, 1, item_desc)
        self.table.scrollToBottom()

    def next_step(self):
        if self.current_step_index >= len(self.simulation_steps):
            self.timer.stop()
            self.btn_auto.setText("Hoàn tất")
            self.btn_auto.setEnabled(False)
            self.btn_next.setEnabled(False)
            
            last_step = self.simulation_steps[-1] if self.simulation_steps else None
            if last_step and last_step[0] != 'not_found':
                QMessageBox.information(self, "Hoàn tất", "Đã kết thúc mô phỏng!")
            return

        step_data = self.simulation_steps[self.current_step_index]
        step_type = step_data[0]
        u, v, desc = step_data[1], step_data[2], step_data[3]
        if len(step_data) >= 7:
            self.txt_path.setText(step_data[4])
            self.txt_struct.setText(step_data[5])
            self.highlight_code_line(step_data[6])
        self.log_step(step_type, desc)

        if step_type == 'processing': self.highlight_node(u, 'processing')
        elif step_type == 'visit': self.highlight_node(u, 'visited')
        elif step_type == 'traverse': 
            self.highlight_edge(u, v, 'highlight')
            self.highlight_node(v, 'processing')
        elif step_type == 'backtrack': self.highlight_edge(u, v, 'highlight')
        elif step_type == 'check_edge': self.highlight_edge(u, v, 'highlight')
        elif step_type == 'highlight_path_node': self.highlight_node(u, 'path')
        elif step_type == 'highlight_path_edge': self.highlight_edge(u, v, 'path')
        elif step_type == 'update_dist': pass 
        
        elif step_type == 'not_found':
            self.timer.stop()
            QMessageBox.warning(self, "Kết quả", f"Rất tiếc! {desc}")
            self.btn_auto.setText("Kết thúc")
            self.btn_auto.setEnabled(False)
            self.btn_next.setEnabled(False)
            return 
        
        self.current_step_index += 1

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GraphSimulator()
    window.show()
    sys.exit(app.exec_())