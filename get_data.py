import os

# from fastcore import fastcore
import wget


def main():
    # path = Path('data')

    if not os.path.exists("data/Daily-train.csv"):
        wget.download(
            "https://raw.githubusercontent.com/M4Competition/M4-methods/master/Dataset/Train/Daily-train.csv",
            "m4_daily/train.csv",
        )
    if not os.path.exists("data/Daily-test.csv"):
        wget.download(
            "https://raw.githubusercontent.com/M4Competition/M4-methods/master/Dataset/Test/Daily-test.csv",
            "m4_daily/test.csv",
        )


if __name__ == "__main__":
    main()
