import os 
from fastcore import fastcore
import wget

def main():
    path = Path('data')
    
    if not os.path.exists('data/Daily-train.csv'):
        wget.download('https://raw.githubusercontent.com/M4Competition/M4-methods/master/Dataset/Train/Daily-train.csv',path)
    if not os.path.exists('data/Daily-test.csv'):
        wget.download('https://raw.githubusercontent.com/M4Competition/M4-methods/master/Dataset/Test/Daily-test.csv',path)

if __name__ == "__main__":
    main()
