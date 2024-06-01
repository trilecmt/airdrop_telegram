import hamster
import cexp
import time


def main():
    pass

if __name__=="__main__":
    while True:
        print("*****PROCESS HAMSTER****")
        hamster.main(delay_time=10)
        
        print("*****PROCESS CEXP****")
        cexp.main(delay_time=10)
        
        print("*****SLEEP***")
        time.sleep(10*60)