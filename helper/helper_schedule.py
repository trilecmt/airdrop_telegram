import sqlite3
import datetime
file_path="schedule.db"

class ScheduleDB:
    def __init__(self,path) -> None:
        self.con = sqlite3.connect(path)
        self.cur = self.con.cursor()
        self.create_table(table_name='schedule',schema=["game","profile_name","latest_run_date", "next_run_date"])
    
    def is_exist_table(self,table_name):
        res = self.cur.execute(f"SELECT name FROM sqlite_master WHERE name='{table_name}'")
        return res.fetchone() is None

    def create_table(self,table_name,schema:list):
        res_check=self.cur.execute(f"SELECT name FROM sqlite_master WHERE name='{table_name}'")
        if res_check.fetchone() is None:   
            res_create=self.cur.execute(f"CREATE TABLE {table_name}({','.join(schema)})")
            print(res_create)
            print(f"Table {table_name} đã được tạo.")
        else:
            print(f"Table {table_name} đã tồn tại.")

    def get_profile(self,table_name,profile_name,game):
        res = self.cur.execute(f"SELECT * FROM {table_name} WHERE game='{game}' and profile_name='{profile_name}'")
        cur=res.fetchone()
        return cur
    
    def insert_profile(self,table_name,game,profile_name,latest_run_date,next_run_date):
        data=(game, profile_name, latest_run_date,next_run_date)
        self.cur.execute(f"INSERT INTO {table_name} VALUES(?, ?, ?,?)", data)
        self.con.commit()
        
    def update_profile(self,table_name,game,profile_name,latest_run_date,next_run_date):
        current_profile= self.get_profile(table_name=table_name,profile_name=profile_name,game=game)
        if current_profile is None:
            self.insert_profile(table_name=table_name,game=game,profile_name=profile_name,latest_run_date=latest_run_date,next_run_date=next_run_date)
        else:
            self.cur.execute(f"UPDATE {table_name} SET latest_run_date = '{latest_run_date}',next_run_date = '{next_run_date}' WHERE game = '{game}' and profile_name='{profile_name}'")
            self.con.commit()

if __name__=="__main__":
    schedule=ScheduleDB(path=file_path)
    table_name='schedule'
    game='blum'
    profile_name="Profile 2"
    schedule.update_profile(
        table_name=table_name,
        game=game,
        profile_name=profile_name,
        latest_run_date=datetime.datetime.utcnow(),
        next_run_date=datetime.datetime.utcnow()+datetime.timedelta(hours=8)
    )
