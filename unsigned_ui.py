# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from typing import Sequence

from PyQt5 import QtCore
from PyQt5.QtCore import QSize, QTimer
from PyQt5.QtWidgets import (QApplication, QGridLayout, QLineEdit, QMainWindow,
                             QWidget)

import time
import datetime

from utils import *

'''
  Config:
  - Normal Small Blind value
  - Normal Small Blind step
  - Normal Level Time period
  - Heads Up Small Blind value
  - Heads Up Small Blind step
  - Heads Up Level Time period
'''

class PokerTimerWindow(QMainWindow):
  def __init__(self,
               geometry : QSize = WindowGeometry.FHD.value,
               max_geometry : QSize = WindowGeometry.UHD.value,
               norm_lvl_time : list[int] = [10,0],
               norm_bb_step : int = 200,
               headsup_lvl_time : list[int] = [8,0],
               headsup_bb_step : int = 1000,
               time_step_ms : int = 10
               ):
    super().__init__()
    # POKER
    self.mode = PokerMode.NORMAL
    # Poker parameters
    self.normal_params = PokerParameters(MyTime(*norm_lvl_time),
                                         1,
                                         norm_bb_step)
    self.headsup_params = PokerParameters(MyTime(*headsup_lvl_time),
                                          1,
                                          headsup_bb_step)
    self.current_state = PokerStats(self.normal_params)
    # Time counters
    self.sec_cnt = 0
    self.time_step_ms = time_step_ms
    self.round_timer_running = False
    self.total_time = time.time()
    self.break_time = 0
    # Setup the Window
    self.setMaximumHeight(max_geometry.height())
    self.setMaximumWidth(max_geometry.width())
    self.setup_window(geometry)
    # Show
    self.show()

  def setup_window(self,
                   geometry : QSize = WindowGeometry.FHD.value):
    # QT
    self.setObjectName("MainWindow")
    self.resize(geometry)
    from pathlib import Path
    img = Path("dumb.jpg")
    self.setStyleSheet("#MainWindow { "
                       f" border-image: url({img.absolute()}) 0 0 0 0 stretch stretch;"
                       "}")
    self.gridLayout = QGridLayout(self)
    self.gridLayout.setObjectName("gridLayout")
    # QFontDataBase
    self.qfontdb = setupQFontDataBase()
    # QTWidgets
    ## Timer
    self.round_timer = QTimer(self.gridLayout)
    self.total_timer = QTimer(self.gridLayout)
    self.total_timer.start(1000) # each second update
    self.break_timer = QTimer(self.gridLayout)

    ## LineEdit
    self.bb_input_line = MyForm("BB Step",
                            font = MyFonts.Blinds,
                            value=self.current_state.big_blind)
    self.bb_input_line.line_edit.keyReleaseEvent = self.formKeyReleasedAction

    ## Labels
    self.round_timer_label = MyLabel("RoundTimer", MyFonts.Timer)
    self.break_timer_label = MyLabel("BreakTimer", MyFonts.Timer,border_color="transparent", bg_color="transparent",
                               layout_dir=QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignHCenter)
    self.total_timer_label = MyLabel("TotalTimer", MyFonts.Timer, border_color="transparent", bg_color="transparent",
                               layout_dir=QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter)
    self.level_label = MyLabel("Level", MyFonts.Blinds, border_color="transparent", bg_color="transparent",
                               layout_dir=QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter)
    self
    self.blinds_label = MyLabel("CurBlinds", MyFonts.Blinds)
    self.next_blinds_label = MyLabel("NxtBlinds", MyFonts.Blinds, border_color="transparent", bg_color="transparent",
                                     layout_dir=QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignHCenter)
    ## PushButtons

    self.pb_headsup = MyPushButton("headsup_pb", whats_this="Switched between Normal(lowBB and long) and Headsup(highBB and short) Mode of play")
    self.pb_reset = MyPushButton("reset_pb", whats_this="Resets the Level to 1 and timer to round period")
    self.lvl_timer_control = Level_Timer_Control(self)

    # Add Widgets to Layout
    # Upper section
    self.gridLayout.addWidget(self.round_timer_label , 0, 2, 4, 3)
    self.gridLayout.addWidget(self.break_timer_label , 3, 2, 1, 3)
    self.gridLayout.addWidget(self.total_timer_label , 0, 2, 1, 3)
    self.gridLayout.addWidget(self.blinds_label      , 0, 0, 3, 2)
    self.gridLayout.addWidget(self.level_label       , 0, 0, 1, 2)
    self.gridLayout.addWidget(self.next_blinds_label , 2, 0, 1, 2)
    # Lower section
    self.gridLayout.addWidget(self.lvl_timer_control , 4, 2, 1, 3)
    self.gridLayout.addWidget(self.pb_reset          , 4, 0, 1, 1)
    self.gridLayout.addWidget(self.pb_headsup        , 4, 1, 1, 1)
    self.gridLayout.addWidget(self.bb_input_line     , 3, 0, 1, 2)

    self.retranslateUi() # change labels

    # Setup the Central Widget
    widget = QWidget()
    widget.setLayout(self.gridLayout)
    self.setCentralWidget(widget)

    QtCore.QMetaObject.connectSlotsByName(self)

    # Connect widgets to actions
    self.lvl_timer_control.pb_next_lvl.clicked.connect(self.next_level_button_action)
    self.lvl_timer_control.pb_prev_level.clicked.connect(self.prev_level_button_action)
    self.lvl_timer_control.pb_start_stop.clicked.connect(self.start_stop_round_timer)
    self.pb_headsup.clicked.connect(self.mode_change_action)
    self.pb_reset.clicked.connect(self.reset_button_action)
    self.round_timer.timeout.connect(self.updateStats)
    self.total_timer.timeout.connect(self.update_total_time)
    self.break_timer.timeout.connect(self.update_break_time)

    # Initialize texts
    self.update_texts()

    # Resize Event
    self.resizeEvent = self.customResizeEvent

  # Event methods
  def customResizeEvent(self, event):
    self.updateFonts()

  # KeyReleaseEvent
  def formKeyReleasedAction(self, *args):
    def check_valid(string):
      try:
        val = int(string)
        return val, True
      except ValueError:
        return f"{string} not VALID", False
    def get_int(string):
      if ":" in string:
        return check_valid((string.split(":")[-1]))
      else:
        return check_valid(string)
    val, isInt  = get_int(self.bb_input_line.line_edit.displayText())
    self.bb_input_line.line_edit.value = val
    if isInt:
      if self.mode == PokerMode.NORMAL:
        self.normal_params.bb_step = val
      else:
        self.headsup_params.bb_step = val

    self.current_state.update_blinds()
    if val != "":
     self.bb_input_line.updateText()

    self.update_texts()

  def vanishing_comma(self,
                      sec_cnt: int,
                      on_time: int = 100,
                      position: int = 300):
    if (sec_cnt > position) and (sec_cnt < (position + on_time)):
      return " "
    return ":"

  def update_break_time(self):
    if self.break_time == 0:
      self.break_time = time.time()
    new_time = time.time()
    elapsed = round(new_time - self.break_time, 2)
    time_pprint =  str(datetime.datetime.strftime(datetime.datetime.utcfromtimestamp(elapsed),'%M:%S'))
    self.break_timer_label.setText(f"BREAK {time_pprint}")

  def update_total_time(self):
    new_time = time.time()
    elapsed = round(new_time - self.total_time, 2)
    time_pprint =  str(datetime.datetime.strftime(datetime.datetime.utcfromtimestamp(elapsed),'%H:%M:%S'))
    self.total_timer_label.setText(f"{time_pprint}")

  def update_texts(self):
    l, m, s, bb, sb, nbb, nsb = self.current_state._list()
    print_comma = self.vanishing_comma(self.sec_cnt)
    self.round_timer_label.setText(f"{m}{print_comma}{s:02d}")
    self.blinds_label.setText(f"{sb}/{bb}")
    self.next_blinds_label.setText(f"NEXT:{nsb}/{nbb}")
    self.level_label.setText(f"LEVEL {l:02d}")

  def count_time(self):
    self.sec_cnt += self.time_step_ms
    if self.sec_cnt == 1000:
      self.sec_cnt = 0
      return True
    return False

  # method called by timer
  def updateStats(self):
    if self.count_time():
      self.current_state.counter_increment()
    self.update_texts()

  def start_stop_round_timer(self):
    if self.round_timer_running:
      self.round_timer.stop()
      self.break_time = 0
      self.break_timer.start(1000)
      self.lvl_timer_control.pb_start_stop.setText("⏯️")
      self.lvl_timer_control.pb_start_stop.setStyleSheet("background-color: rgba(220,220,220,95%);"
                                                         "border: 2px solid black;"
                                                         "color: black;")
    else:
      self.round_timer.start(self.time_step_ms)
      self.break_time = 0
      self.break_timer.stop()
      self.lvl_timer_control.pb_start_stop.setText("⏯️")
      self.lvl_timer_control.pb_start_stop.setStyleSheet("background-color: rgba(40,40,40,95%);"
                                                         "border: 2px solid black;"
                                                         "color: white;")
    # time_pprint =  str(datetime.datetime.strftime(datetime.datetime.utcfromtimestamp(self.break_time),'%M:%S'))
    self.break_timer_label.setText(f"")#{time_pprint}")
    self.round_timer_running = not self.round_timer_running
    self.lvl_timer_control.pb_start_stop.repaint()


  # Actions
  def next_level_button_action(self):
    self.current_state.nxt_level()
    self.update_texts()

  def prev_level_button_action(self):
    self.current_state.prev_level()
    self.update_texts()

  def mode_change_action(self):
    if self.mode == PokerMode.NORMAL:
      self.bb_input_line.line_edit.value = self.headsup_params.bb_step
      self.pb_headsup.setStyleSheet("background-color: rgba(40,40,40,95%);"
                                    "border: 2px solid black;"
                                    "color: white;")
      self.current_state.update_config(self.headsup_params)
      self.mode = PokerMode.HEADSUP
      self.pb_headsup.setText("Headsup")
    else:
      self.bb_input_line.line_edit.value = self.normal_params.bb_step
      self.pb_headsup.setStyleSheet("background-color: rgba(220,220,220,95%);"
                                    "border: 2px solid black;"
                                    "color: black;")
      self.current_state.update_config(self.normal_params)
      self.mode = PokerMode.NORMAL
      self.pb_headsup.setText("Normal")
    self.bb_input_line.updateText()
    self.update_texts()

  def reset_button_action(self):
    self.current_state.update_config(self.normal_params)
    self.update_texts()

  def updateFonts(self, dividers : Sequence = [8,18,30]):
    # Calculate font sizes based on window width and height
    width = self.width()
    if width >= self.maximumWidth():
      width = self.maximumWidth()

    class FontReSize:
      S1 = int(width / dividers[0])
      S2 = int(width / dividers[1])
      S3 = int(width / dividers[2])
      S4 = int(width / 30)
      S5 = int(width / 75)

    def update_font(obj, font_size):
      # Update font sizes keeping other font parameters correct
      font = obj.font()
      font.setPointSize(font_size)
      obj.setFont(font)
      return obj

    self.round_timer_label = update_font(self.round_timer_label, FontReSize.S1)
    self.break_timer_label = update_font(self.break_timer_label, FontReSize.S2)
    self.total_timer_label = update_font(self.total_timer_label, FontReSize.S3)
    self.blinds_label = update_font(self.blinds_label, FontReSize.S2)
    self.level_label = update_font(self.level_label, FontReSize.S3)
    self.lvl_timer_control.updateFonts(FontReSize.S3)
    self.pb_headsup = update_font(self.pb_headsup, FontReSize.S4)
    self.pb_reset = update_font(self.pb_reset, FontReSize.S3)
    self.next_blinds_label = update_font(self.next_blinds_label, FontReSize.S4)
    self.bb_input_line.updateFonts(FontReSize.S5)

  def retranslateUi(self):
    _translate = QtCore.QCoreApplication.translate
    self.setWindowTitle(_translate("MainWindow", "PokerTimer"))
    self.round_timer_label.setText(_translate("MainWindow", "TextLabel"))
    self.blinds_label.setText(_translate("MainWindow", "TextLabel"))
    self.next_blinds_label.setText(_translate("MainWindow", "TextLabel"))
    self.level_label.setText(_translate("MainWindow", "TextLabel"))
    self.lvl_timer_control.pb_prev_level.setText(_translate("MainWindow", "◀"))
    self.lvl_timer_control.pb_next_lvl.setText(_translate("MainWindow", "▶"))
    self.pb_headsup.setText(_translate("MainWindow", "Normal"))
    self.pb_reset.setText(_translate("MainWindow", "Reset"))
    self.lvl_timer_control.pb_start_stop.setText(_translate("MainWindow", "⏯️"))
    self.total_timer_label.setText(_translate("MainWindow", "00:00:00"))
    self.bb_input_line.updateText()


if __name__ == "__main__":
  import sys
  app = QApplication(sys.argv)
  import argparse as argp
  parser = argp.ArgumentParser()
  parser.add_argument("--norm-bb-step", default=200, type=int)
  parser.add_argument("--norm-round-time", nargs='+', default=[10,0], type=list[int])
  parser.add_argument("--hu-bb-step", default=2000, type=int)
  parser.add_argument("--hu-round-time", nargs='+', default=[5,0], type=list[int])
  parser.add_argument("-g", "--geometry", default="VGA", choices=WindowGeometry._member_map_)
  args = parser.parse_args()
  geometry = getattr(WindowGeometry, args.geometry)

  ptw = PokerTimerWindow(geometry=geometry.value,
                         norm_lvl_time = args.norm_round_time,
                         norm_bb_step = args.norm_bb_step,
                         headsup_lvl_time = args.hu_round_time,
                         headsup_bb_step = args.hu_bb_step)
  sys.exit(app.exec_())
