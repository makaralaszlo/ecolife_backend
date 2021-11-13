from objects.basic_profile import BasicProfile


class AdminProfile(BasicProfile):
    """
    Adminisztrátor profil a weboldalhoz, ahonnan szerkeszteni lehet az egyes feladatokat és jutalmakat.
    """

    def __init__(self, _id: str, email_address: str, first_name: str, last_name: str, date_of_birth: str, password: str,
                 company: str, rewards: list, tasks: list) -> None:
        """
        Inicializáló függvény.

        :param id: Adminisztrátor profilhoz tartozó id
        :param email_address: Adminisztrátor e-mail címe
        :param first_name: Adminisztrátor keresztneve
        :param last_name: Adminisztrátor vezetékneve
        :param date_of_birth: Adminisztrátor születési dátuma
        :param password: Adminisztrátor jelszava
        :param company: Adminisztrátor cége
        :param rewards: Adminisztrátor által kiállított jutalmak
        :param tasks: Adminisztrátor által kiálított feladatok
        """
        super().__init__(_id, email_address, first_name, last_name, date_of_birth, password)
        self.__company = company
        self.__rewards = rewards
        self.__tasks = tasks

    def to_dict(self) -> dict:
        """
        Vissza adja a AdminProfile objektumot dict formátumban. Adatbázisba iratás során igy kell kiiratni
        :return:
        """
        basicprofile_values = dict(super(AdminProfile, self).to_dict().copy())
        basicprofile_values.update({'company': self.__company,
                                    'rewards': self.__rewards,
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
        if not isinstance(other, AdminProfile):
            return NotImplemented

        return self._id == other._id
