import functools, time, qtawesome
from PyQt5.QtWidgets import (
    QPushButton,
    QDialog,
    QVBoxLayout,
    QHeaderView,
    QFileDialog,
    QLineEdit,
    QFormLayout,
)
import functools, threading
from traceback import print_exc
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QTableView,
    QAbstractItemView,
    QLabel,
    QVBoxLayout,
    QSpacerItem,
    QTabWidget,
)
import windows
from PyQt5.QtCore import QPoint, QRect, QSize, Qt, pyqtSignal
import os, hashlib
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QApplication,
    QLayout,
    QSizePolicy,
    QWidget,
    QMenu,
    QAction,
    QTabBar,
)
from PyQt5.QtGui import (
    QCloseEvent,
    QIntValidator,
    QPaintEvent,
    QResizeEvent,
    QPixmap,
    QPainter,
    QPen,
    QColor,
)
from PyQt5.QtCore import Qt
from gui.usefulwidget import (
    getsimplecombobox,
    getspinbox,
    getcolorbutton,
    getsimpleswitch,
    getspinbox,
    selectcolor,
)
from PyQt5.QtCore import QPoint, QRect, QSize, Qt, pyqtSignal
import os
from myutils.hwnd import showintab
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtCore import Qt, QSize
from myutils.config import savehook_new_list, savehook_new_data
from myutils.hwnd import getExeIcon
import gobject
from myutils.config import _TR, _TRL, globalconfig, static_data
import winsharedutils
from myutils.wrapper import Singleton_close, Singleton, threader
from myutils.utils import checkifnewgame, vidchangedtask
from myutils.proxy import getproxy
from gui.usefulwidget import yuitsu_switch, saveposwindow, getboxlayout
from myutils.vndb import parsehtmlmethod
from gui.inputdialog import noundictconfigdialog1


class ItemWidget(QWidget):
    focuschanged = pyqtSignal(bool, str)
    doubleclicked = pyqtSignal(str)

    def focusInEvent(self, ev) -> None:
        self.bottommask.setStyleSheet(
            "QLabel { background-color: "
            + globalconfig["dialog_savegame_layout"]["onselectcolor"]
            + "; }"
        )
        self.focuschanged.emit(True, self.exe)

    def focusOutEvent(self, event):
        self.bottommask.setStyleSheet(
            "QLabel { background-color: rgba(255,255,255, 0); }"
        )
        self.focuschanged.emit(False, self.exe)

    def mouseDoubleClickEvent(self, e):
        self.doubleclicked.emit(self.exe)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.bottommask.resize(a0.size())
        self.maskshowfileexists.resize(a0.size())

    def settitle(self, text):
        self._lb.setText(text)

    def setimg(self, pixmap):
        self._img.setimg(pixmap)

    def connectexepath(self, exe):
        self.exe = exe
        self.latershowfileexits(exe)

    @threader
    def latershowfileexits(self, exe):
        if os.path.exists(exe):
            self.maskshowfileexists.setStyleSheet(
                "QLabel { background-color: rgba(255,255,255, 0); }"
            )
        else:
            self.maskshowfileexists.setStyleSheet(
                "QLabel { background-color: "
                + globalconfig["dialog_savegame_layout"]["onfilenoexistscolor"]
                + "; }"
            )

    def __init__(self, pixmap, file) -> None:
        super().__init__()
        self.itemw = globalconfig["dialog_savegame_layout"]["itemw"]
        self.itemh = globalconfig["dialog_savegame_layout"]["itemh"]
        # self.imgw = globalconfig["dialog_savegame_layout"]["imgw"]
        # self.imgh = globalconfig["dialog_savegame_layout"]["imgh"]
        # margin = (
        #     self.itemw - self.imgw
        # ) // 2  # globalconfig['dialog_savegame_layout']['margin']
        margin = globalconfig["dialog_savegame_layout"]["margin"]
        textH = globalconfig["dialog_savegame_layout"]["textH"]
        self.imgw = self.itemw - 2 * margin
        self.imgh = self.itemh - textH - 2 * margin
        #
        self.setFixedSize(QSize(self.itemw, self.itemh))
        self.setFocusPolicy(Qt.StrongFocus)
        self.maskshowfileexists = QLabel(self)
        self.bottommask = QLabel(self)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self._img = IMGWidget(self.imgw, self.imgh, pixmap)
        _w = QWidget()
        _w.setStyleSheet("background-color: rgba(255,255,255, 0);")
        wrap = QVBoxLayout()
        _w.setLayout(wrap)
        _w.setFixedHeight(self.imgh + 2 * margin)
        wrap.setContentsMargins(margin, margin, margin, margin)
        wrap.addWidget(self._img)
        layout.addWidget(_w)

        self._lb = QLabel(file)
        self._lb.setWordWrap(True)
        self._lb.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._lb)
        self.setLayout(layout)


class IMGWidget(QLabel):

    def adaptsize(self, size: QSize):

        if globalconfig["imagewrapmode"] == 0:
            h, w = size.height(), size.width()
            r = float(w) / h
            max_r = float(self.width()) / self.height()
            if r < max_r:
                new_w = self.width()
                new_h = int(new_w / r)
            else:
                new_h = self.height()
                new_w = int(new_h * r)
            return QSize(new_w, new_h)
        elif globalconfig["imagewrapmode"] == 1:
            h, w = size.height(), size.width()
            r = float(w) / h
            max_r = float(self.width()) / self.height()
            if r > max_r:
                new_w = self.width()
                new_h = int(new_w / r)
            else:
                new_h = self.height()
                new_w = int(new_h * r)
            return QSize(new_w, new_h)
        elif globalconfig["imagewrapmode"] == 2:
            return self.size()
        elif globalconfig["imagewrapmode"] == 3:
            return size

    @threader
    def setimg(self, pixmap):
        if type(pixmap) != QPixmap:
            pixmap = pixmap()

        self.pix = pixmap

        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawPixmap(self.getrect(), self.pix)
        painter.end()

        self.setPixmap(pixmap)
        self.setFixedSize(pixmap.size())

    def getrect(self):
        size = self.adaptsize(self.pix.size())
        rect = QRect()
        rect.setX(int((self.width() - size.width()) / 2))
        rect.setY(int((self.height() - size.height()) / 2))
        rect.setSize(size)
        return rect

    def __init__(self, w, h, pixmap) -> None:
        super().__init__()
        self.setFixedSize(QSize(w, h))
        self.setScaledContents(True)
        self.setimg(pixmap)


