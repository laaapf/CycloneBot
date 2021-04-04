import os
import verifications
import discord
from dotenv import load_dotenv
import sqlite3
import asyncio
from riotwatcher import LolWatcher, ApiError
import schedule
import datetime
import time
from discord.ext import tasks, commands
import threading

client = discord.Client()
db = sqlite3.connect('database.db', check_same_thread=False)
splitMessageCommands = ["$insert", "$update"]
watcher = LolWatcher("TOKEN")
myRegion = "br1"
nameList = ['Lapf', 'Tigersaber', 'bliip', 'Jhizz', 'Vlyper']


class database:
    def SplitMessage(command, message):
        if(message[0] in splitMessageCommands):
            splittedMessage = message.split()
            splittedMessage.remove(splittedMessage[0])
            splittedMessage[2] = int(splittedMessage[2])
            splittedMessage[4] = int(splittedMessage[4])
        else:
            splittedMessage = message.split()
            splittedMessage.remove(splittedMessage[0])
        return splittedMessage

    def CloseCon(cursor, con):
        db.commit()
        cursor.close()

    def InsertData(data):
        yesterdayDate = (datetime.datetime.now() - datetime.timedelta(1)
                         ).strftime('%d/%m/%Y')
        yesterdayData = database.SelectData([yesterdayDate], 1)
        deleteTempData = """DELETE FROM TempTable"""
        yesterdayQuery = """INSERT INTO TempTable (name,elo,division,date,current_lp) VALUES (?,?,?,?,?)"""
        dbCursor = db.cursor()
        query = """INSERT INTO SoloqueueData (name,elo,division,date,current_lp) VALUES (?,?,?,?,?)"""
        try:
            dbCursor.execute(deleteTempData,)
            database.CloseCon(dbCursor, db)
            dbCursor = db.cursor()
            dbCursor.executemany(yesterdayQuery, yesterdayData)
            database.CloseCon(dbCursor, db)
            dbCursor = db.cursor()
            dbCursor.execute(query, data)
        except sqlite3.IntegrityError:
            dbCursor.close()
        db.commit()
        dbCursor.close()
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
        dbCursor = db.cursor()
        query = """SELECT * FROM SoloqueueData WHERE date = ?"""
        dbCursor.execute(query, (message[0],))
        queryResult = dbCursor.fetchall()
        resultText = f"**DATE: {message[0]}** ```autohotkey\n\n"
        if(len(identifier) == 0):
            if(len(queryResult) <= 1):
                dbCursor.close()
                return("No records found!")
            for row in queryResult:
                resultText += row[0] + " | " + row[3] + " | " + \
                    str(row[2]) + " | " + str(row[4]) + " LP \n"
            resultText += "```"
            dbCursor.close()
            return resultText
        else:
            dbCursor.close()
            return queryResult


class leagueapi:
    def getSummonerData():
        summonerListStats = []
        for nickname in nameList:
            summoner = watcher.summoner.by_name(myRegion, nickname)
            stats = watcher.league.by_summoner(myRegion, summoner['id'])
            for information in stats:
                if(information['queueType'] == 'RANKED_SOLO_5x5'):
                    summonerListStats.append(information)
        return summonerListStats

    def InsertData(data):
        for counter in range(5):
            database.InsertData([data[counter]['summonerName'], data[counter]['tier'],
                                 data[counter]['rank'], time.strftime("%d/%m/%Y"), int(data[counter]['leaguePoints'])])


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    receivedMessage = message.content
    print(message.content)
    if message.author == client.user:
        return

    if receivedMessage.startswith('$insert'):
        if(verifications.VerifyMessage(receivedMessage)):
            database.InsertData(database.SplitMessage(
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

    if (receivedMessage == '$today'):
        yesterdayDate = (datetime.datetime.now() - datetime.timedelta(2)
                         ).strftime('%d/%m/%Y')
        await message.channel.send(database.SelectData([time.strftime("%d/%m/%Y")]))

    # all bot commands
    if (receivedMessage == '$commands'):
        await message.channel.send("----------Commands----------\n$select <date> - EX: $select 04/03/2021\n$today - updated records for today")


def InsertNewRecords():
    threading.Timer(1, InsertNewRecords).start()
    now = datetime.datetime.now()
    if(now.strftime("%H:%M:%S") == "23:00:00"):
        leagueapi.InsertData(leagueapi.getSummonerData())


InsertNewRecords()


client.run("TOKEN")
