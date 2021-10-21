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
        _, exists = self.get_element(search_data_dict)
        if exists:
            res, success = 'Element already exists in the DataBase!', False
        else:
            res, success = self.__collection.insert(insert_data_dict), True
        return str(res), success

    def get_element(self, search_fields: dict) -> typing.Tuple[typing.Union[list, str], bool]:
        """
        Dicitonaryként kell átadni a search fieldset, majd ezeket az adott collectionban megkeresi és visszadja.

        :param search_fields: keresendő mezőértékek
        :return: megtalált rekordok
        """
        resp_data = []
        if self.__collection.find(search_fields).count() > 0:
            for element in self.__collection.find(search_fields):
                resp_data.append(element)
            return resp_data, True
        else:
            return 'Element does not exists in the DataBase!', False

    def delete_element(self, search_fields: dict) -> typing.Tuple[typing.Union[int, str], bool]:
        """
        Dictionaryban átadott elemek törlése az adatbázisból.

        :param search_fields: törölendő rekordok kereső értéke
        :return: törölt rekordok száma
        """
        resp = self.__collection.delete_many(search_fields)
        if resp.deleted_count > 0:
            return resp.deleted_count, True
        else:
            return 'Element does not exists in the DataBase!', False

    def drop_collection(self) -> str:
        """
        Törli a kollekciót az összes tartalmával.

        :return: sikerességi kimenetel
        """
        res = self.__collection.drop()
        return res
