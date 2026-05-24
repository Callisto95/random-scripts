# https://github.com/seb-m/pyinotify/blob/master/python2/examples/daemon.py
# https://github.com/seb-m/pyinotify/wiki/List-of-Examples
# https://github.com/seb-m/pyinotify/wiki/Tutorial
from subprocess import run
from threading import Lock, Timer

from pyinotify import EventsCodes, Notifier, NotifierError, ProcessEvent, WatchManager


class EventHandler(ProcessEvent):
    def __init__(self, hdd: str):
        super().__init__()
        
        self.hdd: str = hdd
        self.timer: Timer = Timer(256, lambda: ...)  # it doesn't matter, since its overwritten anyway
        self._lock: Lock = Lock()
        self._reset_timer()
    
    def _reset_timer(self) -> None:
        with self._lock:
            self.timer.cancel()
            self.timer: Timer = Timer(20 * 60, self.shutdown_hdd)
            self.timer.daemon = True
            self.timer.start()
    
    def process_IN_ACCESS(self, _) -> None:
        # print("accessed:", event.pathname)
        self._reset_timer()
    
    def shutdown_hdd(self) -> None:
        # print(f"function ran! {self.hdd}")
        run(["hdparm", "-Y", f"/dev/{self.hdd}"])


watchManager: WatchManager = WatchManager()
handler = EventHandler("sdb")
notifier = Notifier(watchManager, handler)

watchManager.add_watch("/YOUR/DIR/HERE", EventsCodes.FLAG_COLLECTIONS['OP_FLAGS']['IN_ACCESS'], rec=True)

try:
    notifier.loop()
except NotifierError as exc:
    print(exc)
