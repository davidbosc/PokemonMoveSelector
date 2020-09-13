import sys
import socket
import _thread

class ConnectionData():
    def __init__(self, username, authToken, wakeCommand = "!move"):
        self.server = 'irc.chat.twitch.tv'
        self.port = 6667
        self.nickname = username
        self.token = 'oauth:%s' % authToken
        self.channel = '#%s' % username
        self.wakeCommand = wakeCommand

def HandleWakeCommand(connectionData, msg):
    msg_index = msg.find("%s :" % connectionData.channel)
    if msg_index !=  -1 and connectionData.wakeCommand in msg:
        msg_index += len(connectionData.channel) + 2
        print(msg[msg_index:])

def TwitchChatScanner(connectionData) :
    HOST = connectionData.server
    PORT = connectionData.port
    bot = socket.socket()
    bot.connect((HOST, PORT))
    bot.send(f"PASS {connectionData.token}\n".encode('utf-8'))
    bot.send(f"NICK {connectionData.nickname}\n".encode('utf-8'))
    bot.send(f"JOIN {connectionData.channel}\n".encode('utf-8'))
    while True:
        msg = bot.recv(2048).decode('utf-8')
        HandleWakeCommand(connectionData, msg)

def StartTwitchChatScanner(username, authToken, wakeCommand = "!move") :
    data = ConnectionData(username, authToken, wakeCommand)
    try:
        _thread.start_new_thread(TwitchChatScanner, (data,))
    except:
        print("Error: unable to start thread")