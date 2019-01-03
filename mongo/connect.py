# made by jy
from mongoengine import connect
from mongoengine.context_managers import switch_db
from mongoengine.context_managers import switch_collection

connect('mydb', host='mongodb://kewp:kewp@wilkes.unist.ac.kr/kewp', port=27017)

class Tags10m():
    date = StringField()
    val = FloatField()

    meta = {'db_alias': kewp_10m}

class Tags1m():
    date = StringField()
    val = FloatField()

    meta = {'db_alias': kewp_1m}