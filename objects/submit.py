import typing


class Submit:
    """
    Egy beküldött feladatot reprezántáló osztály. QR kód esetén is példányosítani kell.
    """
    def __init__(self, user_id: str, task_id: str, image: typing.Any, state: str) -> None:
        """
        Inicializáló függvény.

        :param user_id: A feladathoz beküldő user ID-ja adatbázisból
        :param task_id: A feladat ID-ja adatbázisból
        :param image: A beküldött kép
        :param state: Állapota a beküldésnek ['ACCEPTED', 'REJECTED', 'PENDING']
        """
        self.__user_id = user_id
        self.__task_id = task_id
        self.__image = image
        self.__state = state

    def to_dict(self) -> dict:
        """
        Vissza adja a Submit objektumot dict formátumban. Adatbázisba iratás során igy kell kiiratni

        :return: objektum dict formában
        """
        return {
            'user_id': self.__user_id,
            'task_id': self.__task_id,
            'image': self.__image,
            'state': self.__state
        }

    def __eq__(self, other: typing.Any) -> bool:
        """
        Egyenlőség operátor felül definiáls. ID alapján összehasonlítjuk a két objektumot és az alapján döntjük el,
        hogy azonos-e.

        :param other: Másik objektum
        :return: True/False
        """
        if not isinstance(other, Submit):
            return NotImplemented

        return self.__user_id == other.__user_id and self.__task_id == other.__task_id
