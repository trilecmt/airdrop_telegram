import sqlite3
import datetime
import time

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


    def get_profiles_for_run(self,game,limit=1):
        query=f"SELECT * FROM schedule WHERE game='{game}' and IFNULL(next_run_date,0)<{int(time.time()*1000)} order by IFNULL (next_run_date,0) asc LIMIT {limit}"
        res = self.cur.execute(query)
        cur=res.fetchall()

        return cur
    
    def list_profiles(self,game):
        query=f"SELECT * FROM schedule WHERE game='{game}'"
        res = self.cur.execute(query)
        cur=res.fetchone()
        return cur
    
    def get_profile(self,profile_name,game):
        query=f"SELECT * FROM schedule WHERE game='{game}' and profile_name='{profile_name}'"
        res = self.cur.execute(query)
        cur=res.fetchone()
        if cur is not None:
            return {
                "game":cur[0],
                "profile":cur[1],
                "latest_run_date":datetime.datetime.strptime(cur[2],"%Y-%m-%dT%H:%M:%S.%fZ"),
                "next_run_date":datetime.datetime.strptime(cur[3],"%Y-%m-%dT%H:%M:%S.%fZ"),
            }
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
    game='BLUM'
    profile_name="Profile 2"
    schedule.update_profile(
        game=game,
        profile_name=profile_name,
        latest_run_date=datetime.datetime.utcnow(),
        next_run_date=datetime.datetime.utcnow()+datetime.timedelta(hours=8)
    )
    data=schedule.get_profiles_for_run(game=game,limit=10)
    print(data)
    
    pass
