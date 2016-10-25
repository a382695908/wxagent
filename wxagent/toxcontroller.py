import json

from PyQt5.QtCore import *
from PyQt5.QtDBus import *

from .basecontroller import BaseController, Chatroom
from .wxcommon import *

from .toxrelay import ToxRelay


class ToxCallProxy(QObject):
    def __init__(self, ctrl, parent=None):
        super(ToxCallProxy, self).__init__(parent)
        self.ctrl = ctrl
        return

    def friendExists(self, friendId):
        qDebug('hehree')
        return self.ctrl.remoteCall(self.ctrl.rtab.funcName(), friendId)

    def friendAdd(self, friendId, addMsg):
        qDebug('hehree')
        return self.ctrl.remoteCall(self.ctrl.rtab.funcName(), friendId, addMsg)

    def sendMessage(self, peer, msg):
        qDebug('hehree')
        return self.ctrl.remoteCall(self.ctrl.rtab.funcName(), peer, msg)

    def groupchatSendMessage(self, group_number, msg):
        qDebug('hehree')
        return self.ctrl.remoteCall(self.ctrl.rtab.funcName(), group_number, msg)

    def selfGetConnectionStatus(self):
        qDebug('hehree')
        return self.ctrl.remoteCall(self.ctrl.rtab.funcName())

    def friendGetConnectionStatus(self, peer):
        qDebug('hehree')
        return self.ctrl.remoteCall(self.ctrl.rtab.funcName(), peer)

    def groupchatAdd(self):
        qDebug('hehree')
        return self.ctrl.remoteCall(self.ctrl.rtab.funcName())

    def groupchatSetTitle(self, group_number, title):
        qDebug('hehree')
        return self.ctrl.remoteCall(self.ctrl.rtab.funcName(), group_number, title)

    def groupchatInviteFriend(self, group_number, peer):
        qDebug('hehree')
        return self.ctrl.remoteCall(self.ctrl.rtab.funcName(), group_number, peer)

    def groupPeerNumberIsOurs(self, group_number, peer_number):
        qDebug('hereee')
        return self.ctrl.remoteCall(self.ctrl.rtab.funcName(), group_number, peer_number)

    def groupNumberPeers(self, group_number):
        qDebug('hehree')
        return self.ctrl.remoteCall(self.ctrl.rtab.funcName(), group_number)

    def groupchatGetTitle(self, group_number):
        qDebug('hehree')
        return self.ctrl.remoteCall(self.ctrl.rtab.funcName(), group_number)

    def groupPeerName(self, group_number, peer_number):
        qDebug('hereeee')
        return self.ctrl.remoteCall(self.ctrl.rtab.funcName(), group_number, peer_number)


