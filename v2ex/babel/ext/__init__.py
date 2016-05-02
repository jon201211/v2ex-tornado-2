from storm.locals import *
from storm.sqlobject import *
#from sqlobject import *

#sqlhub.processConnection = connectionForURI('mysql://mysql:123@localhost:3306/v2ex')
databae = create_database('mysql://mysql:123@localhost:3306/v2ex')
store = Store(databae)
class SQLObject(SQLObjectBase):
    @staticmethod
    def _get_store():
        return store