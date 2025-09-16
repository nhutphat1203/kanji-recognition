from pathlib import Path
from obj.record_etl8g import RecordETL8G
from tqdm import tqdm 

class ETL8GExtractor:
    def __init__(self, data_dir: Path, save_dir: Path):
        self.data_dir = Path(data_dir)
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)

    def extract_from_file(self, file_path: Path, n_records: int = None):
        count = 0
        file_size = file_path.stat().st_size
        total_records = file_size // RecordETL8G.RECORD_SIZE

        if n_records is not None:
            total_records = min(total_records, n_records)

        with file_path.open("rb") as f:
            for _ in tqdm(range(total_records), desc=f"Extracting {file_path.name}", unit="rec"):
                record_bytes = f.read(RecordETL8G.RECORD_SIZE)
                if not record_bytes or len(record_bytes) < RecordETL8G.RECORD_SIZE:
                    break
                
                rec = RecordETL8G(record_bytes)
                count += 1
                char = rec.get_unicode_char()
                img = rec.get_pil_image()

                char_dir = self.save_dir / char
                char_dir.mkdir(parents=True, exist_ok=True)

                img_path = char_dir / f"{file_path.stem}_rec{count}.png"
                img.save(img_path)

        print(f"Done! Extracted {count} records from {file_path.name}")

    def extract_all(self, n_records: int = None):
        for file_path in sorted(self.data_dir.glob("ETL8G_*")):
            self.extract_from_file(file_path, n_records=n_records)
