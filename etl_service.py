import os
import csv
import logging
from typing import List, Dict
from models import db, Photo, Keyword, Color
# Set your data folder
DATA_DIR = os.path.abspath("data")
logging.basicConfig(level=logging.INFO)

class ETLService:
    # -------------------- EXTRACT --------------------
    def extract(self, filepath: str) -> List[Dict]:
        filepath = os.path.abspath(filepath)

        if not filepath.startswith(DATA_DIR):
            raise PermissionError("Invalid file path")

        if not os.path.exists(filepath):
            raise FileNotFoundError(filepath)

        logging.info(f"Extracting data from {filepath}")

        with open(filepath, encoding='utf-8') as f:
            return list(csv.DictReader(f, delimiter="\t"))
    # -------------------- TRANSFORM --------------------
    def transform_photos(self, raw_data: List[Dict]) -> List[Dict]:
        cleaned = []

        for row in raw_data:
            try:
                cleaned.append({
                    "photo_id": row["photo_id"],
                    "image_url": row["photo_image_url"],
                    "description": (row.get("photo_description") or "").strip(),
                    "width": int(row.get("photo_width") or 0),
                    "height": int(row.get("photo_height") or 0),
                    "username": row.get("photographer_username", "").strip()
                })
            except Exception as e:
                logging.warning(f"Skipping photo row: {e}")
                continue

        logging.info(f"Transformed {len(cleaned)} photos")
        return cleaned
    def transform_keywords(self, raw_data: List[Dict]) -> List[Dict]:
        cleaned = []

        for row in raw_data:
            if not row.get("keyword"):
                continue

            try:
                cleaned.append({
                    "photo_id": row["photo_id"],
                    "keyword": row["keyword"].strip()
                })
            except Exception as e:
                logging.warning(f"Skipping keyword row: {e}")
                continue

        logging.info(f"Transformed {len(cleaned)} keywords")
        return cleaned
    def transform_colors(self, raw_data: List[Dict]) -> List[Dict]:
        cleaned = []

        for row in raw_data:
            try:
                cleaned.append({
                    "photo_id": row["photo_id"],
                    "hex": row["hex"],
                    "color_name": row.get("keyword", "").strip()
                })
            except Exception as e:
                logging.warning(f"Skipping color row: {e}")
                continue

        logging.info(f"Transformed {len(cleaned)} colors")
        return cleaned
    # -------------------- LOAD --------------------
    def load_photos(self, data: List[Dict]):
        for d in data:
            exists = Photo.query.get(d["photo_id"])
            if not exists:
                db.session.add(Photo(**d))

        db.session.commit()
        logging.info(f"Loaded {len(data)} photos")
    def load_keywords(self, data: List[Dict]):
        for d in data:
            db.session.add(Keyword(**d))

        db.session.commit()
        logging.info(f"Loaded {len(data)} keywords")
    def load_colors(self, data: List[Dict]):
        for d in data:
            db.session.add(Color(**d))

        db.session.commit()
        logging.info(f"Loaded {len(data)} colors")
    # -------------------- RUN PIPELINE --------------------
    def run(self):
        # Photos
        raw_photos = self.extract("data/photos.csv000")
        photos = self.transform_photos(raw_photos)
        self.load_photos(photos)
        # Keywords
        raw_keywords = self.extract("data/keywords.csv000")
        keywords = self.transform_keywords(raw_keywords)
        self.load_keywords(keywords)
        # Colors
        raw_colors = self.extract("data/colors.csv000")
        colors = self.transform_colors(raw_colors)
        self.load_colors(colors)