class ScrollFlow(QWidget):
    def resizeEvent(self, a0) -> None:
        self.qscrollarea.resize(self.size())
        return super().resizeEvent(a0)

    def __init__(self):
        super(ScrollFlow, self).__init__()

        self.listWidget = QtWidgets.QListWidget(self)
        # self.listWidget.setFixedWidth(600)

        self.l = FlowLayout()

        self.listWidget.setLayout(self.l)

        self.qscrollarea = QtWidgets.QScrollArea(self)
        self.qscrollarea.setWidgetResizable(True)
        self.qscrollarea.setWidget(self.listWidget)

    def addwidget(self, wid):
        self.l.addWidget(wid)

    def removeidx(self, index):
        _ = self.l.takeAt(index)
        _.widget().hide()


class FlowLayout(QLayout):
    heightChanged = pyqtSignal(int)

    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)

        self._item_list = []

    def __del__(self):
        while self.count():
            self.takeAt(0)

    def addItem(self, item):  # pylint: disable=invalid-name
        self._item_list.append(item)

    def addSpacing(self, size):  # pylint: disable=invalid-name
        self.addItem(QSpacerItem(size, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))

    def count(self):
        return len(self._item_list)

    def itemAt(self, index):  # pylint: disable=invalid-name
        if 0 <= index < len(self._item_list):
            return self._item_list[index]
        return None

    def takeAt(self, index):  # pylint: disable=invalid-name
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)
        return None

    def expandingDirections(self):  # pylint: disable=invalid-name,no-self-use
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):  # pylint: disable=invalid-name,no-self-use
        return True

    def heightForWidth(self, width):  # pylint: disable=invalid-name
        height = self._do_layout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):  # pylint: disable=invalid-name
        super().setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):  # pylint: disable=invalid-name
        return self.minimumSize()

    def minimumSize(self):  # pylint: disable=invalid-name
        size = QSize()

        for item in self._item_list:
            minsize = item.minimumSize()
            extent = item.geometry().bottomRight()
            size = size.expandedTo(QSize(minsize.width(), extent.y()))

        margin = self.contentsMargins().left()
        size += QSize(2 * margin, 2 * margin)
        return size

    def _do_layout(self, rect, test_only=False):
        m = self.contentsMargins()
        effective_rect = rect.adjusted(+m.left(), +m.top(), -m.right(), -m.bottom())
        x = effective_rect.x()
        y = effective_rect.y()
        line_height = 0

        for item in self._item_list:
            wid = item.widget()

            space_x = self.spacing()
            space_y = self.spacing()
            if wid is not None:
                space_x += wid.style().layoutSpacing(
                    QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal
                )
                space_y += wid.style().layoutSpacing(
                    QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical
                )

            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > effective_rect.right() and line_height > 0:
                x = effective_rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        new_height = y + line_height - rect.y()
        self.heightChanged.emit(new_height)
        return new_height


def opendir(k):
    try:
        os.startfile(os.path.dirname(k))
    except:
        pass


class CustomTabBar(QTabBar):
    lastclick = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):
        index = self.tabAt(event.pos())
        if index == self.count() - 1 and event.button() == Qt.LeftButton:
            self.lastclick.emit()
        else:
            super().mousePressEvent(event)


