class Task:
    """
    Feladatokat repreználtáló osztály.
    """
    def __init__(self, _id: str, company: str, reward: str, max_submission_number: int, immediately_evaluated: bool,
                 title: str, description: str, expiration: str, submits: list) -> None:
        """
        Inicializáló függvény.

        :param _id: Feladat id-ja
        :param company: Feladatot kiíró cég neve
        :param reward: Feladathoz tartozó jutalom
        :param max_submission_number: Feladat maximális beadhatósági száma
        :param immediately_evaluated: Kiértékelődjön-e azonnal a feladat vagy képet kelljen csatolni
        :param title: Feladat neve
        :param description: Feladat leírása
        :param expiration: Feladat lejárata
        :param submits: Feladathoz beküldött képek a felhasználó által
        """
        self.__id = _id
        self.__company = company
        self.__reward = reward
        self.__max_submission_number = max_submission_number
        self.__immediately_evaluated = immediately_evaluated
        self.__title = title
        self.__description = description
        self.__expiration = expiration
        self.__submits = submits

    def __generate_qr_code(self):
        pass

    def to_dict(self) -> dict:
        """
        Vissza adja a Task objektumot dict formátumban. Adatbázisba iratás során igy kell kiiratni

        :return: objektum dict formában
        """
        return {
            '_id': self.__id,
            'company': self.__company,
            'reward': self.__reward,
            'max_submission_number': self.__max_submission_number,
            'immediately_evaluated': self.__immediately_evaluated,
            'title': self.__title,
            'description': self.__description,
            'expiration': self.__expiration,
            'submits': self.__submits
        }

    def __eq__(self, other):
        """
        Egyenlőség operátor felül definiáls. ID alapján összehasonlítjuk a két objektumot és az alapján döntjük el,
        hogy azonos-e.

        :param other: Másik objektum
        :return: True/False
        """
        if not isinstance(other, Task):
            return NotImplemented

        return self.__id == other.__id
