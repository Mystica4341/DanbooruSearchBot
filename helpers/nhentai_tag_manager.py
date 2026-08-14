import json
import os
import aiofiles

class TagManager:
    def __init__(self, db_path='tags.json'):
        self.db_path = db_path
        # Dictionary nội bộ dùng để tra cứu nhanh (O(1) lookup)
        self.tags_db = {} 
        self.load_db_sync()

    def load_db_sync(self):
        """Tải dữ liệu từ file JSON vào RAM và index hóa bằng ID."""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Chuyển đổi List of Objects thành Dictionary để tra cứu siêu tốc
                if isinstance(data, list):
                    for item in data:
                        tag_id = str(item.get('id'))
                        if tag_id:
                            # Lưu toàn bộ object vào dict với key là ID
                            self.tags_db[tag_id] = item 
                            
                print(f"Loaded {len(self.tags_db)} tags from {self.db_path}")
            except Exception as e:
                print(f"Error occurred while reading tags file: {e}")
        else:
            print("No tags.json file found, bot will start learning from scratch.")

    async def save_db_async(self):
        """Lưu lại xuống ổ cứng theo đúng định dạng Mảng (List) ban đầu."""
        try:
            # Biến Dictionary trở lại thành List để giữ nguyên format của bạn
            save_data = list(self.tags_db.values())
            
            async with aiofiles.open(self.db_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(save_data, ensure_ascii=False, indent=4))
        except Exception as e:
            print(f"Lỗi khi lưu file tags: {e}")

    def get_tag_names(self, tag_ids_list, tag_type_filter=None):
        """
        Dịch danh sách ID thành chuỗi tên tag.
        Nếu truyền tag_type (vd: 'artist', 'character'), sẽ chỉ lọc ra những tag thuộc loại đó.
        """
        tag_names = []
        for tag_id in tag_ids_list:
            tag_id_str = str(tag_id)
            
            if tag_id_str in self.tags_db:
                # Trích xuất object lưu trong RAM
                tag_object = self.tags_db[tag_id_str]
                
                # Kiểm tra điều kiện lọc theo type
                if tag_type_filter:
                    # Nếu tag hiện tại có type khớp với type đang tìm thì mới lấy tên
                    if tag_object.get('type') == tag_type_filter:
                        tag_names.append(tag_object.get('name', f"ID:{tag_id_str}"))
                else:
                    # Nếu không truyền tag_type thì lấy tất cả
                    tag_names.append(tag_object.get('name', f"ID:{tag_id_str}"))
            else:
                # Nếu ID chưa có trong DB (chưa học)
                # Ta chỉ hiển thị dạng "ID:..." khi không lọc type, vì ta không biết ID này thuộc type gì
                if not tag_type_filter:
                    tag_names.append(f"ID:{tag_id_str}")
                    
        # Trả về chuỗi cách nhau bởi dấu phẩy, nếu rỗng thì trả về "None" (hoặc "Unknown Artist" tuỳ bạn)
        return ", ".join(tag_names) if tag_names else ""

    async def learn_tags_from_detail(self, detail_data):
        """Học tag mới từ dữ liệu chi tiết truyện và giữ nguyên metadata."""
        is_updated = False
        tags_list = detail_data.get('tags', [])
        
        for tag_object in tags_list:
            tag_id_str = str(tag_object.get('id'))
            
            # Nếu gặp tag mới hoàn toàn, lưu nguyên cả Object (id, type, name, url...)
            if tag_id_str not in self.tags_db:
                self.tags_db[tag_id_str] = tag_object
                is_updated = True
                
        # Chỉ ghi file nếu thực sự có thêm dữ liệu mới
        if is_updated:
            await self.save_db_async()
            print(f"Successfully learned new tags and saved to {self.db_path}")