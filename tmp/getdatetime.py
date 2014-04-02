import datetime
def GetToday():
    now = datetime.date.today()
    return now.strftime("%Y-%m-%d")

if __name__ == '__main__':
    print GetToday()

