from datetime import datetime

nameList = ['Lapf', 'Tigersaber', 'bliip', 'Jhizz', 'Vlyper']
eloList = ['iron', 'bronze', 'silver', 'gold', 'platinum',
           'diamond', 'master', 'grandmaster', 'challenger']
divisionNumber = ["1", "2", "3", "4"]
splitMessageCommands = ["$insert", "$update"]
pirloList = ['Delta Krow', 'Paulo', 'Pirlo',
             'Perlo', 'Delta Crow', 'DeltaCrow']


def DateVerify(date):
    try:
        dateTest = datetime.strptime(date, "%d/%m/%Y")
        return True
    except:
        return False


def VerifyMessage(message):
    splitMessage = message.split()
    splitMessage.remove(splitMessage[0])
    if((len(splitMessage) == 5 and splitMessage[0] in nameList and splitMessage[1].lower() in eloList and splitMessage[2].lower() in divisionNumber and DateVerify(splitMessage[3]) and 0 <= int(splitMessage[4]) <= 100) or (len(splitMessage) == 1 and DateVerify(splitMessage[0]))):
        return True
    else:
        return False
