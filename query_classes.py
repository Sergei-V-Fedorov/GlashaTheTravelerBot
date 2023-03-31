"""Пользовательские классы"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class Hotel:
    """Класс, описывающий информацию об отеле"""
    id: int
    name: str = field(default_factory=str)
    web: str = field(default_factory=str)
    dist_from_center: str = None
    price: float = None
    total_price: float = None
    photos: List[str] = field(default_factory=list)

    def set_name(self, name: str) -> None:
        """Устанавливает поле name"""
        self.name = name

    def set_cite(self, cite: str) -> None:
        """Устанавливает поле web"""
        self.web = cite

    def set_distance(self, distance: str) -> None:
        """Устанавливает поле dist_from_center"""
        self.dist_from_center = distance

    def set_price(self, price: float) -> None:
        """Устанавливает поле price"""
        self.price = price

    def set_total_price(self, total_price: float) -> None:
        """Устанавливает поле total_price"""
        self.total_price = total_price

    def add_photo(self, photo_url: str) -> None:
        """добавляет url фотографии в список"""
        self.photos.append(photo_url)


@dataclass
class QueryResponse:
    """Класс, содержащий результаты поиска отелей"""
    hotel_list: List['Hotel'] = field(default_factory=list)
    status_code: int = None
    error_message: str = ""

    def add_hotel(self, element: 'Hotel') -> None:
        """Добавляет объект отель в список отелей"""
        self.hotel_list.append(element)


@dataclass
class UserQuery:
    """Класс, содержащий информацию пользовательского запроса"""
    user_id: int = None
    user_name: str = None
    destination_id: str = None
    destination: str = None
    check_in: str = None
    check_out: str = None
    adults: int = None
    hotel_number: int = 0
    picture_number: int = 0
    min_price: int = 0
    max_price: int = None
    min_distance: int = 0
    max_distance: int = None
    command: str = None
    datetime: str = None
    sort_order: str = None
    search_result: 'QueryResponse' = None


@dataclass
class History:
    """Класс для вывода информации об истории команд"""
    command: str = None
    datetime: str = None
    destination: str = None
    search_result: 'QueryResponse' = None
