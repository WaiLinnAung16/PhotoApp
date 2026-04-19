from models import Photo, Keyword

class PhotoService:
    @staticmethod
    def search_by_keyword(keyword):
        return Photo.query.join(Keyword).filter(
            Keyword.keyword.contains(keyword)
        ).all()

    @staticmethod
    def get_all_photos(limit=20):
        return Photo.query.limit(limit).all()
    

    