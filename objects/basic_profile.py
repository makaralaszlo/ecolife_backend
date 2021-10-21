import typing
import hashlib
import jwt


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
        # új profil esetén nem lesz ID, a mongodb fogja ezt előállítani
        self._id = _id
        self._email_address = email_address
        self._first_name = first_name
        self._last_name = last_name
        self._date_of_birth = date_of_birth

        # password hash a security érdekében
        if _id == 'null':
            #self._salt = uuid.uuid4().hex
            #self._password = hashlib.sha512((password + self._salt).encode('utf-8')).hexdigest()
            self._password = hashlib.sha512((password).encode('utf-8')).hexdigest()
        else:
            self._password = password

    def to_dict(self) -> dict:
        """
        Vissza adja a BasicProfile objektumot dict formátumban. Adatbázisba iratás során igy kell kiiratni

        :return: objektum dict formában
        """
        if str(self._id) != 'null':
            data = {
                '_id': str(self._id),
                'email_address': self._email_address,
                'first_name': self._first_name,
                'last_name': self._last_name,
                'date_of_birth': self._date_of_birth,
                'password': self._password
            }
        else:
            data = {
                'email_address': self._email_address,
                'first_name': self._first_name,
                'last_name': self._last_name,
                'date_of_birth': self._date_of_birth,
                'password': self._password
            }

        return data

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

    def get_bearer_token(self) -> str:
        self._jwt = jwt.encode(
            {
                'iss': 'EcoLife',
                'sub': str(self._id),
                'name': self._first_name + self._last_name
            },
            'secret',
            algorithm='HS256'
        )
        return self._jwt

    def get_profile_based_on_token(self, token: str) -> bool:
        data = jwt.decode(token, 'secret', algorithms=['HS256'])
        if data['sub'] == str(self._id):
            return True
        return False
