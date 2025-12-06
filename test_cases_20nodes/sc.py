import os
import random

def generate_test_cases():
    folder_name = "test_cases_20nodes"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    print(f"Đang tạo 30 test cases (20 Node) trong thư mục '{folder_name}'...")

    NUM_CASES = 30
    NUM_NODES = 20 # <--- Đã giảm xuống 20
    
    for i in range(1, NUM_CASES + 1):
        filename = os.path.join(folder_name, f"graph_20nodes_case_{i}.txt")
        edges = []
        
        # Case 1-10: Ngẫu nhiên (Random)
        if i <= 10:
            for u in range(1, NUM_NODES + 1):
                # Mỗi đỉnh nối 2-4 đỉnh khác (ít cạnh hơn cho thoáng)
                num_neighbors = random.randint(2, 4) 
                targets = random.sample([x for x in range(1, NUM_NODES + 1) if x != u], num_neighbors)
                for v in targets:
                    w = random.randint(1, 20)
                    edges.append(f"{u} {v} {w}")

        # Case 11-20: Lưới 4x5 (Grid) - Rất đẹp & dễ nhìn
        elif i <= 20:
            rows, cols = 4, 5 # 4x5 = 20 node
            for u in range(1, NUM_NODES + 1):
                r = (u - 1) // cols
                c = (u - 1) % cols
                
                # Nối phải
                if c < cols - 1:
                    edges.append(f"{u} {u+1} {random.randint(1, 10)}")
                # Nối dưới
                if r < rows - 1:
                    edges.append(f"{u} {u+cols} {random.randint(1, 10)}")

        # Case 21-30: Hình bánh xe (Wheel/Star) - Node 20 là tâm
        else:
            center = 20
            for u in range(1, 20):
                # Nối tất cả vào tâm
                edges.append(f"{center} {u} {random.randint(1, 5)}")
                # Nối vòng tròn bên ngoài (1-2, 2-3,...)
                v = u + 1 if u < 19 else 1
                edges.append(f"{u} {v} {random.randint(5, 15)}")

        with open(filename, "w") as f:
            f.write("\n".join(edges))
        
    print("Xong! Đã tạo dữ liệu 20 node.")

if __name__ == "__main__":
    generate_test_cases()