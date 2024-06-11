import sqlite3
import datetime

class ScheduleDB:
    def __init__(self,path='schedule.db') -> None:
        self.con = sqlite3.connect(path)
        self.cur = self.con.cursor()
        self.create_table(schema=["game","profile_name","latest_run_date", "next_run_date"])
    
    def is_exist_table(self):
        res = self.cur.execute(f"SELECT name FROM sqlite_master WHERE name='schedule'")
        return res.fetchone() is None

    def create_table(self,schema:list):
        res_check=self.cur.execute(f"SELECT name FROM sqlite_master WHERE name='schedule'")
        if res_check.fetchone() is None:   
            res_create=self.cur.execute(f"CREATE TABLE schedule({','.join(schema)})")
            print(res_create)
            print(f"Table schedule đã được tạo.")
        else:
            print(f"Table schedule đã tồn tại.")

    def get_profile(self,profile_name,game):
        res = self.cur.execute(f"SELECT * FROM schedule WHERE game='{game}' and profile_name='{profile_name}'")
        cur=res.fetchone()
        return cur
    
    def insert_profile(self,game,profile_name,latest_run_date,next_run_date):
        data=(game, profile_name, latest_run_date,next_run_date)
        self.cur.execute(f"INSERT INTO schedule VALUES(?, ?, ?,?)", data)
        self.con.commit()
        
    def update_profile(self,game,profile_name,latest_run_date,next_run_date):
        current_profile= self.get_profile(profile_name=profile_name,game=game)
        if current_profile is None:
            self.insert_profile(game=game,profile_name=profile_name,latest_run_date=latest_run_date,next_run_date=next_run_date)
        else:
            self.cur.execute(f"UPDATE schedule SET latest_run_date = '{latest_run_date}',next_run_date = '{next_run_date}' WHERE game = '{game}' and profile_name='{profile_name}'")
            self.con.commit()

if __name__=="__main__":
    schedule=ScheduleDB()
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
