import hamsterv2
import cexpv2
import time


def main():
    pass

if __name__=="__main__":
    while True:
        print("*****PROCESS HAMSTER****")
        hamsterv2.main(delay_time=10)
        
        print("*****PROCESS CEXP****")
        cexpv2.main(delay_time=10)
        
        print("*****SLEEP***")
        time.sleep(10*60)