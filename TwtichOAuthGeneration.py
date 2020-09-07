import sys
from PyQt5 import QtWidgets,QtGui,QtCore
from PyQt5.QtWebEngineWidgets import *

class TokenStorage():
    def __init__(self):
        self.value = ""
    
def RenderAuthorizeUI():
    access_token = TokenStorage()

    def getAccessTokenFromUrl(url, window):
        if url.hasFragment(): 
            fragments = url.fragment().split('&')
            for queryStringVariable in fragments:
                if "access_token" in queryStringVariable:
                    tokenStartingIndex = queryStringVariable.index("=") + 1
                    access_token.value = queryStringVariable[tokenStartingIndex:]
                    window.close()

    app = QtWidgets.QApplication(sys.argv)
    window = QWebEngineView()
    window.setWindowTitle("Pokemon Move Selector: Authorize")
    window.load(QtCore.QUrl('https://id.twitch.tv/oauth2/authorize?response_type=token&client_id=v66bfhh102a1y1860k4ilhyhi7ulms&redirect_uri=http://localhost:8080&scope=chat:read&force_verify=true'))
    window.showMaximized()
    window.urlChanged.connect(lambda x: getAccessTokenFromUrl(x, window))
    app.exec_()

    return access_token.value