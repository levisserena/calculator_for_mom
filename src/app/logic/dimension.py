from decimal import Decimal
from enum import Enum


class Category(Enum):
    LENGTH = 'длина'
    VOLUME = 'объем'
    MASSA = 'масса'
    PIECE = 'шт'


class DimensionType:
    def __init__(
        self, dimension: str, category: Category, weight: int, base: bool
    ):
        self.dimension = dimension
        self.category = category
        self.weight = weight
        self.base = base


class DimensionConverter(Enum):
    PIECE = DimensionType('шт', Category.PIECE, 1, True)
    METRE = DimensionType('м', Category.LENGTH, 1, True)
    DECIMETER = DimensionType('дм', Category.LENGTH, 10, False)
    CENTIMETRE = DimensionType('см', Category.LENGTH, 100, False)
    MILLIMETER = DimensionType('мм', Category.LENGTH, 1000, False)
    CUBIC_METRE = DimensionType('м³', Category.VOLUME, 1, False)
    LITER = DimensionType('л', Category.VOLUME, 1000, True)
    MILLILITER = DimensionType('мл', Category.VOLUME, 1_000_000, False)
    KILOGRAM = DimensionType('кг', Category.MASSA, 1, False)
    GRAM = DimensionType('г', Category.MASSA, 1000, True)

    @classmethod
    def get_base(cls, dimension: str, value: Decimal) -> tuple[str, str]:
        """Вернет базовую размерность и множитель."""
        cursor = [dim for dim in cls if dim.value.dimension == dimension][0]
        category = cursor.value.category
        base = [
            dim
            for dim in cls
            if dim.value.category == category and dim.value.base
        ][0]
        ratio = str(
            value / Decimal(cursor.value.weight) * Decimal(base.value.weight)
        )
        return base.value.dimension, ratio

    @classmethod
    def get_dimensions_by_category(cls, category: Category) -> list[str]:
        """Вернет все размерности для данной категории."""
        return [
            dim.value.dimension
            for dim in cls
            if dim.value.category == category
        ]

    @classmethod
    def get_category_by_dimension(cls, dimension: str) -> Category | None:
        """Вернет категорию для данной размерности."""
        categories = [
            dim.value.category
            for dim in cls
            if dim.value.dimension == dimension
        ]
        return categories[0] if categories else None

    @classmethod
    def get_all(cls) -> list[str]:
        """Вернет все размерности."""
        return [dim.value.dimension for dim in cls]
