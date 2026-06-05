from models import Photo, Keyword


class PhotoService:
    """Read operations for the photo gallery."""

    @staticmethod
    def search_by_keyword(keyword):
        """Return photos whose linked keywords contain the given substring."""
        return Photo.query.join(Keyword).filter(
            Keyword.keyword.contains(keyword)
        ).all()

    @staticmethod
    def get_all_photos(limit=20):
        """Return the most recently inserted photos up to ``limit``."""
        return Photo.query.limit(limit).all()


class KeywordService:
    """Keyword autocomplete backed by the keywords table."""

    @staticmethod
    def suggest(prefix: str, limit: int = 10) -> list[str]:
        """Return up to ``limit`` keyword strings matching ``prefix`` (case-insensitive)."""
        if not prefix:
            return []
        matches = (
            Keyword.query.filter(Keyword.keyword.ilike(f"%{prefix}%"))
            .limit(limit)
            .all()
        )
        return [k.keyword for k in matches]