class ToxController(BaseController):
    def __init__(self, rtab, parent=None):
        super(ToxController, self).__init__(rtab, parent)
        self.relay = ToxRelay()
        self.relay.toxkit = ToxCallProxy(self)
        self.peerRelay = self.relay
        self.initRelay()
        return

    def initSession(self):
        return

    def replyMessage(self, msgo):
        qDebug(str(msgo).encode())

        # 这是个什么分支，没有channel的情况应该是p2p消息
        if msgo.get('context') is None:
            from .secfg import peer_tox_user

            msg = msgo['params'][0]
            msg = str(msgo)
            self.relay.sendMessage(msg, peer_tox_user)
        else:
            qDebug(str(msgo['context']['channel']).encode())
            from .secfg import peer_tox_user

            msg = msgo['params'][0]
            msg = str(msgo)
            msg = msgo['context']['content'] if msgo.get('context').get('content') is not None else msg
            self.relay.sendMessage(msg, peer_tox_user)
            self.replyGroupMessage(msgo)

        return

    def replyGroupMessage(self, msgo):
        groupchat = None
        mkey = None
        title = ''

        mkey = msgo['context']['channel']
        qDebug(str(mkey).encode())
        title = "T: " + str(msgo['context']['channel'])
        title = str(msgo['context']['channel'])
        fmtcc = msgo['params'][0]
        fmtcc = str(msgo)
        fmtcc = msgo['context']['content'] if msgo.get('context').get('content') is not None else fmtcc
        if msgo['context'].get('fromuser') is not None:
            fmtcc = '({}) {}'.format(msgo['context']['fromuser'], fmtcc)
        qDebug(fmtcc.encode())

        if len(mkey) == 0:
            qDebug('maybe invalid channel, omit')
            return

        if self.rtab.unichats.existContrl(mkey, self.__class__.__name__):
            groupchat = self.rtab.unichats.get(mkey, self.__class__.__name__)
        else:
            qDebug('room not found: {}'.format(mkey).encode())
            qDebug(str(self.rtab.unichats.dumpKeys()).encode())

        if mkey in self.txchatmap:
            groupchat = self.txchatmap[mkey]
            # assert groupchat is not None
        else:
            qDebug('room not found: {}'.format(mkey).encode())
            qDebug(str(self.txchatmap.keys()).encode())

        if groupchat is not None:
            # assert groupchat is not None
            # 有可能groupchat已经就绪，但对方还没有接收请求，这时发送失败，消息会丢失
            number_peers = self.peerRelay.groupNumberPeers(groupchat.group_number)
            if number_peers < 2:
                groupchat.unsend_queue.append(fmtcc)
                # reinvite peer into group
                self.peerRelay.groupInvite(groupchat.group_number, self.peerRelay.peer_user)
            else:
                self.peerRelay.sendGroupMessage(fmtcc, groupchat.group_number)
        else:
            groupchat = self.createChatroom(msgo, mkey, title)
            groupchat.unsend_queue.append(fmtcc)
            qDebug('groupchat not exists, create it:' + mkey)

        return

    def createChatroom(self, msgo, mkey, title):

        group_number = ('WXU.%s' % mkey).lower()
        group_number = self.peerRelay.createChatroom(mkey, title)
        groupchat = Chatroom()
        groupchat.group_number = group_number
        # groupchat.FromUser = msg.FromUser
        # groupchat.ToUser = msg.ToUser
        # groupchat.FromUserName = msg.FromUserName
        groupchat.msgo = msgo
        self.txchatmap[mkey] = groupchat
        self.relaychatmap[group_number] = groupchat
        groupchat.title = title
        self.rtab.unichats.add(mkey, self.__class__.__name__, groupchat)

        self.peerRelay.groupInvite(group_number, self.peerRelay.peer_user)

        return groupchat

    def fillChatroom(self, msgo, mkey=None, title=None, group_number=None):
        mkey = str(msgo['context']['channel'])
        qDebug(str(mkey).encode())
        title = "T: " + str(msgo['context']['channel'])
        title = str(msgo['context']['channel'])
        group_number = msgo['params'][0]

        # group_number = ('WXU.%s' % mkey).lower()
        # group_number = self.peerRelay.createChatroom(mkey, title)
        groupchat = Chatroom()
        groupchat.group_number = group_number
        # groupchat.FromUser = msg.FromUser
        # groupchat.ToUser = msg.ToUser
        # groupchat.FromUserName = msg.FromUserName
        groupchat.msgo = msgo
        self.txchatmap[mkey] = groupchat
        self.relaychatmap[group_number] = groupchat
        groupchat.title = title
        self.rtab.unichats.add(mkey, self.__class__.__name__, groupchat)
        self.rtab.unichats.addNumber(group_number, self.__class__.__name__, groupchat)

        # self.peerRelay.groupInvite(group_number, self.peerRelay.peer_user)

        return groupchat

    def updateSession(self, msgo):
        qDebug('heree')
        evt = msgo['evt']
        params = msgo['params']
        if evt == 'onToxnetConnectStatus': self.relay.onToxnetConnectStatus(*params)
        elif evt == 'onToxnetFriendStatus': self.relay.onToxnetFriendStatus(*params)
        elif evt == 'onToxnetGroupMessage': self.relay.onToxnetGroupMessage(*params)
        elif evt == 'onToxnetGroupNamelistChanged': self.relay.onToxnetGroupNamelistChanged(*params)
        elif evt == 'onToxnetMessage': self.relay.onToxnetMessage(*params)
        else: pass
        return

    def fillContext(self, msgo):
        msgtxt = str(msgo)
        qDebug(msgtxt.encode())
        qDebug(str(self.txchatmap.keys()).encode())
        qDebug(str(self.relaychatmap.keys()).encode())

        group_number = msgo['params'][0]
        group_number_str = str(group_number)
        title1 = self.relay.groupchatGetTitle(group_number)
        if self.relaychatmap.get(group_number_str) is None:
            title2 = None
        else:
            title2 = self.relaychatmap[group_number_str].title

        qDebug((str(title1) + ',' + str(title2)).encode())

        peer_name = self.relay.groupPeerName(group_number, msgo['params'][1])
        msgo['context'] = {
            'channel': title1,
            'content': msgo['params'][len(msgo['params'])-1],
            'fromuser': peer_name,
        }

        return msgo

    # 防止消息的递归无限传播
    def filterMessage(self, msgo):
        channel = msgo['context']['channel']
        group_number = msgo['params'][0]
        peer_number = msgo['params'][1]
        qDebug('gn={},pn={}'.format(group_number, peer_number))
        rc = self.relay.groupPeerNumberIsOurs(group_number, peer_number)
        stopfwds = ['#archlinux-cn', '#archlinux-cn123']
        for fwd in stopfwds:
            if fwd == channel:
                rc = rc or True
                qDebug("stoped fwd: {}".format(fwd))
        return rc
