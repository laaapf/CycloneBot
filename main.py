import os
import verifications
import discord
from riotwatcher import LolWatcher, ApiError
import datetime
import time
from discord.ext import tasks, commands
import threading
import psycopg2
from psycopg2 import Error

connection = psycopg2.connect(os.environ.get('DATABASE_URL'))
myRegion = "br1"
client = discord.Client()
watcher = LolWatcher(os.environ.get('RIOT_API_TOKEN'))


class database:

    def InsertionChecktime(nowtime):
        if(nowtime.strftime("%H:%M:%S") == "03:02:00"):
            try:
                leagueapi.InsertData(leagueapi.getSummonerData())
                print("Insertion completed")
            except:
                print("Insertion failed")

    def InsertNewRecords():
        threading.Timer(1, database.InsertNewRecords).start()
        now = datetime.datetime.now()
        print(now.strftime("%H:%M:%S"))
        database.InsertionChecktime(now)

    async def Connect():
        global user
        user = await client.fetch_user("162974176544686081")
        try:
            await discord.DMChannel.send(user, "Database connected")
        except:
            await discord.DMChannel.send(user, "Database didn't connect | Bot turning off")
            quit()

    def SplitMessage(command, message):
        if(message[0] in verifications.splitMessageCommands):
            splittedMessage = message.split()
            splittedMessage.remove(splittedMessage[0])
            splittedMessage[4] = int(splittedMessage[4])
        else:
            splittedMessage = message.split()
            splittedMessage.remove(splittedMessage[0])
        return splittedMessage

    def AdjustmentsForSoloqueueInsertion():
        yesterdayDate = (datetime.datetime.now() - datetime.timedelta(2)
                         ).strftime('%d/%m/%Y')
        yesterdayData = database.SelectData([yesterdayDate], 1)
        deleteTempData = """DELETE FROM TempTable;"""
        cursor = connection.cursor()
        try:
            cursor.execute(deleteTempData)
            connection.commit()
            for row in yesterdayData:
                yesterdayQuery = f'''INSERT INTO TempTable (name,date,division,elo,current_lp) VALUES {row};'''
                cursor.execute(yesterdayQuery)
                connection.commit()
            cursor.close()
            return True
        except:
            cursor.close()
            return False

    def InsertDataIntoSoloqueue(data):
        cursor = connection.cursor()
        print(data)
        query = f'''INSERT INTO SoloqueueData (name,date,division,elo,current_lp) VALUES {data};'''
        cursor.execute(query)
        connection.commit()
        cursor.close()
        print("Data inserted succesfully!")

    # def UpdateData(message):
    #     dbCursor = db.cursor()
    #     query = """UPDATE SoloqueueData set elo = ?, division = ?, current_lp = ? WHERE name = ? AND date = ?"""
    #     dbCursor.execute(query, (message[1], message[2],
    #                              message[4], message[0], message[3]))
    #     db.commit()
    #     if(dbCursor.rowcount < 1):
    #         dbCursor.close()
    #         return("No update executed!")
    #     dbCursor.close()
    #     return("Updated!")

    def SelectData(message, *identifier):
        cursor = connection.cursor()
        query = f'''SELECT * FROM SoloqueueData WHERE date LIKE '{message[0]}' '''
        cursor.execute(query)
        queryResult = cursor.fetchall()
        resultText = f"**DATE: {message[0]}** ```autohotkey\n\n"
        if(len(identifier) == 0):
            if(len(queryResult) <= 1):
                cursor.close()
                return("No records found!")
            for row in queryResult:
                resultText += row[0] + " | " + row[3] + " | " + \
                    str(row[2]) + " | " + str(row[4]) + " LP \n"
            resultText += "```"
            cursor.close()
            return resultText
        else:
            cursor.close()
            return queryResult


class leagueapi:
    def getSummonerData():
        summonerListStats = []
        for nickname in verifications.nameList:
            summoner = watcher.summoner.by_name(myRegion, nickname)
            stats = watcher.league.by_summoner(myRegion, summoner['id'])
            for information in stats:
                if(information['queueType'] == 'RANKED_SOLO_5x5'):
                    summonerListStats.append(information)
        return summonerListStats

    def InsertData(data):
        if(database.AdjustmentsForSoloqueueInsertion()):
            for counter in range(5):
                database.InsertDataIntoSoloqueue((data[counter]['summonerName'], time.strftime("%d/%m/%Y") - datetime.timedelta(1), data[counter]['rank'],
                                                  data[counter]['tier'], int(data[counter]['leaguePoints'])))


@client.event
async def on_ready():
    user = await client.fetch_user("162974176544686081")
    try:
        await database.Connect()
        database.InsertNewRecords()
        await discord.DMChannel.send(user, "Database connected!")
    except:
        await discord.DMChannel.send(user, "Database didn't connect!")
        quit()

    # database.InsertNewRecords()
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    receivedMessage = message.content
    print(message.content)
    if message.author == client.user:
        return

    if receivedMessage.startswith('$insert'):
        if(verifications.VerifyMessage(receivedMessage)):
            database.InsertDataIntoSoloqueue(database.SplitMessage(
                "$insert", receivedMessage))
        else:
            await message.channel.send("Invalid parameters!")

    # update soloq row
    # if receivedMessage.startswith('$update'):
    #     if(verifications.VerifyMessage(receivedMessage)):
    #         await message.channel.send(database.UpdateData(database.SplitMessage("$update", receivedMessage)))
    #     else:
    #         await message.channel.send("Invalid parameters!")

    # parameters for update and insert

    # if (receivedMessage == '$soloq_help'):
    #     await message.channel.send("$<command> <nickname> <elo> <division> <date> <lp>")

    # select data from a certain day
    if receivedMessage.startswith('$select'):
        if(verifications.VerifyMessage(receivedMessage)):
            await message.channel.send(database.SelectData(database.SplitMessage("$select", receivedMessage)))
        else:
            await message.channel.send("Invalid parameters!")

    for word in verifications.pirloList:
        if(word.lower() in receivedMessage.lower()):
            await message.channel.send('ladrao')

    if (receivedMessage == '$last_update'):
        datenow = (datetime.datetime.now() -
                   datetime.timedelta(1)).strftime('%d/%m/%Y')

        await message.channel.send(database.SelectData([datenow]))

    # all bot commands
    if(receivedMessage == '$time'):
        await message.channel.send(datetime.datetime.now().strftime("%H:%M:%S"))

    if (receivedMessage == '$commands'):
        print(receivedMessage)
        await message.channel.send("----------Commands----------\n$select <date> - EX: $select 04/03/2021\n$today - updated records for today")


client.run(os.environ.get('DISCORD_TOKEN'))
