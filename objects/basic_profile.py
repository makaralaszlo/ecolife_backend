import typing


class BasicProfile:
    """
    Profilok ősosztálya ebből kerül példányosításra az admin és a user profile.
    """
    def __init__(self, _id: str, email_address: str, first_name: str, last_name: str, date_of_birth: str, password: str)\
            -> None:
        """
        Inicilaizáló függvény.

        :param id: profilhoz tartozó id
        :param email_address: profilhoz tartozó e-mail cím
        :param first_name: profilhoz tartozó keresztnév
        :param last_name: profilhoz tartozó vezetéknév
        :param date_of_birth: profilhoz tartozó születésdátum
        :param password: profilhoz tartozó jelszó
        """
        self._id = _id
        self._email_address = email_address
        self._first_name = first_name
        self._last_name = last_name
        self._date_of_birth = date_of_birth
        self._password = password

    def to_dict(self) -> dict:
        """
        Vissza adja a BasicProfile objektumot dict formátumban. Adatbázisba iratás során igy kell kiiratni

        :return: objektum dict formában
        """
        return {
            '_id': self._id,
            'email_address': self._email_address,
            'first_name': self._first_name,
            'last_name': self._last_name,
            'date_of_birth': self._date_of_birth,
            'password': self._password
        }

    def __eq__(self, other: typing.Any) -> bool:
        """
        Egyenlőség operátor felül definiáls. ID alapján összehasonlítjuk a két objektumot és az alapján döntjük el,
        hogy azonos-e.

        :param other: Másik objektum
        :return: True/False
        """
        if not isinstance(other, BasicProfile):
            return NotImplemented

        return self._id == other._id
