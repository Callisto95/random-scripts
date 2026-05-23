# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'QuickBac.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLayout,
    QMainWindow, QPushButton, QRadioButton, QScrollBar,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1076, 892)
        MainWindow.setMinimumSize(QSize(1000, 0))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.image = QLabel(self.centralwidget)
        self.image.setObjectName(u"image")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.image.sizePolicy().hasHeightForWidth())
        self.image.setSizePolicy(sizePolicy)
        self.image.setMinimumSize(QSize(0, 360))
        self.image.setAcceptDrops(False)
        self.image.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.image.setScaledContents(False)
        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        self.verticalLayout.addWidget(self.image)

        self.group_offsets = QGroupBox(self.centralwidget)
        self.group_offsets.setObjectName(u"group_offsets")
        self.verticalLayout_4 = QVBoxLayout(self.group_offsets)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.offset_primary = QScrollBar(self.group_offsets)
        self.offset_primary.setObjectName(u"offset_primary")
        self.offset_primary.setToolTipDuration(-1)
        self.offset_primary.setMinimum(0)
        self.offset_primary.setMaximum(1000)
        self.offset_primary.setValue(500)
        self.offset_primary.setOrientation(Qt.Orientation.Horizontal)
        self.offset_primary.setInvertedAppearance(False)

        self.verticalLayout_4.addWidget(self.offset_primary)

        self.offset_secondary = QScrollBar(self.group_offsets)
        self.offset_secondary.setObjectName(u"offset_secondary")
        self.offset_secondary.setEnabled(False)
        self.offset_secondary.setMaximum(1000)
        self.offset_secondary.setValue(500)
        self.offset_secondary.setOrientation(Qt.Orientation.Horizontal)

        self.verticalLayout_4.addWidget(self.offset_secondary)

        self.zoom = QScrollBar(self.group_offsets)
        self.zoom.setObjectName(u"zoom")
        self.zoom.setMinimum(1)
        self.zoom.setMaximum(1000)
        self.zoom.setValue(500)
        self.zoom.setOrientation(Qt.Orientation.Horizontal)

        self.verticalLayout_4.addWidget(self.zoom)


        self.verticalLayout.addWidget(self.group_offsets)

        self.group_controls = QHBoxLayout()
        self.group_controls.setObjectName(u"group_controls")
        self.group_controls.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.group_wanted = QGroupBox(self.centralwidget)
        self.group_wanted.setObjectName(u"group_wanted")
        self.verticalLayout_2 = QVBoxLayout(self.group_wanted)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontal = QRadioButton(self.group_wanted)
        self.horizontal.setObjectName(u"horizontal")
        self.horizontal.setChecked(True)

        self.verticalLayout_2.addWidget(self.horizontal)

        self.vertical = QRadioButton(self.group_wanted)
        self.vertical.setObjectName(u"vertical")

        self.verticalLayout_2.addWidget(self.vertical)


        self.group_controls.addWidget(self.group_wanted)

        self.group_mode = QGroupBox(self.centralwidget)
        self.group_mode.setObjectName(u"group_mode")
        self.verticalLayout_3 = QVBoxLayout(self.group_mode)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.crop = QRadioButton(self.group_mode)
        self.crop.setObjectName(u"crop")
        self.crop.setChecked(True)

        self.verticalLayout_3.addWidget(self.crop)

        self.fill = QRadioButton(self.group_mode)
        self.fill.setObjectName(u"fill")

        self.verticalLayout_3.addWidget(self.fill)


        self.group_controls.addWidget(self.group_mode)

        self.group_guides = QGroupBox(self.centralwidget)
        self.group_guides.setObjectName(u"group_guides")
        self.gridLayout = QGridLayout(self.group_guides)
        self.gridLayout.setObjectName(u"gridLayout")
        self.vertical_50_percent = QCheckBox(self.group_guides)
        self.vertical_50_percent.setObjectName(u"vertical_50_percent")

        self.gridLayout.addWidget(self.vertical_50_percent, 0, 1, 1, 1)

        self.vertical_33_percent = QCheckBox(self.group_guides)
        self.vertical_33_percent.setObjectName(u"vertical_33_percent")

        self.gridLayout.addWidget(self.vertical_33_percent, 0, 0, 1, 1)

        self.horizontal_33_percent = QCheckBox(self.group_guides)
        self.horizontal_33_percent.setObjectName(u"horizontal_33_percent")

        self.gridLayout.addWidget(self.horizontal_33_percent, 1, 0, 1, 1)

        self.horizontal_50_percent = QCheckBox(self.group_guides)
        self.horizontal_50_percent.setObjectName(u"horizontal_50_percent")

        self.gridLayout.addWidget(self.horizontal_50_percent, 1, 1, 1, 1)

        self.vertical_66_percent = QCheckBox(self.group_guides)
        self.vertical_66_percent.setObjectName(u"vertical_66_percent")

        self.gridLayout.addWidget(self.vertical_66_percent, 0, 2, 1, 1)

        self.horizontal_66_percent = QCheckBox(self.group_guides)
        self.horizontal_66_percent.setObjectName(u"horizontal_66_percent")

        self.gridLayout.addWidget(self.horizontal_66_percent, 1, 2, 1, 1)


        self.group_controls.addWidget(self.group_guides)


        self.verticalLayout.addLayout(self.group_controls)

        self.group_buttons = QHBoxLayout()
        self.group_buttons.setObjectName(u"group_buttons")
        self.group_buttons.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.center = QPushButton(self.centralwidget)
        self.center.setObjectName(u"center")

        self.group_buttons.addWidget(self.center)

        self.export = QPushButton(self.centralwidget)
        self.export.setObjectName(u"export")

        self.group_buttons.addWidget(self.export)


        self.verticalLayout.addLayout(self.group_buttons)

        self.commands = QComboBox(self.centralwidget)
        self.commands.setObjectName(u"commands")

        self.verticalLayout.addWidget(self.commands)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.commands.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"QuickBac", None))
        self.image.setText(QCoreApplication.translate("MainWindow", u"IMAGE HERE", None))
        self.group_offsets.setTitle("")
