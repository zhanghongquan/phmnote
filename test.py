from bearing.bearingdata import  XJTUData
from bearing.features import Database

def refresh_features():
    db = Database()
    db.delete_all_features()
    xjtu = XJTUData()
    xjtu.refresh_features(db)

db = Database()
for x in db.list_features("Bearing3_1", "rms", "std_var"):
    print(x)