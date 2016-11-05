import logging
from collections import defaultdict
import json

from PyQt5.QtCore import *
from .baseagent import BaseAgent

from .qtoxkit import *


class ToxAgent(BaseAgent):
    def __init__(self, parent=None):
        super(ToxAgent, self).__init__(parent)

        self.self_user = ''
        self.peer_user = ''
        self.nick_name = ''

        self.toxkit = None  # QToxKit

        return

    def Login(self):
        qDebug('heree')
        self.initToxnet()
        return

    def Logout(self):
        return

    def RecvMessage(self):
        return

    # override
    def onRpcCall(self, argv):
        qDebug('hereeeee: {}'.format(argv).encode()[0:78])
        qDebug('hereeeee: {}'.format(argv).encode())

        func = argv[0]
        ret = None

        if func == 'friendExists':
            ret = self.toxkit.friendExists(argv[1])
        elif func == 'sendMessage':
            try:
                ret = self.toxkit.sendMessage(argv[1], argv[2])
            except Exception as ex:
                qDebug(str(ex).encode())
                qDebug(str(argv).encode())
        elif func == 'groupchatSendMessage':
            ret = self.toxkit.groupchatSendMessage(argv[1], argv[2])
        elif func == 'groupchatAdd':
            ret = self.toxkit.groupchatAdd()
        elif func == 'groupNumberPeers':
            ret = self.toxkit.groupNumberPeers(argv[1])
        elif func == 'groupchatSetTitle':
            ret = self.toxkit.groupchatSetTitle(argv[1], argv[2])
        elif func == 'groupchatGetTitle':
            ret = self.toxkit.groupchatGetTitle(argv[1])
        elif func == 'groupchatInviteFriend':
            try:
                ret = self.toxkit.groupchatInviteFriend(argv[1], argv[2])
            except Exception as ex:
                qDebug(str(ex).encode())
                qDebug(str(argv).encode())
        elif func == 'groupPeerNumberIsOurs':
            ret = self.toxkit.groupPeerNumberIsOurs(argv[1], argv[2])
        elif func == 'groupPeerName':
            ret = self.toxkit.groupPeerName(argv[1], argv[2])
        elif func == 'groupPeerPubkey':
            ret = self.toxkit.groupPeerPubkey(argv[1], argv[2])
        elif func == 'selfGetAddress':
            ret = self.toxkit.selfGetAddress()
        elif func == 'bootDht':
            ret = self.toxkit.bootDht()
        else:
            qDebug('not supported now: {}'.format(func))

        return ret

    # ##########################
    # abstract method implemention
    # @return True|False
    def sendMessage(self, msg, peer):
        try:
            self.toxkit.sendMessage(peer, msg)
        except Exception as ex:
            qDebug(str(ex))
            return False
        return True

    # @return True|False
    def sendGroupMessage(self, msg, peer):
        group_number = int(peer)
        rc = self.toxkit.groupchatSendMessage(group_number, msg)
        return rc

    # @return True|False
    def sendFileMessage(self, msg, peer):
        return

    # @return True|False
    def sendVoiceMessage(self, msg, peer):
        return

    # @return True|False
    def sendImageMessage(self, msg, peer):
        return

    def disconnectIt(self):
        return

    def isConnected(self):
        status = self.toxkit.selfGetConnectionStatus()
        return status > 0

    def isPeerConnected(self, peer):
        # qDebug(str(self.fixstatus))
        status = self.toxkit.friendGetConnectionStatus(peer)
        return status > 0

    def createChatroom(self, room_key, title):
        group_number = self.toxkit.groupchatAdd()
        rc = self.toxkit.groupchatSetTitle(group_number, title)

        # 上游需要一个字符串类型的group_number标识
        # 注意在传递回来的地方，要再转换成int
        return str(group_number)

    def groupInvite(self, group_number, peer):
        group_number = int(group_number)
        rc = self.toxkit.groupchatInviteFriend(group_number, peer)
        return rc

    def groupNumberPeers(self, group_number):
        group_number = int(group_number)
        number_peers = self.toxkit.groupNumberPeers(group_number)
        return number_peers

    # raw toxcore protocol handler
    def initToxnet(self):
        from .secfg import peer_tox_user
        self.peer_user = peer_tox_user

        loglevel = logging.DEBUG
        loglevel = logging.WARNING
        logging.basicConfig(level=loglevel, format='%(levelname)-8s %(message)s')

        self.nick_name = 'yatbot0inmuc'
        self.is_connected = False
        self.fixrooms = defaultdict(list)
        self.fixstatus = defaultdict(bool)

        qDebug('hrehhrere')
        ident = 'qq2tox'
        self.toxkit = QToxKit(ident, True)
        self.toxkit.connectChanged.connect(self.onToxnetConnectStatus, Qt.QueuedConnection)
        self.toxkit.newMessage.connect(self.onToxnetMessage, Qt.QueuedConnection)
        self.toxkit.friendConnectionStatus.connect(self.onToxnetFriendStatus, Qt.QueuedConnection)
        self.toxkit.fileChunkRequest.connect(self.onToxnetFileChunkReuqest, Qt.QueuedConnection)
        self.toxkit.fileRecvControl.connect(self.onToxnetFileRecvControl, Qt.QueuedConnection)
        self.toxkit.newGroupMessage.connect(self.onToxnetGroupMessage, Qt.QueuedConnection)
        self.toxkit.groupNamelistChanged.connect(self.onToxnetGroupNamelistChanged, Qt.QueuedConnection)
        self.toxkit.groupInvite.connect(self.onToxnetGroupInvite, Qt.QueuedConnection)
        return

    def onToxnetConnectStatus(self, status):
        qDebug(str(status))

        if status > 0:
            # self.connected.emit()
            args = {
                'evt': 'connected',
                'params': [],
            }
            self.SendMessageX(args)
            True
        else:
            # self.disconnected.emit()
            True

        friendId = self.peer_user
        fexists = self.toxkit.friendExists(friendId)
        qDebug(str(fexists))

        famsg = 'from qq2tox...'
        if not fexists:
            friend_number = self.toxkit.friendAdd(friendId, famsg)
            qDebug(str(friend_number))
        else:
            # rc = self.toxkit.friendDelete(friendId)
            # qDebug(str(rc))
            try:
                True
                # friend_number = self.toxkit.friendAddNorequest(friendId)
                # qDebug(str(friend_number))
            except Exception as ex:
                pass
            # self.toxkit.friendAddNorequest(friendId)
            pass

        args = self.makeBusMessage(None, self.funcName(), status)
        self.SendMessageX(args)
        return

    def onToxnetMessage(self, friendId, msgtype, msg):
        qDebug(friendId + ':' + str(msgtype) + '=' + str(len(msg)))

        # 汇总消息好友发送过来的消息当作命令处理
        # getqrcode
        # islogined
        # 等待，总之是wxagent支持的命令，

        args = self.makeBusMessage(None, self.funcName(), friendId, msgtype, msg)
        self.SendMessageX(args)
        # self.newMessage.emit(msg)
        return

    def onToxnetFriendStatus(self, friendId, status):
        qDebug(friendId + ':' + str(status))

        if status > 0:
            # self.peerConnected.emit(friendId)
            args = {
                'evt': 'peerConnected',
                'params': [friendId],
            }
            self.SendMessageX(args)
            True
        else:
            # self.peerDisconnected.emit(friendId)
            args = {
                'evt': 'peerDisconnected',
                'params': [friendId],
            }
            self.SendMessageX(args)
            True

        args = self.makeBusMessage(None, self.funcName(), friendId, status)
        self.SendMessageX(args)
        return

    def onToxnetFileChunkReuqest(self, friendId, file_number, position, length):
        if qrand() % 7 == 1:
            qDebug('fn=%s,pos=%s,len=%s' % (file_number, position, length))

        if position >= len(self.qrpic):
            qDebug('warning exceed file size: finished.')
            # self.toxkit.fileControl(friendId, file_number, 2)  # CANCEL
            return

        chunk = self.qrpic[position:(position + length)]
        self.toxkit.fileSendChunk(friendId, file_number, position, chunk)
        return

    def onToxnetFileRecvControl(self, friendId, file_number, control):
        qDebug('fn=%s,ctl=%s,' % (file_number, control))

        return

    def onToxnetGroupMessage(self, group_number, peer_number, message):
        # qDebug('nextline...')
        qDebug(('gn=%s,pn=%s,mlen=%s,mp=%s' %
                (group_number, peer_number, len(message), message[0:27])).encode())

        args = self.makeBusMessage('message', None, group_number, peer_number, message)
        args = self.setCtxChannel(args, group_number)
        self.SendMessageX(args)

        # TODO 实现上应该检测peer_toxid, peer_number和创建群与邀请顺序有关
        if peer_number == 0:  # it myself sent message, omit
            return

        # self.newGroupMessage.emit(str(group_number), message)
        return

    def onToxnetGroupNamelistChanged(self, group_number, peer_number, change_type):
        qDebug(str(change_type))
        chop = {0: 'add', 1: 'delete', 2: 'name'}[change_type]
        info = {0: 'why 0?', 1: 'myself %sed' % chop,
                2: 'toxpeer %sed' % chop, 3: 'who is there? wtf?'}

        args = self.makeBusMessage(None, self.funcName(), group_number, peer_number, change_type)
        self.SendMessageX(args)

        # 判断组员数
        number_peers = self.toxkit.groupNumberPeers(group_number)
        pinfo = info[number_peers] if number_peers < 3 else info[3]
        qDebug('np: %d, %s' % (number_peers, pinfo))

        # 据说要这么写更好，少用return控制流程
        if number_peers >= 2 and change_type == self.toxkit.CHAT_CHANGE_PEER_NAME:
            # 上游需要字符串类型的group标识。
            # self.peerEnterGroup.emit(str(group_number))
            pass

        if number_peers != 2: return
        if change_type != 2: return  # 好像只有CHANGE_PEER_NAME才能保证对方进入群组了。
        # change_type为0,1,2，分别表示？？？

        return

    def onToxnetGroupInvite(self, friend_number, group_type, group_pubkey):
        qDebug('{},{},{}'.format(friend_number, group_type, group_pubkey).encode())
        # TODO check friend_number role
        rc = None
        if group_type == 0:  # Tox.GROUPCHAT_TYPE_TEXT
            rc = self.toxkit.groupchatJoin(friend_number, group_type, group_pubkey)
        else:  # tox.GROUPCHAT_TYPE_AV
            rc = self.toxkit.AVGroupchatJoin(friend_number, group_type, group_pubkey)
        # qDebug(str(rc))
        args = self.makeBusMessage(None, self.funcName(), friend_number, group_type, group_pubkey)
        self.SendMessageX(args)
        return rc
