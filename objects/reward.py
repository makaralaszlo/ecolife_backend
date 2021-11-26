import uuid


class Reward:
    """
    Jutalmat reprezántáló osztály.
    """

    def __init__(self, _id: str, title: str, description: str, company: str, redeem_code: str, expiration: str) -> None:
        """
        Inicializáló függvény.

        :param _id: Jutalom id-ja
        :param title: Jutalom neve
        :param description: Jutalom leírása
        :param company: Jutalmat kiíró cég neve
        :param redeem_code: Jutalomhoz tartozó 8 számjegyű kód
        :param expiration: Jutalom lejárati dátuma
        """
        self.__id = _id
        self.__title = title
        self.__description = description
        self.__company = company

        if redeem_code != '':
            self.__redeem_code = redeem_code
        else:
            self.__redeem_code = str(uuid.uuid4()).split('-')[0]
        self.__expiration = expiration

    def to_dict(self) -> dict:
        """
        Vissza adja a Reward objektumot dict formátumban. Adatbázisba iratás során igy kell kiiratni

        :return: objektum dict formában
        """
        if str(self.__id) != 'null':
            data = {
                '_id': str(self.__id),
                'title': self.__title,
                'description': self.__description,
                'company': self.__company,
                'redeem_code': self.__redeem_code,
                'expiration': self.__expiration
            }
        else:
            data = {
                'title': self.__title,
                'description': self.__description,
                'company': self.__company,
                'redeem_code': self.__redeem_code,
                'expiration': self.__expiration
            }
        return data

    def __eq__(self, other):
        """
        Egyenlőség operátor felül definiáls. ID alapján összehasonlítjuk a két objektumot és az alapján döntjük el,
        hogy azonos-e.

        :param other: Másik objektum
        :return: True/False
        """
        if not isinstance(other, Reward):
            return NotImplemented

        return self.__id == other.__id
