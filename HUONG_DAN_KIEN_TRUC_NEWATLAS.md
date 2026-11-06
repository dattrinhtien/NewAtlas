# 🏛️ NEWATLAS 3D PRO - TÀI LIỆU KIẾN TRÚC & HƯỚNG DẪN VẬN HÀNH

Tài liệu hướng dẫn hệ thống WebApp 3D Giải phẫu Bóc tách Toàn vẹn kết hợp Hệ Tri thức 419 Huyệt vị & 14 Kinh lạc YHCT.

---

## 1. TỔNG QUAN KIẾN TRÚC ĐÃ THỰC HIỆN

Dự án **NewAtlas** được tái cấu trúc hoàn toàn từ mô hình monolithic cũ (Unity WebGL 222MB một khối) sang **Kiến trúc Mô-đun Ba Tầng Hiện Đại (Modular 3-Tier Layered Architecture)**:

```
NewAtlas/
├── web/                                 # WebApp 3D Hoàn chỉnh
│   ├── index.html                       # Giao diện y khoa Dark Mode + Glassmorphism
│   ├── css/style.css                    # Tinh chỉnh hiển thị responsive, tooltip, drawer
│   ├── js/
│   │   ├── app.js                       # Controller trung tâm điều phối sự kiện
│   │   ├── threeViewer.js               # Engine Three.js: ACESFilmic, Tube neon, 419 huyệt
│   │   ├── storageManager.js            # Trình quản lý IndexedDB (Lazy load & Local Cache)
│   │   └── vendor/                      # Three.js ES Modules độc lập (chạy offline 100%)
│   │       ├── three.module.js
│   │       ├── GLTFLoader.js
│   │       └── OrbitControls.js
│   ├── data/
│   │   ├── acupoints.json               # Đầy đủ 419 huyệt vị với 18 trường thông tin y học
│   │   ├── meridians.json               # 14 đường kinh lạc chuẩn quốc tế
│   │   └── special_groups.json          # Phân loại Ngũ du, Du, Mộ, Nguyên, Lạc huyệt
│   ├── models/                          # Các tệp mô hình giải phẫu (.glb)
│   │   ├── skeleton.glb                 # Khung xương (mốc định vị huyệt)
│   │   ├── muscles.glb                  # Cơ bắp (độ sâu thốn và hướng châm kim)
│   │   ├── human-learning.glb           # Da ngọc bích bán trong suốt
│   │   ├── nerves.glb                   # Hệ thần kinh (Lazy-load + Caching)
│   │   └── organs.glb                   # Hệ nội tạng tạng phủ (Lazy-load + Caching)
│   └── server.py                        # HTTP Server nội bộ tối ưu byte-range và CORS
│
├── Models-of-human-anatomy/
│   ├── Z-Anatomy/Startup.blend          # Mô hình gốc Blender 3D (306MB)
│   └── export_z_anatomy_systems.py      # Script Blender xuất từng hệ 100% không decimate
│
└── run_local_web.command                # Click đúp là mở ngay WebApp trên trình duyệt
```

---

## 2. ĐÁP ỨNG TRỌN VẸN 3 YÊU CẦU CỦA BẠN

### Yêu cầu 1: Giữ nguyên mô hình gốc Blender 3D, không nén giảm dung lượng
- Chúng tôi đã tạo script `Models-of-human-anatomy/export_z_anatomy_systems.py`.
- Script này khi chạy trong Blender sẽ lọc từng Collection gốc của `Startup.blend` (Xương, Cơ, Thần kinh, Tuần hoàn, Bạch huyết, Nội tạng, Da) và xuất sang từng file `.glb` với tùy chọn:
  * `export_apply=True`, `export_yup=True`, `export_materials='EXPORT'`
  * **TUYỆT ĐỐI KHÔNG DECIMATE MESH**: Giữ trọn 100% số đỉnh (vertices), đường pháp tuyến (normals) và độ nét bề mặt của Z-Anatomy.

### Yêu cầu 2: Kế thừa định vị huyệt, kinh lạc & thông tin từ AcuAtlas3D
- Đã trích xuất và chuyển giao trọn vẹn cơ sở dữ liệu từ `acuatlas3d`:
  * **Đúng 419 huyệt vị** (362 huyệt chính kinh + 57 kỳ huyệt lâm sàng).
  * Mỗi huyệt chứa **đầy đủ 18 trường thông tin y học**: Tên Việt, Hán, Pinyin, Mã WHO, vị trí mốc giải phẫu, giải phẫu lớp cơ/thần kinh/mạch máu bên dưới, chủ trị, kỹ thuật châm sâu mấy thốn, cảnh báo an toàn chống thấu tạng, và công thức phối huyệt cổ truyền.
  * Tọa độ 3D đã được căn chỉnh chiếu bám sát mặt cơ thể.

### Yêu cầu 3: Cơ chế Lazy-Loading & Lưu Cache lần đầu (IndexedDB)
- **Lần đầu truy cập:** WebApp chỉ tải các hệ Baseline gồm: Lớp Da ngọc bích + Khung Xương + Hệ Cơ + 14 Kinh lạc & 419 Huyệt vị. Web khởi động chỉ trong 1-2 giây.
- **Khi người dùng chuyển sang hệ khác (Thần kinh, Nội tạng, Bạch huyết...):**
  1. `storageManager.js` kiểm tra IndexedDB của máy tính/trình duyệt.
  2. Nếu chưa có -> Tải file qua mạng với thanh tiến trình % (`Download Progress Modal`), sau khi tải xong sẽ tự động ghi nhị phân vào IndexedDB.
  3. Từ lần truy cập thứ hai trở đi -> Đọc trực tiếp từ ổ cứng máy tính (< 0.1s), không tốn mạng, chạy hoàn toàn offline.
  4. Có nút **"Dọn dẹp bộ nhớ offline"** trên giao diện để người dùng chủ động kiểm soát dung lượng lưu trữ.

---

## 3. CÁCH KHỞI CHẠY VÀ SỬ DỤNG

1. **Khởi chạy ứng dụng:**
   - Chỉ cần click đúp vào file `run_local_web.command` ở thư mục gốc.
   - Trình duyệt sẽ tự động mở địa chỉ: `http://localhost:8080`.

2. **Thao tác trên 3D:**
   - **Xoay:** Nhấp chuột trái và kéo.
   - **Di chuyển (Pan):** Nhấp chuột phải và kéo.
   - **Phóng to / Thu nhỏ:** Lăn con trỏ chuột.
   - **Xem chi tiết huyệt:** Click vào bất kỳ huyệt nào -> Camera sẽ lướt mượt tới vị trí huyệt và Drawer bên phải sẽ mở ra hiển thị toàn bộ 18 thông tin chuyên sâu.
   - **Tìm kiếm nhanh:** Gõ tên huyệt (ví dụ: *Hợp Cốc*, *LI4*, *Ấn Đường*, *Bách Hội*) hoặc tên bệnh chứng (*đau đầu*, *mất ngủ*, *đau lưng*) vào ô tìm kiếm trên đỉnh màn hình.
   - **Bật các hệ giải phẫu sâu:** Gạt công tắc ở thanh bên trái (Hệ Thần Kinh, Nội Tạng...) để kích hoạt cơ chế Lazy-load & Cache.

