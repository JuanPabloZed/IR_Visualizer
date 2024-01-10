from numpy import array, max as maax, log10
from numpy.fft import rfft, rfftfreq

# from scipy.io.wavfile import read
from soundfile import read

# from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QPushButton, QMainWindow, QCheckBox, QApplication, QFileDialog,QMessageBox,QLabel
from PyQt5.QtGui import QIcon
from PyQt5.uic import loadUi
from PyQt5.QtMultimedia import QSound
import pyqtgraph as pg
from qt_material import apply_stylesheet

from pathlib import Path

from funcs import *

import sys
from os import path

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = path.abspath(".")

    return path.join(base_path, relative_path)

class MainWindow(QMainWindow):
    def __init__(self,parent = None):
        super(MainWindow,self).__init__(parent)

        loadUi(resource_path("add\window.ui"),self)

        self.setWindowIcon(QIcon(resource_path("add\Visualizer_icon.ico")))

        self.ir1_button = self.findChild(QPushButton,"ir1_button")
        self.ir1_button.clicked.connect(lambda: self.loadfile1())
        self.label1 = self.findChild(QLabel,"label1")

        self.ir2_button = self.findChild(QPushButton,"ir2_button")
        self.ir2_button.setEnabled(False)
        self.ir2_button.clicked.connect(lambda: self.loadfile2())
        self.label2 = self.findChild(QLabel,"label2")
        
        self.ir3_button = self.findChild(QPushButton,"ir3_button")
        self.ir3_button.clicked.connect(lambda: self.loadfile3())
        self.ir3_button.setEnabled(False)
        self.label3 = self.findChild(QLabel,"label3")
        
        self.ir4_button = self.findChild(QPushButton,"ir4_button")
        self.ir4_button.clicked.connect(lambda: self.loadfile4())
        self.ir4_button.setEnabled(False)
        self.label4 = self.findChild(QLabel,"label4")

        self.play1_button = self.findChild(QPushButton,"play1_button")
        self.play1_button.setEnabled(False)
        self.play1_button.clicked.connect(lambda: self.playIR(self.fileName1))

        self.play2_button = self.findChild(QPushButton,"play2_button")
        self.play2_button.setEnabled(False)
        self.play2_button.clicked.connect(lambda: self.playIR(self.fileName2))

        self.play3_button = self.findChild(QPushButton,"play3_button")
        self.play3_button.setEnabled(False)
        self.play3_button.clicked.connect(lambda: self.playIR(self.fileName3))

        self.play4_button = self.findChild(QPushButton,"play4_button")
        self.play4_button.setEnabled(False)
        self.play4_button.clicked.connect(lambda: self.playIR(self.fileName4))

        self.ir1_check = self.findChild(QCheckBox,"ir1_check")
        self.ir1_check.clicked.connect(lambda: self.plot_n_check())

        self.ir2_check = self.findChild(QCheckBox,"ir2_check")
        self.ir2_check.clicked.connect(lambda: self.plot_n_check())

        self.ir3_check = self.findChild(QCheckBox,"ir3_check")
        self.ir3_check.clicked.connect(lambda: self.plot_n_check())

        self.ir4_check = self.findChild(QCheckBox,"ir4_check")
        self.ir4_check.clicked.connect(lambda: self.plot_n_check())

        self.clear_button = self.findChild(QPushButton,"clear_button")
        self.clear_button.clicked.connect(lambda: self.clear_all())

        self.stereo_button = self.findChild(QPushButton, "stereo_button")
        self.stereo_button.clicked.connect(lambda: self.stereo_mode())
        self.stereo_button.setEnabled(False)
        self.stereo_button.setText("Stereo mode (coming soon)")

        self.temporal_plot = self.findChild(pg.PlotWidget,"temporal_plot")
        self.temporal_plot.setTitle('Waveform')
        self.temporal_plot.showGrid(x=True,y=True)
        self.temporal_plot.setLabel('bottom','Time',units='s')
        self.temporal_plot.setLabel('left','Amplitude')

        self.spectral_plot = self.findChild(pg.PlotWidget,"spectral_plot")
        self.spectral_plot.setTitle('Spectrum')
        self.spectral_plot.setLogMode(x=True)
        self.spectral_plot.showGrid(x=True,y=True)
        self.spectral_plot.setLabel('bottom','Frequency',units='Hz')
        self.spectral_plot.setLabel('left','Amplitude',units='dB')

        # curves array
        self.ircurves = [0,0,0,0]
        self.spcurves = [0,0,0,0]

    def clear_all(self):
        #* reset curves
        for i in range(4):
            self.temporal_plot.removeItem(self.ircurves[i])
            self.spectral_plot.removeItem(self.spcurves[i])

            self.ircurves[i]=0
            self.spcurves[i]=0
        
        #* reset buttons
        # section 1
        self.label1.setText("Load file :")

        self.ir1_check.setEnabled(False)
        self.ir1_check.setChecked(True)

        self.play1_button.setEnabled(False)

        # section 2
        self.label2.setText("Load file :")

        self.ir2_button.setEnabled(False)

        self.ir2_check.setEnabled(False)
        self.ir2_check.setChecked(True)

        self.play2_button.setEnabled(False)

        # section 3
        self.label3.setText("Load file :")

        self.ir3_button.setEnabled(False)

        self.ir3_check.setEnabled(False)
        self.ir3_check.setChecked(True)

        self.play3_button.setEnabled(False)

        # section 4
        self.label4.setText("Load file :")

        self.ir4_button.setEnabled(False)

        self.ir4_check.setEnabled(False)
        self.ir4_check.setChecked(True)

        self.play4_button.setEnabled(False)

        return

    def plot_n_check(self):
        #* behavior for checkbxox 1
        if self.ir1_check.isEnabled():
            if self.ir1_check.isChecked():
                # plot waveform
                self.temporal_plot.addItem(self.ircurves[0])
                self.spectral_plot.addItem(self.spcurves[0])
                
            else:
                # remove curves
                self.temporal_plot.removeItem(self.ircurves[0])
                self.spectral_plot.removeItem(self.spcurves[0])

        #* behavior for checkbxox 2
        if self.ir2_check.isEnabled():
            if self.ir2_check.isChecked():
                # plot waveform
                self.temporal_plot.addItem(self.ircurves[1])
                self.spectral_plot.addItem(self.spcurves[1])
                
            else:
                # remove curves
                self.temporal_plot.removeItem(self.ircurves[1])
                self.spectral_plot.removeItem(self.spcurves[1])

        #* behavior for checkbxox 3
        if self.ir3_check.isEnabled():
            if self.ir3_check.isChecked():
                # plot waveform
                self.temporal_plot.addItem(self.ircurves[2])
                self.spectral_plot.addItem(self.spcurves[2])
                
            else:
                # remove curves
                self.temporal_plot.removeItem(self.ircurves[2])
                self.spectral_plot.removeItem(self.spcurves[2])

        #* behavior for checkbxox 4
        if self.ir4_check.isEnabled():
            if self.ir4_check.isChecked():
                # plot waveform
                self.temporal_plot.addItem(self.ircurves[3])
                self.spectral_plot.addItem(self.spcurves[3])
                
            else:
                # remove curves
                self.temporal_plot.removeItem(self.ircurves[3])
                self.spectral_plot.removeItem(self.spcurves[3])

    def loadfile1(self):
        #* clear curves
        if self.label1.text() != "Load file :":
            self.temporal_plot.removeItem(self.ircurves[0])
            self.spectral_plot.removeItem(self.spcurves[0])


        self.fileName1, _ = QFileDialog.getOpenFileName(self,"Select IR file", "","*wav")
        #* mono check
        self.ir1, self.sr1 = read(self.fileName1)
        while self.ir1.ndim == 2:
                QMessageBox.critical(self,"Error","Only mono files supported.\nPlease select a mono only IR file.")
                self.fileName1,_ = QFileDialog.getOpenFileName(self,"Please choose a mono file only", "",'*.wav')
                self.ir1, self.sr1 = read(self.fileName1)
        

        self.label1.setText(Path(self.fileName1).name)

        #* activate next buttons (if not already activated)
        if not(self.ir2_button.isEnabled()):
            self.ir2_button.setEnabled(True)
        self.ir1_check.setEnabled(True)

        #*  plot data
        # waveform
        pen = pg.mkPen(color = '#8bc34a')
        self.ircurves[0] = self.temporal_plot.plot(array([i/self.sr1 for i in range(len(self.ir1))]),normalize(self.ir1),pen=pen)

        # fft computing
        h_spec = padNhamm(self.ir1)
        fft = rfft(h_spec)
        fft_toplot = smooth(20*log10(abs(fft)),45)-maax(20*log10(abs(fft)))
        f1 = rfftfreq(len(h_spec),1/self.sr1)
        # keeping info between 20Hz and 20kHz
        i = 0
        j = -1
        while f1[i] <= 20:
            i += 1
        while f1[j] >= 22000:
            j -= 1
        f1 = f1[i:j]
        fft_toplot = fft_toplot[i:j]
        # fft plotting
        pen = pg.mkPen(color = '#8bc34a')
        self.spcurves[0] = self.spectral_plot.plot(f1,fft_toplot,pen=pen)
        
        self.play1_button.setEnabled(True)
        return    

    def loadfile2(self):
        #* clear curves
        if self.label2.text() != "Load file :":
            self.temporal_plot.removeItem(self.ircurves[1])
            self.spectral_plot.removeItem(self.spcurves[1])
        
        self.fileName2, _ = QFileDialog.getOpenFileName(self,"Select IR file", "","*wav")

        #* mono check
        self.ir2, self.sr2  = read(self.fileName2)
        while self.ir2.ndim == 2:
                QMessageBox.critical(self,"Error","Only mono files supported.\nPlease select a mono only IR file.")
                self.fileName2,_ = QFileDialog.getOpenFileName(self,"Please choose a mono file only", "",'*.wav')
                self.ir2, self.sr2 = read(self.fileName2)


        self.label2.setText(Path(self.fileName2).name)

        #* activate next button (if not already activated)
        if not(self.ir3_button.isEnabled()):
            self.ir3_button.setEnabled(True)
        self.ir2_check.setEnabled(True)

        #*  plot data
        # waveform
        pen = pg.mkPen(color = '#ff595e')
        self.ircurves[1] = self.temporal_plot.plot(array([i/self.sr2 for i in range(len(self.ir2))]),normalize(self.ir2),pen=pen)

        # fft computing
        h_spec = padNhamm(self.ir2)
        fft = rfft(h_spec)
        fft_toplot = smooth(20*log10(abs(fft)),45)-maax(20*log10(abs(fft)))
        f1 = rfftfreq(len(h_spec),1/self.sr2)
        # cropping between 20Hz and 20kHz
        i = 0
        j = -1
        while f1[i] <= 20:
            i += 1
        while f1[j] >= 22000:
            j -= 1
        f1 = f1[i:j]
        fft_toplot = fft_toplot[i:j]
        # fft plotting
        pen = pg.mkPen(color = '#ff595e')
        self.spcurves[1] = self.spectral_plot.plot(f1,fft_toplot,pen=pen)

        self.play2_button.setEnabled(True)

        return   

    def loadfile3(self):
        #* clear curves
        if self.label3.text() != "Load file :":
            self.temporal_plot.removeItem(self.ircurves[2])
            self.spectral_plot.removeItem(self.spcurves[2])

        self.fileName3, _ = QFileDialog.getOpenFileName(self,"Select IR file", "","*wav")

        #* mono check
        self.ir3, self.sr3  = read(self.fileName3)
        while self.ir3.ndim == 2:
                QMessageBox.critical(self,"Error","Only mono files supported.\nPlease select a mono only IR file.")
                self.fileName3,_ = QFileDialog.getOpenFileName(self,"Please choose a mono file only", "",'*.wav')
                self.ir3, self.sr3 = read(self.fileName3)


        self.label3.setText(Path(self.fileName3).name)

        #* activate next button (if not already activated)
        if not(self.ir4_button.isEnabled()):
            self.ir4_button.setEnabled(True)
        self.ir3_check.setEnabled(True)

        #*  plot data
        # waveform
        pen = pg.mkPen(color = '#ffca3a')
        self.ircurves[2] = self.temporal_plot.plot(array([i/self.sr3 for i in range(len(self.ir3))]),normalize(self.ir3),pen=pen)

        # fft computing
        h_spec = padNhamm(self.ir3)
        fft = rfft(h_spec)
        fft_toplot = smooth(20*log10(abs(fft)),45)-maax(20*log10(abs(fft)))
        f1 = rfftfreq(len(h_spec),1/self.sr3)
        # cropping between 20Hz and 20kHz
        i = 0
        j = -1
        while f1[i] <= 20:
            i += 1
        while f1[j] >= 22000:
            j -= 1
        f1 = f1[i:j]
        fft_toplot = fft_toplot[i:j]
        # fft plotting
        pen = pg.mkPen(color = '#ffca3a')
        self.spcurves[2] = self.spectral_plot.plot(f1,fft_toplot,pen=pen)

        self.play3_button.setEnabled(True)

        return   

    def loadfile4(self):
        #* clear curves
        if self.label4.text() != "Load file :":
            self.temporal_plot.removeItem(self.ircurves[3])
            self.spectral_plot.removeItem(self.spcurves[3])

        self.fileName4, _ = QFileDialog.getOpenFileName(self,"Select IR file", "","*wav")

        #* mono check
        self.ir4, self.sr4 = read(self.fileName4)
        while self.ir4.ndim == 2:
                QMessageBox.critical(self,"Error","Only mono files supported.\nPlease select a mono only IR file.")
                self.fileName4,_ = QFileDialog.getOpenFileName(self,"Please choose a mono file only", "",'*.wav')
                self.ir4, self.sr4 = read(self.fileName4)


        self.label4.setText(Path(self.fileName4).name)

        self.ir4_check.setEnabled(True)

        #*  plot data
        # waveform
        pen = pg.mkPen(color = '#c77dff')
        self.ircurves[3] = self.temporal_plot.plot(array([i/self.sr4 for i in range(len(self.ir4))]),normalize(self.ir4),pen=pen)

        # fft computing
        h_spec = padNhamm(self.ir4)
        fft = rfft(h_spec)
        fft_toplot = smooth(20*log10(abs(fft)),45)-maax(20*log10(abs(fft)))
        f1 = rfftfreq(len(h_spec),1/self.sr4)
        # cropping between 20Hz and 20kHz
        i = 0
        j = -1
        while f1[i] <= 20:
            i += 1
        while f1[j] >= 22000:
            j -= 1
        f1 = f1[i:j]
        fft_toplot = fft_toplot[i:j]
        # fft plotting
        pen = pg.mkPen(color = '#c77dff')
        self.spcurves[3] = self.spectral_plot.plot(f1,fft_toplot,pen=pen)

        self.play4_button.setEnabled(True)
        return   
    
    def playIR(self,filepath):
        datapath = filepath
        QSound.play(datapath)
        return

app = QApplication(sys.argv)
main_window = MainWindow()
apply_stylesheet(app,theme='dark_lightgreen.xml')
main_window.show()
app.exec_()