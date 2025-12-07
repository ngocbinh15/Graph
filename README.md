# Graph Algorithms Visualizer

Ứng dụng mô phỏng trực quan các thuật toán đồ thị: DFS, BFS, Dijkstra bằng Python và PyQt5.

## Tính năng

- Vẽ đồ thị (có thể chọn hướng hoặc vô hướng)
- Thêm/xoá đỉnh, cạnh, kéo thả vị trí đỉnh
- Chọn thuật toán (DFS, BFS, Dijkstra) và mô phỏng từng bước
- Hiển thị bảng các bước đi, so sánh trực quan giữa các thuật toán
- Giao diện hiện đại, trải nghiệm giống visualgo.net
- Tách biệt phần thuật toán và giao diện

## Cách sử dụng

1. Cài đặt Python 3.x và PyQt5:
   ```
   pip install pyqt5
   ```
2. Chạy ứng dụng:
   ```
   python gui.py
   ```
3. Vẽ đồ thị, chọn thuật toán, nhấn "Bước tiếp" để xem từng bước mô phỏng.

## Cấu trúc mã nguồn

- `gui.py`: Giao diện người dùng, xử lý sự kiện, hiển thị đồ thị và bảng bước đi
- `graph.py`: Định nghĩa cấu trúc dữ liệu đồ thị
- `algorithms.py`: Chứa các hàm thuật toán (DFS, BFS, Dijkstra)

## Đóng góp

Mọi đóng góp, ý tưởng hoặc báo lỗi xin gửi về [github.com/ngocbinh15/Graph](https://github.com/ngocbinh15/Graph)

## License

MIT License
