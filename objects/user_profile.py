from objects.basic_profile import BasicProfile


class UserProfile(BasicProfile):
    """
    Átlagos felhasználó profilt reprezántáló osztály.
    """

    def __init__(self, _id: str, email_address: str, first_name: str, last_name: str, date_of_birth: str, password: str,
                 rewards: list, tasks: list) -> None:
        """
        Inicializáló függvény.

        :param _id: Felhasználó idja
        :param email_address: Felhasználó email cime
        :param first_name: Felhasználó vezetékneve
        :param last_name: Felhasználó keresztneve
        :param date_of_birth: Felhasználó születési dátuma
        :param password: Felhasználó jelszava
        :param rewards: Felhasználó kuponjai
        :param tasks: Felhasználó feladatai
        """
        super().__init__(_id, email_address, first_name, last_name, date_of_birth, password)
        self.__rewards = rewards
        self.__tasks = tasks

    def to_dict(self) -> dict:
        """
        Vissza adja a AdminProfile objektumot dict formátumban. Adatbázisba iratás során igy kell kiiratni
        :return:
        """
        basicprofile_values = dict(super(UserProfile, self).to_dict().copy())
        basicprofile_values.update({'rewards': self.__rewards,
                                    'tasks': self.__tasks
                                    })
        return basicprofile_values

    def __eq__(self, other):
        """
        Egyenlőség operátor felül definiáls. ID alapján összehasonlítjuk a két objektumot és az alapján döntjük el,
        hogy azonos-e.

        :param other: Másik objektum
        :return: True/False
        """
        if not isinstance(other, UserProfile):
            return NotImplemented

        return self._id == other._id
