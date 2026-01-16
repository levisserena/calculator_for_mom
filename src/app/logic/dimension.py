from decimal import Decimal
from enum import Enum


class Category(Enum):
    LENGTH = 'длина'
    VOLUME = 'объем'
    MASSA = 'масса'
    PIECE = 'шт'


class DimensionType:
    def __init__(
        self, dimension: str, category: Category, weight: int
    ) -> None:
        self.dimension = dimension
        self.category = category
        self.weight = weight


class DimensionConverter(Enum):
    PIECE = DimensionType('шт', Category.PIECE, 1)
    METRE = DimensionType('м', Category.LENGTH, 1)
    DECIMETER = DimensionType('дм', Category.LENGTH, 10)
    CENTIMETRE = DimensionType('см', Category.LENGTH, 100)
    MILLIMETER = DimensionType('мм', Category.LENGTH, 1000)
    CUBIC_METRE = DimensionType('м³', Category.VOLUME, 1)
    LITER = DimensionType('л', Category.VOLUME, 1000)
    MILLILITER = DimensionType('мл', Category.VOLUME, 1_000_000)
    KILOGRAM = DimensionType('кг', Category.MASSA, 1)
    GRAM = DimensionType('г', Category.MASSA, 1000)

    @classmethod
    def get_ratio(cls, current_dimension: str, db_dimension: str) -> Decimal:
        """Вернет коэффициент перевода из одной единицы измерения в другую."""
        current_ratio = db_ratio = None

        for dim in cls:
            if dim.value.dimension == current_dimension:
                current_ratio = dim.value.weight
            if dim.value.dimension == db_dimension:
                db_ratio = dim.value.weight

        if current_ratio is not None and db_ratio is not None:
            return Decimal(db_ratio) / Decimal(current_ratio)

        return Decimal(1)

    @classmethod
    def get_dimensions_same_category(cls, dimension: str) -> list[str] | None:
        """
        Вернет все размерности той же категории, что и полученная размерность.
        """
        category = None

        for dim in cls:
            if dim.value.dimension == dimension:
                category = dim.value.category
                break

        if not category:
            return None

        return [
            dim.value.dimension
            for dim in cls
            if dim.value.category == category
        ]

    @classmethod
    def get_all(cls) -> list[str]:
        """Вернет все размерности."""
        return [dim.value.dimension for dim in cls]