#if QT_CONFIG(tooltip)
        self.offset_primary.setToolTip(QCoreApplication.translate("MainWindow", u"Primary Offset", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.offset_primary.setStatusTip("")
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.offset_primary.setWhatsThis("")
#endif // QT_CONFIG(whatsthis)
#if QT_CONFIG(tooltip)
        self.offset_secondary.setToolTip(QCoreApplication.translate("MainWindow", u"Secondary Offset", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.zoom.setToolTip(QCoreApplication.translate("MainWindow", u"Zoom", None))
#endif // QT_CONFIG(tooltip)
        self.group_wanted.setTitle(QCoreApplication.translate("MainWindow", u"Wanted", None))
        self.horizontal.setText(QCoreApplication.translate("MainWindow", u"Horizontal", None))
        self.vertical.setText(QCoreApplication.translate("MainWindow", u"Vertical", None))
        self.group_mode.setTitle(QCoreApplication.translate("MainWindow", u"Mode", None))
        self.crop.setText(QCoreApplication.translate("MainWindow", u"Crop", None))
        self.fill.setText(QCoreApplication.translate("MainWindow", u"Fill", None))
        self.group_guides.setTitle(QCoreApplication.translate("MainWindow", u"Guides", None))
        self.vertical_50_percent.setText(QCoreApplication.translate("MainWindow", u"v 50%", None))
        self.vertical_33_percent.setText(QCoreApplication.translate("MainWindow", u"v 33%", None))
        self.horizontal_33_percent.setText(QCoreApplication.translate("MainWindow", u"h 33%", None))
        self.horizontal_50_percent.setText(QCoreApplication.translate("MainWindow", u"h 50%", None))
        self.vertical_66_percent.setText(QCoreApplication.translate("MainWindow", u"v 66%", None))
        self.horizontal_66_percent.setText(QCoreApplication.translate("MainWindow", u"h 66%", None))
        self.center.setText(QCoreApplication.translate("MainWindow", u"Center", None))
        self.export.setText(QCoreApplication.translate("MainWindow", u"Export", None))
        self.commands.setCurrentText("")
        self.commands.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Run Command", None))
    # retranslateUi

