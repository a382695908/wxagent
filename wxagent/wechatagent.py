import json

from PyQt5.QtCore import *
from PyQt5.QtDBus import *

from .baseagent import BaseAgent

from .qwechat import QWechat


class WechatAgent(BaseAgent):

    def __init__(self, parent=None):
        super(WechatAgent, self).__init__(parent)
        self.wechat = None
        return

    def Login(self):
        self.wechat = QWechat(self)
        self.wechat._agent = self
        self.wechat.Login()
        return

    # override
    def onRpcCall(self, argv):
        qDebug('hereeeee: {}'.format(argv).encode()[0:78])

        func = argv[0]
        ret = None

        if func == 'friendExists':
            ret = self.wechat.friendExists(argv[1])
        elif func == 'sendMessage':
            ret = self.wechat.sendMessage(argv[1], argv[2])
        elif func == 'getqrpic':
            ret = QByteArray(self.wechat.qrpic).toBase64().data().decode()
            qDebug(str(len(ret)))
        elif func == 'islogined':
            ret = self.wechat.logined
        elif func == 'getinitdata':
            data64 = self.wechat.wxinitRawData.toBase64()
            ret = data64.data().decode()
        elif func == 'getcontact':
            data64 = self.wechat.wxFriendRawData.toBase64()
            ret = data64.data().decode()
        elif func == 'getgroups':
            ret = json.JSONEncoder().encode(self.wechat.wxGroupUserNames)
        else:
            qDebug('not supported now: {}'.format(func).encode())

        return ret