@Singleton
class browserdialog(QDialog):

    def parsehtml(self, exepath):
        try:
            newpath = parsehtmlmethod(savehook_new_data[exepath]["infopath"])
        except:
            print_exc()
            newpath = savehook_new_data[exepath]["infopath"]
        if newpath[:4].lower() != "http":
            newpath = os.path.abspath(newpath)
        return newpath

    def resizeEvent(self, a0: QResizeEvent) -> None:
        if self._resizable == False:
            return
        self.nettab.resize(a0.size().width(), self.nettab.height())
        rate = QApplication.instance().devicePixelRatio()
        rect = (
            0,
            int(rate * self.nettab.height()),
            int(rate * a0.size().width()),
            int(rate * (a0.size().height() - self.nettab.height())),
        )
        if self.webviewv == 0:
            self.browser.resize(*rect)
        elif self.webviewv == 1:
            self.browser.set_geo(*rect)

    def __init__(self, parent, textsource_or_exepath) -> None:
        super().__init__(parent, Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        if isinstance(textsource_or_exepath, str):
            self.exepath = textsource_or_exepath
        else:
            try:
                self.exepath = textsource_or_exepath.pname
            except:
                self.exepath = "0"
        self._resizable = False
        self.resize(1300, 801)
        self.webviewv = globalconfig["usewebview"]
        if self.webviewv == 0:
            self.browser = winsharedutils.HTMLBrowser(int(self.winId()))
        elif self.webviewv == 1:
            from webview import Webview

            self.browser = Webview(
                0, int(self.winId())
            )  # 构造函数里会触发ResizeEvent。虽然确实有问题，但很奇怪前一天晚上正常，第二天起来就崩溃了。
        self.setWindowTitle(savehook_new_data[self.exepath]["title"])
        self.nettab = QTabWidget(self)
        self.nettab.setFixedHeight(self.nettab.tabBar().height())
        tabBar = CustomTabBar(self)
        self.nettab.setTabBar(tabBar)
        tabBar.lastclick.connect(self.lastclicked)
        # self.nettab.setSizePolicy( QSizePolicy.Preferred,QSizePolicy.Fixed)
        self.hasvndb = bool(
            savehook_new_data[self.exepath]["infopath"]
            and os.path.exists(savehook_new_data[self.exepath]["infopath"])
        )
        if self.hasvndb:
            self.nettab.addTab(QWidget(), "vndb")
        for lnk in savehook_new_data[self.exepath]["relationlinks"]:
            self.nettab.addTab(QWidget(), lnk[0])
        self.nettab.addTab(QWidget(), "+")
        self.nettab.currentChanged.connect(self.changetab)
        self.nettab.setContextMenuPolicy(Qt.CustomContextMenu)
        self.nettab.customContextMenuRequested.connect(self.showmenu)
        if self.hasvndb + len(savehook_new_data[self.exepath]["relationlinks"]):
            self.changetab(0)
        # vbox.addWidget(self.nettab)
        # vbox.addWidget(qww)
        self._resizable = True
        self.resize(1300, 800)

        self.show()

    def showmenu(self, p):
        tab_index = self.nettab.tabBar().tabAt(p)
        if (self.hasvndb and tab_index == 0) or tab_index == self.nettab.count() - 1:
            return
        menu = QMenu(self)
        shanchu = QAction(_TR("删除"))
        cache = QAction(_TR("缓存"))
        menu.addAction(cache)
        menu.addAction(shanchu)
        action = menu.exec(self.mapToGlobal(p))
        if action == shanchu:
            self.nettab.setCurrentIndex(0)
            self.nettab.removeTab(tab_index)
            savehook_new_data[self.exepath]["relationlinks"].pop(
                tab_index - self.hasvndb
            )
        elif action == cache:

            def cachehtml(exepath, idx):
                url = savehook_new_data[exepath]["relationlinks"][idx][1]
                import requests

                headers = {
                    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "accept-language": "zh-CN,zh;q=0.9,ar;q=0.8,sq;q=0.7",
                    "cache-control": "no-cache",
                    "pragma": "no-cache",
                    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Windows"',
                    "sec-fetch-dest": "document",
                    "sec-fetch-mode": "navigate",
                    "sec-fetch-site": "same-origin",
                    "sec-fetch-user": "?1",
                    "upgrade-insecure-requests": "1",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                }

                response = requests.get(url, headers=headers, proxies=getproxy())
                os.makedirs("./cache/cachehtml", exist_ok=True)
                fn = (
                    "./cache/cachehtml/"
                    + hashlib.md5(url.encode("utf8")).hexdigest()
                    + ".html"
                )
                with open(fn, "w", encoding="utf8") as ff:
                    ff.write(
                        response.text.replace(
                            "<HEAD>", '<HEAD><base href="{}">'.format(url)
                        ).replace("<head>", '<head><base href="{}">'.format(url))
                    )
                for i in range(len(savehook_new_data[exepath]["relationlinks"])):
                    if url == savehook_new_data[exepath]["relationlinks"][i][1]:
                        if len(savehook_new_data[exepath]["relationlinks"][i]) == 3:
                            savehook_new_data[exepath]["relationlinks"][i][2] = fn
                        else:
                            savehook_new_data[exepath]["relationlinks"][i].append(fn)

            threading.Thread(
                target=cachehtml, args=(self.exepath, tab_index - self.hasvndb)
            ).start()

    def lastclicked(self):
        def callback(texts):
            if len(texts[0].strip()) and len(texts[1].strip()):
                savehook_new_data[self.exepath]["relationlinks"].append(texts)
                self.nettab.insertTab(self.nettab.count() - 1, QWidget(), texts[0])

        gobject.baseobject.Prompt.call.emit(
            _TR("添加关联页面"),
            _TR("页面类型_页面链接"),
            [["vndb/2df/..."], "about:blank"],
            [callback],
        )

    def changetab(self, idx):
        if self.hasvndb and idx == 0:
            try:
                self.browser.navigate((self.parsehtml(self.exepath)))
            except:
                self.browser.navigate("about:blank")
        else:
            lnks = savehook_new_data[self.exepath]["relationlinks"][idx - self.hasvndb]
            if len(lnks) == 3 and os.path.exists(lnks[2]):
                link = os.path.abspath(lnks[2])
            else:
                link = lnks[1]
            print(link)
            self.browser.navigate(link)


def getvndbrealtags(vndbtags_naive):
    vndbtags = []
    for tagid in vndbtags_naive:
        if tagid in globalconfig["vndbcache"]["tagid2name"]:
            vndbtags.append(globalconfig["vndbcache"]["tagid2name"][tagid])
    return vndbtags


@Singleton
class dialog_setting_game(QDialog):
    def selectexe(self):
        f = QFileDialog.getOpenFileName(directory=self.exepath)
        res = f[0]
        if res != "":

            res = res.replace("/", "\\")
            if res in savehook_new_list:
                return
            savehook_new_list[savehook_new_list.index(self.exepath)] = res
            savehook_new_data[res] = savehook_new_data[self.exepath]
            savehook_new_data.pop(self.exepath)
            _icon = getExeIcon(res, cache=True)
            if self.item:
                self.item.savetext = res
                self.table.setIndexWidget(
                    self.model.index(self.model.indexFromItem(self.item).row(), 1),
                    getcolorbutton(
                        "", "", functools.partial(opendir, res), qicon=_icon
                    ),
                )
            if self.gametitleitme:
                if savehook_new_data[res]["imagepath"] is None:
                    self.gametitleitme.setimg(getExeIcon(res, False, cache=True))
                self.gametitleitme.connectexepath(res)

            self.setWindowIcon(_icon)
            self.editpath.setText(res)
            self.exepath = res

    def __init__(self, parent, exepath, item=None, gametitleitme=None) -> None:
        super().__init__(parent, Qt.WindowCloseButtonHint)
        checkifnewgame(exepath)
        formLayout = QVBoxLayout(self)  # 配置layout

        self.item = item
        self.exepath = exepath
        self.gametitleitme = gametitleitme

        titleedit = QLineEdit(savehook_new_data[exepath]["title"])

        def _titlechange(x):
            savehook_new_data[exepath]["title"] = x
            savehook_new_data[exepath]["istitlesetted"] = True
            savehook_new_data[exepath]["searchnoresulttime"] = 0
            self.setWindowTitle(x)
            gametitleitme.settitle(x)

        titleedit.textChanged.connect(_titlechange)
        formLayout.addLayout(getboxlayout([QLabel(_TR("标题")), titleedit]))

        imgpath = QLineEdit(savehook_new_data[exepath]["imagepath"])
        imgpath.setReadOnly(True)

        def selectimg():
            f = QFileDialog.getOpenFileName(
                directory=savehook_new_data[exepath]["imagepath"]
            )
            res = f[0]
            if res != "":

                _pixmap = QPixmap(res)
                if _pixmap.isNull() == False:
                    savehook_new_data[exepath]["imagepath"] = res
                    savehook_new_data[exepath]["isimagepathusersetted"] = True
                    imgpath.setText(res)
                    gametitleitme.setimg(_pixmap)

        formLayout.addLayout(
            getboxlayout(
                [
                    QLabel(_TR("封面")),
                    imgpath,
                    getcolorbutton(
                        "", "", selectimg, icon="fa.gear", constcolor="#FF69B4"
                    ),
                ]
            )
        )

        vndbid = QLineEdit(str(savehook_new_data[exepath]["vid"]))
        vndbid.setValidator(QIntValidator())
        vndbid.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        vndbid.textEdited.connect(functools.partial(vidchangedtask, exepath))

        statiswids = [
            QLabel(_TR("统计信息")),
            getcolorbutton(
                "",
                "",
                lambda: dialog_statistic(self, exepath),
                icon="fa.bar-chart",
                constcolor="#FF69B4",
            ),
            QLabel(_TR("vndbid")),
            vndbid,
            getcolorbutton(
                "",
                "",
                lambda: browserdialog(self, exepath),
                icon="fa.book",
                constcolor="#FF69B4",
            ),
            getcolorbutton(
                "",
                "",
                lambda: vidchangedtask(exepath, savehook_new_data[exepath]["vid"]),
                icon="fa.refresh",
                constcolor="#FF69B4",
            ),
        ]
        formLayout.addLayout(getboxlayout(statiswids))
        editpath = QLineEdit(exepath)
        editpath.setReadOnly(True)
        if item:
            self.table = parent.table
            self.model = parent.model
            editpath.textEdited.connect(lambda _: item.__setitem__("savetext", _))
        self.editpath = editpath
        self.setWindowTitle(savehook_new_data[exepath]["title"])
        self.resize(QSize(600, 200))
        self.setWindowIcon(getExeIcon(exepath, cache=True))
        formLayout.addLayout(
            getboxlayout(
                [
                    QLabel(_TR("修改路径")),
                    editpath,
                    getcolorbutton(
                        "",
                        "",
                        functools.partial(self.selectexe),
                        icon="fa.gear",
                        constcolor="#FF69B4",
                    ),
                ]
            )
        )

        b = windows.GetBinaryType(exepath)

        if b == 6:
            _methods = ["", "Locale_Remulator", "Ntleas"]
        else:
            _methods = ["Locale-Emulator", "Locale_Remulator", "Ntleas"]
        if b == 6 and savehook_new_data[exepath]["localeswitcher"] == 0:
            savehook_new_data[exepath]["localeswitcher"] = 2
        formLayout.addLayout(
            getboxlayout(
                [
                    QLabel(_TR("转区启动")),
                    getsimpleswitch(savehook_new_data[exepath], "leuse"),
                    QLabel(_TR("转区方法")),
                    getsimplecombobox(
                        _TRL(_methods), savehook_new_data[exepath], "localeswitcher"
                    ),
                ][(type != 2) * 2 :]
            )
        )

        editcmd = QLineEdit(savehook_new_data[exepath]["startcmd"])
        editcmd.textEdited.connect(
            lambda _: savehook_new_data[exepath].__setitem__("startcmd", _)
        )

        formLayout.addLayout(
            getboxlayout(
                [
                    QLabel(_TR("命令行启动")),
                    getsimpleswitch(savehook_new_data[exepath], "startcmduse"),
                    editcmd,
                ]
            )
        )

        formLayout.addLayout(
            getboxlayout(
                [
                    QLabel(_TR("自动切换到模式")),
                    getsimplecombobox(
                        _TRL(["不切换", "HOOK", "剪贴板", "OCR"]),
                        savehook_new_data[exepath],
                        "onloadautochangemode2",
                    ),
                ]
            )
        )

        formLayout.addLayout(
            getboxlayout(
                [
                    QLabel(_TR("自动切换源语言")),
                    getsimplecombobox(
                        _TRL(["不切换"])
                        + _TRL(static_data["language_list_translator"]),
                        savehook_new_data[exepath],
                        "onloadautoswitchsrclang",
                    ),
                ]
            )
        )

        methodtab = QTabWidget()
        methodtab.addTab(self.gethooktab(exepath), "HOOK")
        methodtab.addTab(self.getpretranstab(exepath), _TR("预翻译"))
        methodtab.addTab(self.getttssetting(exepath), _TR("语音"))
        methodtab.addTab(self.getlabelsetting(exepath), _TR("标签"))
        formLayout.addWidget(methodtab)

        self.show()

    def getlabelsetting(self, exepath):
        _w = QWidget()
        formLayout = QVBoxLayout()
        # formLayout.setAlignment(Qt.AlignTop)
        _w.setLayout(formLayout)
        formLayout.setContentsMargins(0, 0, 0, 0)
        self.labelflow = ScrollFlow()

        def newitem(text, removeable):
            qw = tagitem(text, removeable)

            def __(_qw, t):
                _qw.remove()
                i = savehook_new_data[exepath]["usertags"].index(t)
                self.labelflow.removeidx(i)
                savehook_new_data[exepath]["usertags"].remove(t)

            if removeable:
                qw.removesignal.connect(functools.partial(__, qw))

            def _lbclick(t):
                self.parent().tagswidget.addTag(t)

            qw.labelclicked.connect(_lbclick)
            self.labelflow.addwidget(qw)

        for tag in savehook_new_data[exepath]["usertags"]:
            newitem(tag, True)
        for tag in getvndbrealtags(savehook_new_data[exepath]["vndbtags"]):
            newitem(tag, False)
        formLayout.addWidget(self.labelflow)
        _dict = {"new": 0}

        formLayout.addWidget(self.labelflow)
        button = QPushButton(_TR("添加"))

        def _add(_):
            tag = globalconfig["labelset"][_dict["new"]]
            if tag not in savehook_new_data[exepath]["usertags"]:
                savehook_new_data[exepath]["usertags"].append(tag)
                newitem(tag, True)

        button.clicked.connect(_add)

        formLayout.addLayout(
            getboxlayout(
                [
                    getsimplecombobox(globalconfig["labelset"], _dict, "new"),
                    button,
                ]
            )
        )
        return _w

    def getttssetting(self, exepath):
        _w = QWidget()
        formLayout = QVBoxLayout()
        formLayout.setAlignment(Qt.AlignTop)
        _w.setLayout(formLayout)

        edit = QLineEdit(savehook_new_data[exepath]["allow_tts_auto_names"])
        edit.textChanged.connect(
            lambda x: savehook_new_data[exepath].__setitem__("allow_tts_auto_names", x)
        )
        formLayout.addLayout(
            getboxlayout([QLabel(_TR("禁止自动朗读的人名(以|分隔多个)")), edit])
        )
        formLayout.addLayout(
            getboxlayout(
                [
                    QLabel(_TR("语音修正")),
                    getsimpleswitch(savehook_new_data[exepath], "tts_repair"),
                    getcolorbutton(
                        globalconfig,
                        "",
                        callback=lambda x: noundictconfigdialog1(
                            self,
                            savehook_new_data[exepath],
                            "tts_repair_regex",
                            "语音修正",
                            ["正则", "原文", "替换"],
                        ),
                        icon="fa.gear",
                        constcolor="#FF69B4",
                    ),
                ]
            )
        )
        return _w

    def getpretranstab(self, exepath):
        _w = QWidget()
        formLayout = QVBoxLayout()
        formLayout.setAlignment(Qt.AlignTop)
        _w.setLayout(formLayout)

        def selectimg(key, filter1, le):
            f = QFileDialog.getOpenFileName(
                directory=savehook_new_data[exepath][key], filter=filter1
            )
            res = f[0]
            if res != "":
                savehook_new_data[exepath][key] = res
                le.setText(res)

        for showname, key, filt in [
            ("json翻译文件", "gamejsonfile", "*.json"),
            ("sqlite翻译记录", "gamesqlitefile", "*.sqlite"),
            ("VNR人工翻译文件", "gamexmlfile", "*.xml"),
        ]:
            editjson = QLineEdit(exepath)
            editjson.setReadOnly(True)
            editjson.setText(savehook_new_data[exepath][key])
            formLayout.addLayout(
                getboxlayout(
                    [
                        QLabel(_TR(showname)),
                        editjson,
                        getcolorbutton(
                            "",
                            "",
                            functools.partial(selectimg, key, filt, editjson),
                            icon="fa.gear",
                            constcolor="#FF69B4",
                        ),
                    ]
                )
            )
        return _w

    def gethooktab(self, exepath):
        _w = QWidget()
        formLayout = QVBoxLayout()
        _w.setLayout(formLayout)
        formLayout.addLayout(
            getboxlayout(
                [
                    QLabel(_TR("代码页")),
                    getsimplecombobox(
                        _TRL(static_data["codepage_display"]),
                        savehook_new_data[exepath],
                        "codepage_index",
                        lambda x: gobject.baseobject.textsource.setsettings(),
                    ),
                ]
            )
        )

        formLayout.addLayout(
            getboxlayout(
                [
                    QLabel(_TR("移除非选定hook")),
                    getsimpleswitch(savehook_new_data[exepath], "removeuseless"),
                ]
            )
        )

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(
            _TRL(
                [
                    "删除",
                    "特殊码",
                ]
            )
        )  # ,'HOOK'])

        self.hcmodel = model

        table = QTableView()
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table.horizontalHeader().setStretchLastSection(True)
        # table.setEditTriggers(QAbstractItemView.NoEditTriggers);
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode((QAbstractItemView.SingleSelection))
        table.setWordWrap(False)
        table.setModel(model)
        self.hctable = table

        for row, k in enumerate(savehook_new_data[exepath]["needinserthookcode"]):  # 2
            self.newline(row, k)

        formLayout.addWidget(self.hctable)

        formLayout.addLayout(
            getboxlayout(
                [
                    QLabel(_TR("插入特殊码延迟(ms)")),
                    getspinbox(
                        0, 1000000, savehook_new_data[exepath], "inserthooktimeout"
                    ),
                ]
            )
        )
        if (
            savehook_new_data[exepath]["use_saved_text_process"]
            or "save_text_process_info" in savehook_new_data[exepath]
        ):
            formLayout.addLayout(
                getboxlayout(
                    [
                        QLabel(_TR("使用保存的文本处理流程")),
                        getsimpleswitch(
                            savehook_new_data[exepath], "use_saved_text_process"
                        ),
                    ]
                )
            )
        return _w

    def clicked2(self):
        try:
            savehook_new_data[self.exepath]["needinserthookcode"].pop(
                self.hctable.currentIndex().row()
            )
            self.hcmodel.removeRow(self.hctable.currentIndex().row())
        except:
            pass

    def newline(self, row, k):

        self.hcmodel.insertRow(row, [QStandardItem(), QStandardItem(k)])

        self.hctable.setIndexWidget(
            self.hcmodel.index(row, 0),
            getcolorbutton(
                "", "", self.clicked2, icon="fa.times", constcolor="#FF69B4"
            ),
        )


@Singleton
class dialog_syssetting(QDialog):

    def __init__(self, parent) -> None:
        super().__init__(parent, Qt.WindowCloseButtonHint)
        self.setWindowTitle(_TR("其他设置"))
        formLayout = QFormLayout(self)
        formLayout.addRow(
            QLabel(_TR("隐藏不存在的游戏")),
            getsimpleswitch(globalconfig, "hide_not_exists"),
        )
        for key, name in [
            ("itemw", "宽度"),
            ("itemh", "高度"),
            # ("imgw", "图片宽度"),
            # ("imgh", "图片高度"),
            ("margin", "边距"),
            ("textH", "文字区高度"),
        ]:
            formLayout.addRow(
                (_TR(name)),
                getspinbox(0, 1000, globalconfig["dialog_savegame_layout"], key),
            )
        for key, name in [
            ("onselectcolor", "选中时颜色"),
            ("onfilenoexistscolor", "游戏不存在时颜色"),
        ]:
            formLayout.addRow(
                (_TR(name)),
                getcolorbutton(
                    globalconfig["dialog_savegame_layout"],
                    key,
                    callback=functools.partial(
                        selectcolor,
                        self,
                        globalconfig["dialog_savegame_layout"],
                        key,
                        None,
                        self,
                        key,
                    ),
                    name=key,
                    parent=self,
                ),
            )
        formLayout.addRow(
            _TR("缩放"),
            getsimplecombobox(
                _TRL(["填充", "适应", "拉伸", "居中"]),
                globalconfig,
                "imagewrapmode",
            ),
        )
        self.show()


@Singleton
class dialog_statistic(QDialog):
    def formattime(self, t):
        t = int(t)
        s = t % 60
        t = t // 60
        m = t % 60
        t = t // 60
        h = t
        string = ""
        if h:
            string += str(h) + _TR("时")
        if m:
            string += str(m) + _TR("分")
        if s:
            string += str(s) + _TR("秒")
        if string == "":
            string = _TR("未开始")
        return string

    refreshsignal = pyqtSignal()

    def refresh(self):
        while self.isVisible():
            time.sleep(1)
            self._timelabel.setText(
                self.formattime(savehook_new_data[self.exepath]["statistic_playtime"])
            )
            self._wordlabel.setText(
                str(savehook_new_data[self.exepath]["statistic_wordcount"])
            )

    def __init__(self, parent, exepath) -> None:
        super().__init__(parent, Qt.WindowCloseButtonHint)
        checkifnewgame(exepath)
        self.exepath = exepath
        self.setWindowTitle(_TR("统计信息"))
        # self.resize(QSize(800,400))
        formlayout = QFormLayout()
        self._timelabel = QLabel(
            self.formattime(savehook_new_data[exepath]["statistic_playtime"])
        )
        formlayout.addRow(_TR("游戏时间"), self._timelabel)
        self._wordlabel = QLabel(str(savehook_new_data[exepath]["statistic_wordcount"]))
        formlayout.addRow(_TR("文字计数"), self._wordlabel)
        self.setLayout(formlayout)
        self.refreshsignal.connect(self.refresh)
        self.show()
        threading.Thread(target=self.refresh).start()


@threader
def startgame(game):
    try:
        if os.path.exists(game):
            mode = savehook_new_data[game]["onloadautochangemode2"]
            if mode > 0:
                _ = {1: "texthook", 2: "copy", 3: "ocr"}
                if globalconfig["sourcestatus2"][_[mode]]["use"] == False:
                    globalconfig["sourcestatus2"][_[mode]]["use"] = True

                    yuitsu_switch(
                        gobject.baseobject.settin_ui,
                        globalconfig["sourcestatus2"],
                        "sourceswitchs",
                        _[mode],
                        None,
                        True,
                    )
                    gobject.baseobject.starttextsource(use=_[mode], checked=True)

            dirpath = os.path.dirname(game)

            if savehook_new_data[game]["startcmduse"]:
                usearg = savehook_new_data[game]["startcmd"].format(exepath=game)
                windows.CreateProcess(
                    None,
                    usearg,
                    None,
                    None,
                    False,
                    0,
                    None,
                    dirpath,
                    windows.STARTUPINFO(),
                )
                return
            if savehook_new_data[game]["leuse"] == False or (
                game.lower()[-4:] not in [".lnk", ".exe"]
            ):
                # 对于其他文件，需要AssocQueryStringW获取命令行才能正确le，太麻烦，放弃。
                windows.ShellExecute(None, "open", game, "", dirpath, windows.SW_SHOW)
                return

            execheck3264 = game
            usearg = '"{}"'.format(game)
            if game.lower()[-4:] == ".lnk":
                exepath, args, iconpath, dirp = winsharedutils.GetLnkTargetPath(game)

                if args != "":
                    usearg = '"{}" {}'.format(exepath, args)
                elif exepath != "":
                    usearg = '"{}"'.format(exepath)

                if exepath != "":
                    execheck3264 = exepath

                if dirp != "":
                    dirpath = dirp

            localeswitcher = savehook_new_data[game]["localeswitcher"]
            b = windows.GetBinaryType(execheck3264)
            if b == 6 and localeswitcher == 0:
                localeswitcher = 1
            if localeswitcher == 2 and b == 6:
                _shareddllproxy = "shareddllproxy64"
            else:
                _shareddllproxy = "shareddllproxy32"
            shareddllproxy = os.path.abspath("./files/plugins/" + _shareddllproxy)
            _cmd = {0: "le", 1: "LR", 2: "ntleas"}[localeswitcher]
            windows.CreateProcess(
                None,
                '"{}" {} {}'.format(shareddllproxy, _cmd, usearg),
                None,
                None,
                False,
                0,
                None,
                dirpath,
                windows.STARTUPINFO(),
            )
    except:
        print_exc()


@Singleton_close
class labelsetedit(QDialog):
    def __init__(self, p) -> None:
        super().__init__(p)
        try:
            self.setWindowTitle(_TR("标签集"))
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(
                _TRL(
                    [
                        "删除",
                        "标签",
                    ]
                )
            )
            self.hcmodel = model

            table = QTableView()
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            table.horizontalHeader().setStretchLastSection(True)
            # table.setEditTriggers(QAbstractItemView.NoEditTriggers);
            table.setSelectionBehavior(QAbstractItemView.SelectRows)
            table.setSelectionMode((QAbstractItemView.SingleSelection))
            table.setWordWrap(False)
            table.setModel(model)
            self.hctable = table

            for row, k in enumerate(globalconfig["labelset"]):  # 2
                self.newline(row, k)
            formLayout = QVBoxLayout()
            formLayout.addWidget(self.hctable)
            button = QPushButton(_TR("添加行"))
            button.clicked.connect(lambda _: self.newline(0, ""))
            formLayout.addWidget(button)
            self.setLayout(formLayout)
            self.show()
        except:
            print_exc()

    def clicked2(self):
        try:
            globalconfig["labelset"].pop(self.hctable.currentIndex().row())
            self.hcmodel.removeRow(self.hctable.currentIndex().row())
        except:
            pass

    def closeEvent(self, a0: QCloseEvent) -> None:
        rows = self.hcmodel.rowCount()
        rowoffset = 0
        dedump = set()
        globalconfig["labelset"].clear()
        for row in range(rows):
            k = self.hcmodel.item(row, 1).text()
            if k == "" or k in dedump:
                rowoffset += 1
                continue
            globalconfig["labelset"].append(k)
            dedump.add(k)

    def newline(self, row, k):
        self.hcmodel.insertRow(row, [QStandardItem(), QStandardItem(k)])
        self.hctable.setIndexWidget(
            self.hcmodel.index(row, 0),
            getcolorbutton(
                "", "", self.clicked2, icon="fa.times", constcolor="#FF69B4"
            ),
        )


class ClickableLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setClickable(True)

    def setClickable(self, clickable):
        self._clickable = clickable

    def mousePressEvent(self, event):
        if self._clickable and event.button() == Qt.LeftButton:
            self.clicked.emit()

    clicked = pyqtSignal()


class tagitem(QWidget):

    removesignal = pyqtSignal(str)
    labelclicked = pyqtSignal(str)

    def remove(self):
        self.hide()
        _lay = self.layout()
        _ws = []
        for i in range(_lay.count()):
            witem = _lay.itemAt(i)
            _ws.append(witem.widget())
        for w in _ws:
            _lay.removeWidget(w)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        border_color = Qt.black
        border_width = 1
        pen = QPen(border_color)
        pen.setWidth(border_width)
        painter.setPen(pen)
        painter.drawRect(self.rect())

    def __init__(self, tag, removeable=True) -> None:
        super().__init__()
        tagLayout = QHBoxLayout()
        tagLayout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(tagLayout)

        lb = ClickableLabel(tag)
        lb.clicked.connect(lambda: self.labelclicked.emit(tag))
        tagLayout.addWidget(lb)
        if removeable:
            button = getcolorbutton(
                None,
                None,
                lambda: self.removesignal.emit(tag),  # self.removeTag(tag),
                qicon=qtawesome.icon(
                    "fa.times",
                    color="#FF69B4",
                ),
                sizefixed=True,
            )
            tagLayout.addWidget(button)


class TagWidget(QWidget):
    tagschanged = pyqtSignal(tuple)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tags = []

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel(_TR("标签")))
        self.setLayout(layout)

        self.lineEdit = QLineEdit()
        self.lineEdit.returnPressed.connect(lambda: self.addTag(self.lineEdit.text()))
        layout.addWidget(self.lineEdit)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.tag2widget = {}
        layout.addWidget(
            getcolorbutton(
                "",
                "",
                lambda _: labelsetedit(parent),
                icon="fa.gear",
                constcolor="#FF69B4",
            ),
        )

    def addTag(self, tag):
        try:

            if not tag:
                return
            if tag in self.tag2widget:
                return
            self.tags.append(tag)
            qw = tagitem(tag)
            qw.removesignal.connect(self.removeTag)

            layout = self.layout()
            # layout.insertLayout(layout.count() - 1, tagLayout)
            layout.insertWidget(layout.count() - 2, qw)
            self.tag2widget[tag] = qw
            self.lineEdit.clear()
            self.lineEdit.setFocus()
            self.tagschanged.emit(tuple(self.tag2widget.keys()))
        except:
            print_exc()

    def removeTag(self, tag):
        _w = self.tag2widget[tag]
        _w.remove()

        self.layout().removeWidget(_w)
        self.tag2widget.pop(tag)
        self.lineEdit.setFocus()
        self.tagschanged.emit(tuple(self.tag2widget.keys()))


