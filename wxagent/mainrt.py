import sys
import signal
import asyncio

from PyQt5.QtCore import *
from .qtutil import pyctrl
from quamash import QEventLoop, QThreadExecutor

from .wxcommon import *

from .wechatagent import WechatAgent
from .ircagent import IRCAgent
from .toxagent import ToxAgent
from .xmppagent import XmppAgent
from .roundtable import RoundTable
# from .xmppagent import XmppAgent
# from .slackagent import SlackAgent


class StartupManager(QObject):
    def __init__(self, parent=None):
        super(StartupManager, self).__init__(parent)
        self.protocols = {'wechat': WechatAgent, 'irc': IRCAgent, 'tox': ToxAgent,
                          'xmpp': XmppAgent,
                          'roundtable': RoundTable}
        self.procs = {}
        # self.loginAllProtocols()
        self.agt = None  # BaseAgent
        return

    def loginAllProtocols(self):

        agts = self.agents
        # agts.append(WXAgent())
        agts.append(IRCAgent())
        agts.append(ToxAgent())

        for agt in agts:
            agt.PushMessage.connect(self.onPushMessage, Qt.QueuedConnection)
            agt.Login()

        return

    def start(self):
        cmd = sys.argv[1] if len(sys.argv) > 1 else None
        member = sys.argv[2] if len(sys.argv) > 2 else None

        if member is not None and self.protocols.get(member) is None:
            qDebug('not supported protocol: ' + member)
            sys.exit(-1)

        if cmd == 'start':
            if member is None: self.startControl()
            else: self.startProc(member)
            pass
        elif cmd == 'stop':
            if member is None: self.startControl()
            else: self.startProc(member)
            pass
        elif cmd == 'restart':
            if member is None: qDebug('ctrl can not restart.')
            else: self.startProc(member)
            pass
        else:
            if member is None and cmd is None:
                self.startControl()
            else:
                qDebug('what are you doing: cmd={}, protocol={}'.format(cmd, member))
                sys.exit(-1)
            pass
        return

    def startControl(self):
        return

    def stopControl(self):
        return

    def startProc(self, member):
        self.agt = self.protocols[member]()
        self.agt.Login()
        return

    def stopProc(self, member):
        return

    def restartProc(self, member):
        return


# hot fix
g_w2t = None


def sigint_handler():
    qDebug('clean up...')
    app = QCoreApplication.instance()
    app.exit(0)
    # sys.exit(0)
    return


def on_app_about_close():
    qDebug('hereee')
    global g_w2t

    # g_w2t.peerRelay.disconnectIt()
    return


def main():
    if qVersion() < '5.5.0': raise 'not supported qt version < 5.5.0'
    app = QCoreApplication(sys.argv)
    pyctrl()
    loop = QEventLoop(app)
    loop.add_signal_handler(signal.SIGINT, sigint_handler)
    asyncio.set_event_loop(loop)

    rto = StartupManager()
    rto.start()

    global g_w2t
    g_w2t = rto
    app.aboutToQuit.connect(on_app_about_close)

    qDebug('qt&loop...{}'.format(rto))
    with loop: loop.run_forever()  # sys.exit(app.exec_())
    return


if __name__ == '__main__': main()
