import random

def generate_graph_data(filename, num_vertices, num_edges):
    """
    Tạo dữ liệu đồ thị ngẫu nhiên và lưu vào file.
    Format: Đỉnh_nguồn Đỉnh_đích Trọng_số
    """
    with open(filename, 'w') as f:
        # Nếu bạn muốn dòng đầu tiên chứa số đỉnh và số cạnh (thường gặp trong đề bài):
        # f.write(f"{num_vertices} {num_edges}\n") 
        
        for _ in range(num_edges):
            # Chọn ngẫu nhiên đỉnh u và v từ 1 đến num_vertices
            u = random.randint(1, num_vertices)
            v = random.randint(1, num_vertices)
            
            # Đảm bảo không có khuyên (u != v) - Bỏ qua nếu không cần thiết
            while u == v:
                v = random.randint(1, num_vertices)
            
            # Chọn trọng số ngẫu nhiên (ví dụ từ 1 đến 20 giống mẫu của bạn)
            w = random.randint(1, 20)
            
            f.write(f"{u} {v} {w}\n")

    print(f"Đã tạo xong file '{filename}' với {num_vertices} đỉnh và {num_edges} cạnh.")

# --- CẤU HÌNH ---
SO_DINH = 10       # 10,000 đỉnh
SO_CANH = 12       # Ví dụ: 50,000 cạnh (trung bình mỗi đỉnh nối với 5 đỉnh khác)
TEN_FILE = "graph_10.txt"

generate_graph_data(TEN_FILE, SO_DINH, SO_CANH)