@Singleton_close
class dialog_savedgame_new(saveposwindow):
    def startgame(self, game):
        if os.path.exists(game):
            idx = savehook_new_list.index(game)
            savehook_new_list.insert(0, savehook_new_list.pop(idx))
            self.close()
            startgame(game)

    def clicked2(self):
        try:
            game = self.currentfocuspath
            idx = savehook_new_list.index(game)
            savehook_new_list.pop(idx)
            if game in savehook_new_data:
                savehook_new_data.pop(game)
            self.flow.removeidx(self.idxsave.index(game))
            self.idxsave.pop(self.idxsave.index(game))
            self.keepocus(idx)
        except:
            pass

    def clicked4(self):
        opendir(self.currentfocuspath)

    def clicked3(self):

        f = QFileDialog.getOpenFileName(
            directory="", options=QFileDialog.DontResolveSymlinks
        )

        res = f[0]
        if res != "":
            res = res.replace("/", "\\")
            if res not in savehook_new_list:
                self.newline(res)
                self.idxsave.append(res)

    def keepocus(self, idx):
        idx = min(len(savehook_new_list) - 1, idx)
        if len(savehook_new_list):
            self.flow.l._item_list[idx].widget().setFocus()

    def top1focus(self):
        if len(savehook_new_list):
            self.flow.l._item_list[0].widget().setFocus()

    def tagschanged(self, tags):
        checkexists = _TR("存在") in tags
        if checkexists:
            _ = list(tags)
            _.remove(_TR("存在"))
            tags = tuple(_)
        self.formLayout.removeWidget(self.flow)
        self.idxsave.clear()
        self.flow = ScrollFlow()
        self.formLayout.insertWidget(self.formLayout.count() - 1, self.flow)
        for k in savehook_new_list:
            if checkexists and os.path.exists(k) == False:
                continue

            # print(vndbtags)
            notshow = False
            for tag in tags:
                if (
                    tag not in getvndbrealtags(savehook_new_data[k]["vndbtags"])
                    and tag not in savehook_new_data[k]["usertags"]
                    and tag not in savehook_new_data[k]["title"]
                    and tag != str(savehook_new_data[k]["vid"])
                ):
                    notshow = True
                    break
            if notshow:
                continue
            self.newline(k)
            self.idxsave.append(k)
            QApplication.processEvents()

    def __init__(self, parent) -> None:
        super().__init__(
            parent,
            flags=Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint,
            dic=globalconfig,
            key="savegamedialoggeo",
        )
        self.setWindowTitle(_TR("已保存游戏"))
        if globalconfig["showintab_sub"]:
            showintab(int(self.winId()), True)
        formLayout = QVBoxLayout()
        self.tagswidget = TagWidget(self)
        self.tagswidget.tagschanged.connect(self.tagschanged)
        formLayout.addWidget(self.tagswidget)
        self.flow = ScrollFlow()

        formLayout.addWidget(self.flow)
        self.formLayout = formLayout
        buttonlayout = QHBoxLayout()
        self.buttonlayout = buttonlayout
        self.savebutton = []
        self.simplebutton(
            "开始游戏", True, lambda: self.startgame(self.currentfocuspath), True
        )
        self.simplebutton("游戏设置", True, self.showsettingdialog, False)
        self.simplebutton("删除游戏", True, self.clicked2, False)
        self.simplebutton("打开目录", True, self.clicked4, True)

        self.simplebutton("添加游戏", False, self.clicked3, 1)
        self.simplebutton("其他设置", False, lambda: dialog_syssetting(self), False)
        formLayout.addLayout(buttonlayout)
        _W = QWidget()
        _W.setLayout(formLayout)
        self.setCentralWidget(_W)
        self.activategamenum = 1
        self.itemfocuschanged(False, None)
        self.show()
        self.idxsave = []
        if globalconfig["hide_not_exists"]:
            self.tagswidget.addTag(_TR("存在"))
        else:
            self.tagschanged(tuple())

    def showsettingdialog(self):
        idx = self.idxsave.index(self.currentfocuspath)

        dialog_setting_game(
            self,
            self.currentfocuspath,
            None,
            gametitleitme=self.flow.l._item_list[idx].widget(),
        )

    def simplebutton(self, text, save, callback, exists):
        button5 = QPushButton()
        button5.setText(_TR(text))
        if save:
            self.savebutton.append((button5, exists))
        button5.clicked.connect(callback)
        button5.setFocusPolicy(Qt.NoFocus)
        self.buttonlayout.addWidget(button5)
        return button5

    def itemfocuschanged(self, b, k):

        if b:
            if self.currentfocuspath == k:
                return
            self.activategamenum += 1
            self.currentfocuspath = k
        else:
            self.activategamenum -= 1
            self.currentfocuspath = None

        _able = self.activategamenum > 0

        for _btn, exists in self.savebutton:
            _able1 = _able and (
                (not exists)
                or (self.currentfocuspath)
                and (os.path.exists(self.currentfocuspath))
            )
            _btn.setEnabled(_able1)

    def newline(self, k):
        checkifnewgame(k)

        def _getpixfunction(kk):
            _pix = QPixmap(savehook_new_data[kk]["imagepath"])
            if _pix.isNull():
                _pix = getExeIcon(kk, False, cache=True)
            return _pix

        gameitem = ItemWidget(
            functools.partial(_getpixfunction, k), savehook_new_data[k]["title"]
        )
        gameitem.connectexepath(k)
        gameitem.doubleclicked.connect(self.startgame)
        gameitem.focuschanged.connect(self.itemfocuschanged)
        self.flow.addwidget(gameitem)
