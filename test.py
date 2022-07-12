from bearing.bearingdata import  XJTUData
from bearing.db import Database

def refresh_features():
    db = Database()
    db.delete_all_features()
    xjtu = XJTUData()
    xjtu.refresh_features(db)

db = Database()
for x in db.list_features("Bearing3_1", "H", "rms", "std_var"):
    print(x[0])