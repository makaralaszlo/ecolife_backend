import pymongo
import config.database_keys as database_keys


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
        self.__client = pymongo.MongoClient(f'mongodb+srv://ecolife_backend:{database_keys.PASSWORD}@cluster0.gymek.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
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

