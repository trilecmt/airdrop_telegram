import hamster
import cexp
import time
import memefiv2


def main():
    pass

if __name__=="__main__":
    while True:
        print("*****PROCESS HAMSTER****")
        hamster.main(delay_time=10,count_processes =1)
        
        print("*****PROCESS CEXP****")
        cexp.main(delay_time=10)
        
        print("*****PROCESS MEMEFI****")
        memefiv2.main(delay_time=10)
        
        print("*****SLEEP***")
        time.sleep(10*60)