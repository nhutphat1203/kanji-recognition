import numpy as np
from PIL import Image

class RecordETL8G:
    RECORD_SIZE = 8199
    IMAGE_WIDTH = 128
    IMAGE_HEIGHT = 127
    
    def __init__(self, raw_bytes: bytes):
        if len(raw_bytes) != self.RECORD_SIZE:
            raise ValueError(f"Record phải có {self.RECORD_SIZE} bytes, nhưng nhận {len(raw_bytes)} bytes")

        # Parse các trường metadata
        self.serial_sheet_no = int.from_bytes(raw_bytes[0:2], "big")          # Byte 1-2
        self.jis_code = raw_bytes[2:4]                                       # Byte 3-4
        self.typical_reading = raw_bytes[4:12].decode("ascii", errors="ignore").strip()  # Byte 5-12
        self.serial_data_no = int.from_bytes(raw_bytes[12:16], "big")        # Byte 13-16
        self.eval_individual = raw_bytes[16]                                 # Byte 17
        self.eval_group = raw_bytes[17]                                      # Byte 18
        self.gender = raw_bytes[18]                                          # Byte 19 (1=male,2=female)
        self.age = raw_bytes[19]                                             # Byte 20
        self.industry_code = int.from_bytes(raw_bytes[20:22], "big")         # Byte 21-22
        self.occupation_code = int.from_bytes(raw_bytes[22:24], "big")       # Byte 23-24
        self.gathering_date = int.from_bytes(raw_bytes[24:26], "big")        # Byte 25-26 (19YYMM)
        self.scanning_date = int.from_bytes(raw_bytes[26:28], "big")         # Byte 27-28 (19YYMM)
        self.sample_pos_x = int.from_bytes(raw_bytes[28:30], "big")          # Byte 29-30
        self.sample_pos_y = int.from_bytes(raw_bytes[30:32], "big")          # Byte 31-32
        # Byte 33-60 (30 byte) = undefined

        # Parse ảnh (byte 61–8188 = 8128 byte)
        image_bytes = raw_bytes[60:8188]
        pixels = []
        for b in image_bytes:
            high = (b >> 4) & 0x0F
            low = b & 0x0F
            pixels.extend([high, low])
        pixels = pixels[:self.IMAGE_WIDTH * self.IMAGE_HEIGHT]
        
        self.image_array = np.array(pixels, dtype=np.uint8).reshape((self.IMAGE_HEIGHT, self.IMAGE_WIDTH))
        self.image_array = (self.image_array * 17).astype(np.uint8)  # scale 0–15 → 0–255

    def get_unicode_char(self) -> str:
        try:
            # Chuyển JIS bytes → EUC-JP bằng cách cộng offset 0x80
            euc_bytes = bytes([b + 0x80 for b in self.jis_code])
            return euc_bytes.decode("euc_jp")
        except:
            return "?"



    def get_pil_image(self) -> Image.Image:
        """Trả về ảnh PIL"""
        return Image.fromarray(self.image_array)
