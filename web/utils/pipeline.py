# @falcon.ny
__author__ = 'nosoyyo'
__version__ = {'0.1': '2018.01',
               '0.2': '2018.02',
               '0.3': '2018.05.23',
               '0.4': '2018.05.31',
               '0.41': '2018.10.29',
               '0.42': '2018.12.8',
               '0.43': '2018.12.18'
               '0.44': '2018.12.28'
               }

# 0.1 basically setup
# 0.2 base class changed into singleton mode; added user/pwd auth;
# 0.3 removed singleton mode, added basic CRUD method wrappers
# 0.4 add `ls` behaviour customization
# 0.41 implemented on BumbleBee; exchanged lots of f-strings;
# 0.42 implemented on NemBee; now only connects on __init__
# 0.43 implemented on kb; nothing really changed except for some defaults
# 0.43 implemented on jielong; nothing really changed except for some defaults
# TODO: check the im

import os
import logging
import pymongo
from bson.objectid import ObjectId
from pymongo.collection import Collection


settings = {}
settings['MONGODB_SERVER'] = os.environ.get('LOCAL_MONGODB_SERVER')
settings['MONGODB_PORT'] = int(os.environ.get('LOCAL_MONGODB_PORT'))
settings['MONGODB_USERNAME'] = os.environ.get('LOCAL_MONGODB_USERNAME')
settings['MONGODB_PASSWORD'] = os.environ.get('LOCAL_MONGODB_PASSWORD')
settings['MONGODB_NEMBEE_DB'] = 'jielong'
settings['MONGODB_INIT_COL'] = 'test'

# init
if 'log' not in os.listdir():
    os.mkdir('log')

logging.basicConfig(
    filename='log/mongodb.log',
    level=logging.INFO,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')


# ==================
# MongoDB quickstart
# ==================
class MongoDBPipeline():

    def __init__(self):
        self.client = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT'],
        )
        self.db = self.client.get_database(settings['MONGODB_NEMBEE_DB'])
        self.auth = self.db.authenticate(
            settings['MONGODB_USERNAME'],
            settings['MONGODB_PASSWORD']
        )
        self.col = self.db.get_collection(settings['MONGODB_INIT_COL'])

    def setDB(self, dbname):
        self.db = self.client.get_database(dbname)
        return self

    def setCol(self, colname, dbname=None):
        if dbname:
            self.db = self.client.get_database(dbname)
        return self.db.get_collection(colname)

    def dealWithCol(self, _col=None) -> Collection:
        try:
            if not _col:
                col = self.col
            elif isinstance(_col, Collection):
                col = _col
            elif isinstance(_col, str):
                col = self.setCol(_col)
            else:
                raise NotImplementedError
            return col
        except Exception as e:
            logging.error(f'dealWithCol raises {e}')

    def insert(self, doc: dict, col: str = None) -> ObjectId:
        col = self.dealWithCol(col)
        try:
            oid = col.insert_one(doc).inserted_id
            if isinstance(oid, ObjectId):
                logging.debug(f'doc {doc} inserted into {col.name}')
                return oid
        except Exception as e:
            logging.error(f'pipeline.insert() raises {e}')

    def ls(self, arg=None, col=None, **kwargs):
        col = self.dealWithCol(col)

        if arg is None:
            return self.db.list_collection_names()
        elif isinstance(arg, str):
            col = self.dealWithCol(arg)
            return [item for item in col.find()]
        elif isinstance(arg, int) and col is None:
            col = self.ls()[arg]
            return self.ls(col)
        elif isinstance(arg, dict):
            logging.debug(f'looking for {arg} in "{col.name}"')
            return [item for item in col.find(arg)]
        elif isinstance(arg, ObjectId):
            return col.find_one({'_id': arg})
        elif col.name in self.custom_ls_behaviour_col:
            return self.custom_ls(arg=arg, col=col, **kwargs)
        elif kwargs:
            # TODO
            return col.find_one(kwargs)

    def update(self, oid: ObjectId, doc: dict, col: str = None) -> bool:
        col = self.dealWithCol(col)

        try:
            result = col.update_one({'_id': oid}, {"$set": doc},)
            if result.modified_count:
                logging.debug(f'updated {doc} in {col.name}, result[{result}]')
                flag = True
            else:
                if result.matched_count:
                    logging.debug(
                        f'{doc} not updated in {col.name}, input same to output.')
                    flag = False
                else:
                    logging.debug(
                        f'{doc} not updated in {col.name}, nothing matches input.')
                    flag = False

            return flag
        except Exception as e:
            logging.error(f'm.update raises {e}')
            return False

    def rm(self, arg, col=None):
        '''
        Supports deleting by oid for now.

        :param oid: `bson.objectid.ObjectId`
        '''
        col = self.dealWithCol(col)

        if isinstance(arg, ObjectId):
            try:
                result = bool(col.delete_one(
                    {'_id': arg}).raw_result['n']) or False
                logging.info(f'deleting {arg} in {col.name}, result[{result}]')
                return result
            except Exception as e:
                logging.error(
                    f'm.rm raises {e} during deleting by ObjectId')
                return False
        elif isinstance(arg, dict):
            try:
                if '_id' in arg.keys() and isinstance(arg['_id'], ObjectId):
                    return self.rm(arg['_id'], col)
                else:
                    return False
            except Exception as e:
                logging.error(f'm.rm raises {e} during deleting doc')
                return False
        else:
            return False
