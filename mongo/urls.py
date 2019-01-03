from django.conf.urls import url
from mongo.views import mongoAPI

urlpatterns = [
    # mongoDB API
    url(r'^tag', mongoAPI.connect_mongo_tag),
    url(r'^all', mongoAPI.connect_mongo_all),
    url(r'^data', mongoAPI.connect_mongo_data),
    url(r'^json', mongoAPI.connect_mongo_json),
    url(r'^history', mongoAPI.connect_mongo_history),
    url(r'^power', mongoAPI.connect_mongo_power),
    url(r'^important', mongoAPI.connect_mongo_important),
    url(r'^changeth', mongoAPI.connect_mongo_change_th),
    url(r'^stopdata', mongoAPI.connect_mongo_stop),
    url(r'^structure', mongoAPI.return_structure),
    url(r'^stop', mongoAPI.return_stophistory),
    url(r'^correlation', mongoAPI.return_correlation),
    url(r'^simulation', mongoAPI.simulation_json),
    url(r'^listdata', mongoAPI.connect_mongo_list_data),
    url(r'^simulationlistdata', mongoAPI.simulation),
]