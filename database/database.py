import pymongo
import config.database_keys as database_keys
import typing


class DataBase:
    """
    DataBase osztály ne példányosítsd közvetlenül! Az örökléshez van készítve.
    """

    def __init__(self, database: str, collection: str) -> None:
        """
        Inicializáló függvény, létrehozza a database-t ha nem létezik, illetve a kollekciót.

        :rtype None
        :param database: adatbázis név
        :param collection: kollekció név
        """
        self.__client = pymongo.MongoClient(
            f'mongodb+srv://ecolife_backend:{database_keys.PASSWORD}@cluster0.gymek.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
        self.__database_name = database
        self.__collection_name = collection

        if database in self.__client.list_database_names():
            self.__database = self.__client.get_database(database)
        else:
            self.__database = self.__client[database]

        if collection in self.__database.collection_names():
            self.__collection = self.__database.get_collection(collection)
        else:
            self.__collection = self.__database[collection]

    def insert_element(self, search_data_dict: dict, insert_data_dict: dict) -> typing.Tuple[str, bool]:
        """
        Az átadott dictionary elemeiet beilleszti az adott adatbázisba.

        :param data_dict: beillesztendő adatok
        :return: sikeresség
        """
        if self.get_element(search_data_dict).count() > 0:
            res, success = 'Element already exists in the DataBase!', False
        else:
            res, success = self.__collection.insert(insert_data_dict), True
        return str(res), success

    def get_element(self, search_fields: dict) -> pymongo.CursorType:
        """
        Dicitonaryként kell átadni a search fieldset, majd ezeket az adott collectionban megkeresi és visszadja.

        :param search_fields: keresendő mezőértékek
        :return: megtalált rekordok
        """
        return self.__collection.find(search_fields)

    def drop_collection(self) -> str:
        """
        Törli a kollekciót az összes tartalmával.

        :return: sikerességi kimenetel
        """
        res = self.__collection.drop()
        return res
