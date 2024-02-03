from numpy import array, max as maax, min as miin, log10, column_stack, size as siize, transpose,trim_zeros
from numpy.fft import rfft, rfftfreq

from scipy.signal import spectrogram

# from scipy.io.wavfile import read
from soundfile import read

# from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QPushButton, QMainWindow, QCheckBox, QApplication, QFileDialog,QMessageBox,QLabel,QGroupBox
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

class Mono_visualizer(QMainWindow):
    def __init__(self,parent = None):
        super(Mono_visualizer,self).__init__(parent)

        loadUi(resource_path("add\mono_window.ui"),self)

        self.ir1_box = self.findChild(QGroupBox,"ir1_box")
        self.ir1_box.setStyleSheet("QGroupBox#ir1_box { border: 2px solid #8bc34a }")
        self.ir2_box = self.findChild(QGroupBox,"ir2_box")
        self.ir2_box.setStyleSheet("QGroupBox#ir2_box { border: 2px solid #ff595e }")
        self.ir3_box = self.findChild(QGroupBox,"ir3_box")
        self.ir3_box.setStyleSheet("QGroupBox#ir3_box { border: 2px solid #ffca3a }")
        self.ir4_box = self.findChild(QGroupBox,"ir4_box")
        self.ir4_box.setStyleSheet("QGroupBox#ir4_box { border: 2px solid #c77dff }")

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

        self.temporal_plot = self.findChild(pg.PlotWidget,"temporal_plot")
        self.temporal_plot.setTitle('Waveform')
        self.temporal_plot.showGrid(x=True,y=True)
        self.temporal_plot.setLabel('bottom','Time',units='s')
        self.temporal_plot.setLabel('left','Amplitude')
        self.temporal_plot.setMouseEnabled(y=False)

        self.spectral_plot = self.findChild(pg.PlotWidget,"spectral_plot")
        self.spectral_plot.setTitle('Spectrum')
        self.spectral_plot.setLogMode(x=True)
        self.spectral_plot.showGrid(x=True,y=True)
        self.spectral_plot.setLabel('bottom','Frequency',units='Hz')
        self.spectral_plot.setLabel('left','Amplitude',units='dB')

        # curves array
        self.ircurves = [0,0,0,0]
        self.spcurves = [0,0,0,0]

    def stereo_mode(self):
        stereo_window.show()
        mono_window.close()
        return

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
        
        #* dimension check
        self.ir1, self.sr1 = read(self.fileName1)
        if self.ir1.ndim != 1:
            QMessageBox.critical(self,"Error: stereo files files only","""You selected a non-mono file. Please select a mono file, or click on the "stereo mode" button.""")
            return

        self.label1.setText(Path(self.fileName1).name)

        #* activate next buttons (if not already activated)
        if not(self.ir2_button.isEnabled()):
            self.ir2_button.setEnabled(True)
        self.ir1_check.setEnabled(True)

        #* plot data
        pen = pg.mkPen(color = '#8bc34a')
        # waveform
        self.ircurves[0] = self.temporal_plot.plot(array([i/self.sr1 for i in range(len(self.ir1))]),normalize(self.ir1),pen=pen)
        # fft computing
        h_spec = padNhamm(self.ir1)
        fft = rfft(h_spec)
        f1 = rfftfreq(len(h_spec),1/self.sr1)
        fft_toplot = smooth(20*log10(abs(fft)),max(4,len(fft)//2000))-maax(20*log10(abs(fft)))
        # cropping fft between 20Hz and 20kHz
        i = 0
        j = -1
        while f1[i] <= 20:
            i += 1
        while f1[j] >= 22000:
            j -= 1
        f1 = f1[i:j]
        fft_toplot = fft_toplot[i:j]
        self.spcurves[0] = self.spectral_plot.plot(f1,fft_toplot,pen=pen)
    
        self.play1_button.setEnabled(True)
        return    

    def loadfile2(self):
        #* clear curves
        if self.label2.text() != "Load file :":
            self.temporal_plot.removeItem(self.ircurves[1])
            self.spectral_plot.removeItem(self.spcurves[1])
        
        self.fileName2, _ = QFileDialog.getOpenFileName(self,"Select IR file", "","*wav")

        #* dimension check
        self.ir2, self.sr2  = read(self.fileName2)
        if self.ir2.ndim != 1:
            QMessageBox.critical(self,"Error: mono files only","""You selected a non-mono file. Please select a mono file, or click on the "stereo mode" button.""")
            return

        self.label2.setText(Path(self.fileName2).name)

        #* activate next button (if not already activated)
        if not(self.ir3_button.isEnabled()):
            self.ir3_button.setEnabled(True)
        self.ir2_check.setEnabled(True)

        #*  plot data
        pen = pg.mkPen(color = '#ff595e')
        # waveform
        self.ircurves[1] = self.temporal_plot.plot(array([i/self.sr2 for i in range(len(self.ir2))]),normalize(self.ir2),pen=pen)
        # fft computing
        h_spec = padNhamm(self.ir2)
        fft = rfft(h_spec)
        f1 = rfftfreq(len(h_spec),1/self.sr2)
        fft_toplot = smooth(20*log10(abs(fft)),max(4,len(fft)//2000))-maax(20*log10(abs(fft)))
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
        self.spcurves[1] = self.spectral_plot.plot(f1,fft_toplot,pen=pen)

        self.play2_button.setEnabled(True)
        return   

    def loadfile3(self):
        #* clear curves
        if self.label3.text() != "Load file :":
            self.temporal_plot.removeItem(self.ircurves[2])
            self.spectral_plot.removeItem(self.spcurves[2])

        self.fileName3, _ = QFileDialog.getOpenFileName(self,"Select IR file", "","*wav")

        #* dimension check
        self.ir3, self.sr3  = read(self.fileName3)
        if self.ir3.ndim != 1:
            QMessageBox.critical(self,"Error: mono files only","""You selected a non-mono file. Please select a mono file, or click on the "stereo mode" button.""")
            return

        self.label3.setText(Path(self.fileName3).name)

        #* activate next button (if not already activated)
        if not(self.ir4_button.isEnabled()):
            self.ir4_button.setEnabled(True)
        self.ir3_check.setEnabled(True)

        #*  plot data
        pen = pg.mkPen(color = '#ffca3a')
        # waveform
        self.ircurves[2] = self.temporal_plot.plot(array([i/self.sr3 for i in range(len(self.ir3))]),normalize(self.ir3),pen=pen)
        # fft computing
        h_spec = padNhamm(self.ir3)
        fft = rfft(h_spec)
        f1 = rfftfreq(len(h_spec),1/self.sr3)
        fft_toplot = smooth(20*log10(abs(fft)),max(4,len(fft)//2000))-maax(20*log10(abs(fft)))
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
        self.spcurves[2] = self.spectral_plot.plot(f1,fft_toplot,pen=pen)

        self.play3_button.setEnabled(True)
        return   

    def loadfile4(self):
        #* clear curves
        if self.label4.text() != "Load file :":
            self.temporal_plot.removeItem(self.ircurves[3])
            self.spectral_plot.removeItem(self.spcurves[3])

        self.fileName4, _ = QFileDialog.getOpenFileName(self,"Select IR file", "","*wav")

        #* dimension check
        self.ir4, self.sr4 = read(self.fileName4)
        if self.ir4.ndim != 1:
            QMessageBox.critical(self,"Error: mono files only","""You selected a non-mono file. Please select a mono file, or click on the "stereo mode" button.""")
            return
        
        self.label4.setText(Path(self.fileName4).name)

        self.ir4_check.setEnabled(True)

        #*  plot data
        pen = pg.mkPen(color = '#c77dff')
        # waveform
        self.ircurves[3] = self.temporal_plot.plot(array([i/self.sr4 for i in range(len(self.ir4))]),normalize(self.ir4),pen=pen)
        # fft computing
        h_spec = padNhamm(self.ir4)
        fft = rfft(h_spec)
        f1 = rfftfreq(len(h_spec),1/self.sr4)
        fft_toplot = smooth(20*log10(abs(fft)),max(4,len(fft)//2000))-maax(20*log10(abs(fft)))
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
        self.spcurves[3] = self.spectral_plot.plot(f1,fft_toplot,pen=pen)

        self.play4_button.setEnabled(True)
        return   
    
    def playIR(self,filepath):
        datapath = filepath
        QSound.play(datapath)
        return

class Stereo_visualizer(QMainWindow):
    def __init__(self,parent=None):
        super(Stereo_visualizer,self).__init__(parent)

        loadUi(resource_path("add\stereo_window.ui"),self)

        self.ir1_box = self.findChild(QGroupBox,"ir1_box")
        self.ir1_box.setStyleSheet("QGroupBox#ir1_box { border: 2px solid #8bc34a }")
        self.ir2_box = self.findChild(QGroupBox,"ir2_box")
        self.ir2_box.setStyleSheet("QGroupBox#ir2_box { border: 2px solid #ff595e }")
        self.ir3_box = self.findChild(QGroupBox,"ir3_box")
        self.ir3_box.setStyleSheet("QGroupBox#ir3_box { border: 2px solid #ffca3a }")
        self.ir4_box = self.findChild(QGroupBox,"ir4_box")
        self.ir4_box.setStyleSheet("QGroupBox#ir4_box { border: 2px solid #c77dff }")
        
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

        self.mono_button = self.findChild(QPushButton,"mono_button")
        self.mono_button.clicked.connect(lambda: self.mono_mode())

        self.temporal_plot = self.findChild(pg.PlotWidget,"temporal_plot")
        self.temporal_plot.setTitle('Waveform')
        self.temporal_plot.showGrid(x=True,y=True)
        self.temporal_plot.setLabel('bottom','Time',units='s')
        self.temporal_plot.setLabel('left','Amplitude')
        ay = self.temporal_plot.getAxis('left')
        yticks = [(0,'Right'),(2.2,'Left')]
        ay.setTicks([yticks])
        self.temporal_plot.setYRange(-1,3)
        self.temporal_plot.setMouseEnabled(y=False)

        self.spectral_plot = self.findChild(pg.PlotWidget,"spectral_plot")
        self.spectral_plot.setTitle('Spectrum')
        self.spectral_plot.setLogMode(x=True)
        self.spectral_plot.showGrid(x=True,y=True)
        self.spectral_plot.setLabel('bottom','Frequency',units='Hz')
        self.spectral_plot.setLabel('left','Amplitude',units='dB')

        self.spectro_plot1 = self.findChild(pg.PlotWidget,"spectro_plot1")
        self.spectro_plot1.setTitle('Spectrogram IR 1 (avg. of L & R ch.)')
        self.spectro_plot1.setLabel('left','Freq.',units='Hz')
        self.spectro_plot1.setLabel('bottom','Time',units='s')
        self.spectro_plot1.setYRange(20,22000)

        self.spectro_plot2 = self.findChild(pg.PlotWidget,"spectro_plot2")
        self.spectro_plot2.setTitle('Spectrogram IR 2 (avg. of L & R ch.)')
        self.spectro_plot2.setLabel('left','Freq.',units='Hz')
        self.spectro_plot2.setLabel('bottom','Time',units='s')
        self.spectro_plot2.setYRange(20,22000)

        self.spectro_plot3 = self.findChild(pg.PlotWidget,"spectro_plot3")
        self.spectro_plot3.setTitle('Spectrogram IR 3 (avg. of L & R ch.)')
        self.spectro_plot3.setLabel('left','Freq.',units='Hz')
        self.spectro_plot3.setLabel('bottom','Time',units='s')
        self.spectro_plot3.setYRange(20,22000)

        self.spectro_plot4 = self.findChild(pg.PlotWidget,"spectro_plot4")
        self.spectro_plot4.setTitle('Spectrogram IR 4 (avg. of L & R ch.)')
        self.spectro_plot4.setLabel('left','Freq.',units='Hz')
        self.spectro_plot4.setLabel('bottom','Time',units='s')
        self.spectro_plot4.setYRange(20,22000)

        self.ircurves = [[0,0],[0,0],[0,0],[0,0]]
        self.spcurves = [0,0,0,0]

    
    def mono_mode(self):
        mono_window.show()
        stereo_window.close()
    
    def playIR(self,filepath):
        datapath = filepath
        print(datapath)
        QSound.play(datapath)
        return

    def check_length(self,sr,ir):
        too_long = False
        if len(ir[:,0])/sr >= 60:
            QMessageBox.critical(self,"Error: file too long","The selected file is longer than a minute. Stereo files longer than one minute are not supported. Please select a shorter file.")
            too_long = True
        return too_long

    def plot_n_check(self):
        #* behavior for checkbxox 1
        if self.ir1_check.isEnabled():
            if self.ir1_check.isChecked():
                # plot waveform
                self.temporal_plot.addItem(self.ircurves[0][0])
                self.temporal_plot.addItem(self.ircurves[0][1])
                self.spectral_plot.addItem(self.spcurves[0])
                
            else:
                # remove curves
                self.temporal_plot.removeItem(self.ircurves[0][0])
                self.temporal_plot.removeItem(self.ircurves[0][1])
                self.spectral_plot.removeItem(self.spcurves[0])

        #* behavior for checkbxox 2
        if self.ir2_check.isEnabled():
            if self.ir2_check.isChecked():
                # plot waveform
                self.temporal_plot.addItem(self.ircurves[1][0])
                self.temporal_plot.addItem(self.ircurves[1][1])
                self.spectral_plot.addItem(self.spcurves[1])
                
            else:
                # remove curves
                self.temporal_plot.removeItem(self.ircurves[1][0])
                self.temporal_plot.removeItem(self.ircurves[1][1])
                self.spectral_plot.removeItem(self.spcurves[1])

        #* behavior for checkbxox 3
        if self.ir3_check.isEnabled():
            if self.ir3_check.isChecked():
                # plot waveform
                self.temporal_plot.addItem(self.ircurves[2][0])
                self.temporal_plot.addItem(self.ircurves[2][1])
                self.spectral_plot.addItem(self.spcurves[2])
                
            else:
                # remove curves
                self.temporal_plot.removeItem(self.ircurves[2][0])
                self.temporal_plot.removeItem(self.ircurves[2][1])
                self.spectral_plot.removeItem(self.spcurves[2])

        #* behavior for checkbxox 4
        if self.ir4_check.isEnabled():
            if self.ir4_check.isChecked():
                # plot waveform
                self.temporal_plot.addItem(self.ircurves[3][0])
                self.temporal_plot.addItem(self.ircurves[3][1])
                self.spectral_plot.addItem(self.spcurves[3])
                
            else:
                # remove curves
                self.temporal_plot.removeItem(self.ircurves[3][0])
                self.temporal_plot.removeItem(self.ircurves[3][1])
                self.spectral_plot.removeItem(self.spcurves[3])

    def clear_all(self):
        #* reset curves
        for i in range(4):
            self.temporal_plot.removeItem(self.ircurves[i][0])
            self.temporal_plot.removeItem(self.ircurves[i][1])

            self.spectral_plot.removeItem(self.spcurves[i])

            self.ircurves[i]=[0,0]
            self.spcurves[i]=0
        self.spectro_plot1.clear()
        self.spectro_plot2.clear()
        self.spectro_plot3.clear()
        self.spectro_plot4.clear()
        
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

    def loadfile1(self):
        #* clear curves
        if self.label1.text() != "Load file :":
            self.temporal_plot.removeItem(self.ircurves[0][0])
            self.temporal_plot.removeItem(self.ircurves[0][1])
            self.spectral_plot.removeItem(self.spcurves[0])

        self.fileName1, _ = QFileDialog.getOpenFileName(self,"Select IR file", "","*wav")
        self.ir1, self.sr1 = read(self.fileName1)

        if self.ir1.ndim == 1:
            QMessageBox.critical(self,"Error: stereo files only","""You selected a mono file. Please select a stereo file, or click on the "mono mode" button to visualize mono files.""")
            return
        elif self.ir1.ndim == 2:
            if self.ir1.shape[1] > 2:
                QMessageBox.critical(self,"Error: stereo files only","""Multi-channel files are not supported. Please select a stereo file, or click on the "mono mode" button to visualize mono files.""")
                return

        too_long = self.check_length(self.sr1,self.ir1)
        if too_long:
            return
        
        self.label1.setText(Path(self.fileName1).name)

        #* activate next buttons (if not already activated)
        if not(self.ir2_button.isEnabled()):
            self.ir2_button.setEnabled(True)
        self.ir1_check.setEnabled(True)

        #* plot data
        pen = pg.mkPen(color = '#8bc34a')
        # waveform
        time = array([i/self.sr1 for i in range(len(self.ir1))])
        self.ircurves[0][0] = self.temporal_plot.plot(time,normalize(self.ir1)[:,1],pen=pen)
        self.ircurves[0][1] = self.temporal_plot.plot(time,normalize(self.ir1)[:,0]+2.2,pen=pen)
        # fft computing
        ir_avg = (self.ir1[:,0] + self.ir1[:,1]) / 2
        h_spec = padNhamm(ir_avg)
        fft = rfft(h_spec)
        f1 = rfftfreq(len(h_spec),1/self.sr1)
        fft_toplot = smooth(20*log10(abs(fft)),max(4,len(f1)//800))-maax(20*log10(abs(fft)))
        # keeping info between 20Hz and 20kHz
        i = 0
        j = -1
        while f1[i] <= 20:
            i += 1
        while f1[j] >= 22000:
            j -= 1
        f1 = f1[i:j]
        fft_toplot = fft_toplot[i:j]

        self.spcurves[0] = self.spectral_plot.plot(f1,fft_toplot,pen=pen)
        # spectrogram
        self.spectro(self.sr1,self.ir1,self.spectro_plot1)
        
        self.play1_button.setEnabled(True)
        return   
    
    def loadfile2(self):
        #* clear curves
        if self.label2.text() != "Load file :":
            self.temporal_plot.removeItem(self.ircurves[1][0])
            self.temporal_plot.removeItem(self.ircurves[1][1])
            self.spectral_plot.removeItem(self.spcurves[1])

        self.fileName2, _ = QFileDialog.getOpenFileName(self,"Select IR file", "","*wav")
        self.ir2, self.sr2 = read(self.fileName2)
        

        if self.ir2.ndim == 1:
            QMessageBox.critical(self,"Error: stereo files only","""You selected a mono file. Please select a stereo file, or click on the "mono mode" button to visualize mono files.""")
            return
        elif self.ir2.ndim == 2:
            if self.ir2.shape[1] > 2:
                QMessageBox.critical(self,"Error: stereo files only","""Multi-channel files are not supported. Please select a stereo file, or click on the "mono mode" button to visualize mono files.""")
                return

        too_long = self.check_length(self.sr2,self.ir2)
        if too_long:
            return
        
        self.label2.setText(Path(self.fileName2).name)

        #* activate next buttons (if not already activated)
        if not(self.ir3_button.isEnabled()):
            self.ir3_button.setEnabled(True)
        self.ir2_check.setEnabled(True)

        #* plot data
        pen = pg.mkPen(color = '#ff595e')
        # waveform
        time = array([i/self.sr2 for i in range(len(self.ir2))])
        self.ircurves[1][0] = self.temporal_plot.plot(time,normalize(self.ir2)[:,1],pen=pen)
        self.ircurves[1][1] = self.temporal_plot.plot(time,normalize(self.ir2)[:,0]+2.2,pen=pen)
        # fft computing
        ir_avg = (self.ir2[:,0] + self.ir2[:,1]) / 2
        h_spec = padNhamm(ir_avg)
        fft = rfft(h_spec)
        f1 = rfftfreq(len(h_spec),1/self.sr2)
        fft_toplot = smooth(20*log10(abs(fft)),max(4,len(f1)//350))-maax(20*log10(abs(fft)))
        # keeping info between 20Hz and 20kHz
        i = 0
        j = -1
        while f1[i] <= 20:
            i += 1
        while f1[j] >= 22000:
            j -= 1
        f1 = f1[i:j]
        fft_toplot = fft_toplot[i:j]

        self.spcurves[1] = self.spectral_plot.plot(f1,fft_toplot,pen=pen)
        # spectrogram
        self.spectro(self.sr2,self.ir2,self.spectro_plot2)
        
        self.play2_button.setEnabled(True)
        return
    
    def loadfile3(self):
        #* clear curves
        if self.label3.text() != "Load file :":
            self.temporal_plot.removeItem(self.ircurves[2][0])
            self.temporal_plot.removeItem(self.ircurves[2][1])
            self.spectral_plot.removeItem(self.spcurves[2])

        self.fileName3, _ = QFileDialog.getOpenFileName(self,"Select IR file", "","*wav")
        self.ir3, self.sr3 = read(self.fileName3)
        

        if self.ir3.ndim == 1:
            QMessageBox.critical(self,"Error: stereo files only","""You selected a mono file. Please select a stereo file, or click on the "mono mode" button to visualize mono files.""")
            return
        elif self.ir3.ndim == 2:
            if self.ir3.shape[1] > 2:
                QMessageBox.critical(self,"Error: stereo files only","""Multi-channel files are not supported. Please select a stereo file, or click on the "mono mode" button to visualize mono files.""")
                return

        too_long = self.check_length(self.sr3,self.ir3)
        if too_long:
            return
        
        self.label3.setText(Path(self.fileName3).name)

        #* activate next buttons (if not already activated)
        if not(self.ir4_button.isEnabled()):
            self.ir4_button.setEnabled(True)
        self.ir3_check.setEnabled(True)

        #* plot data
        pen = pg.mkPen(color = '#ffca3a')
        # waveform
        time = array([i/self.sr3 for i in range(len(self.ir3))])
        self.ircurves[2][0] = self.temporal_plot.plot(time,normalize(self.ir3)[:,1],pen=pen)
        self.ircurves[2][1] = self.temporal_plot.plot(time,normalize(self.ir3)[:,0]+2.2,pen=pen)
        # fft computing
        ir_avg = (self.ir3[:,0] + self.ir3[:,1]) / 2
        h_spec = padNhamm(ir_avg)
        fft = rfft(h_spec)
        f1 = rfftfreq(len(h_spec),1/self.sr3)
        fft_toplot = smooth(20*log10(abs(fft)),max(4,len(f1)//800))-maax(20*log10(abs(fft)))
        # keeping info between 20Hz and 20kHz
        i = 0
        j = -1
        while f1[i] <= 20:
            i += 1
        while f1[j] >= 22000:
            j -= 1
        f1 = f1[i:j]
        fft_toplot = fft_toplot[i:j]

        self.spcurves[2] = self.spectral_plot.plot(f1,fft_toplot,pen=pen)
        # spectrogram
        self.spectro(self.sr3,self.ir3,self.spectro_plot3)
        
        self.play3_button.setEnabled(True)
        return
    
    def loadfile4(self):
        #* clear curves
        if self.label4.text() != "Load file :":
            self.temporal_plot.removeItem(self.ircurves[3][0])
            self.temporal_plot.removeItem(self.ircurves[3][1])
            self.spectral_plot.removeItem(self.spcurves[3])

        self.fileName4, _ = QFileDialog.getOpenFileName(self,"Select IR file", "","*wav")
        self.ir4, self.sr4 = read(self.fileName4)
        

        if self.ir4.ndim == 1:
            QMessageBox.critical(self,"Error: stereo files only","""You selected a mono file. Please select a stereo file, or click on the "mono mode" button to visualize mono files.""")
            return
        elif self.ir4.ndim == 2:
            if self.ir4.shape[1] > 2:
                QMessageBox.critical(self,"Error: stereo files only","""Multi-channel files are not supported. Please select a stereo file, or click on the "mono mode" button to visualize mono files.""")
                return
            
        too_long = self.check_length(self.sr4,self.ir4)
        if too_long:
            return

        self.label4.setText(Path(self.fileName4).name)

        self.ir4_check.setEnabled(True)

        #* plot data
        pen = pg.mkPen(color = '#c77dff')
        # waveform
        time = array([i/self.sr4 for i in range(len(self.ir4))])
        self.ircurves[3][0] = self.temporal_plot.plot(time,normalize(self.ir4)[:,1],pen=pen)
        self.ircurves[3][1] = self.temporal_plot.plot(time,normalize(self.ir4)[:,0]+2.2,pen=pen)
        # fft computing
        ir_avg = (self.ir4[:,0] + self.ir4[:,1]) / 2
        h_spec = padNhamm(ir_avg)
        fft = rfft(h_spec)
        f1 = rfftfreq(len(h_spec),1/self.sr4)
        fft_toplot = smooth(20*log10(abs(fft)),max(4,len(f1)//800))-maax(20*log10(abs(fft)))
        # keeping info between 20Hz and 20kHz
        i = 0
        j = -1
        while f1[i] <= 20:
            i += 1
        while f1[j] >= 22000:
            j -= 1
        f1 = f1[i:j]
        fft_toplot = fft_toplot[i:j]

        self.spcurves[3] = self.spectral_plot.plot(f1,fft_toplot,pen=pen)
        # spectrogram
        self.spectro(self.sr4,self.ir4,self.spectro_plot4)
        
        self.play4_button.setEnabled(True)
        return

    def spectro(self,sr,ir,plotitem):
        plotitem.clear()
        # ir_avg = (ir[:,0] + ir[:,1]) / 2
        i=-1
        j=0
        while ir[i,0]==0.:
            i -= 1
        # while ir[j,0]==0.:
        #     j += 1
        L=ir[j:i,0]
        R=ir[j:i,1]
        ir = column_stack((L,R))
        ir = normalize(ir)
        #* get left & right spectro
        nperseg = npow2(len(ir[:,0])//2000)
        if len(ir[:,0])<=4000:
            nperseg = 64
        f,t,Sxx = spectrogram((ir[:,0]+ir[:,1])/2,fs=int(sr),nfft=max(len(ir[:,0])//100,64),nperseg=nperseg,scaling='spectrum')
        Sxx = 20*log10(transpose(Sxx))
        
        # _,_,SxxR = spectrogram(ir[:,1],fs=int(sr),nfft=len(ir[:,1])//50,nperseg=len(ir[:,1])//400,scaling='spectrum')
        # SxxR = 20*log10(transpose(SxxR))
        #* set the images
        # left side
        imgL = pg.ImageItem()
        imgL.setImage(Sxx)
        trL = pg.Qt.QtGui.QTransform()
        trL.scale(t[-1] / siize(Sxx, axis=0), f[-1] / siize(Sxx, axis=1))  
        # trL.translate(0,len(f))
        imgL.setTransform(trL)
        # # right side
        # imgR = pg.ImageItem()
        # imgR.setImage(SxxR)
        # trR = pg.Qt.QtGui.QTransform()
        # trR.scale(t[-1] / siize(SxxR, axis=0), f[-1] / (2*siize(SxxR, axis=1)))  
        # imgR.setTransform(trR)

        # plotitem.setLimits(xMin=0, xMax=t[-1], yMin=f[0], yMax=f[-1])

        #* histograms
        # left side
        histL = pg.HistogramLUTItem()
        histL.setImageItem(imgL)
        print("max sxx = ", maax(Sxx))
        print("min sxx = ", miin(Sxx))
        # histL.setLevels(miin(Sxx), maax(Sxx))
        histL.gradient.restoreState(
        {'mode': 'rgb',
        'ticks': [(1.0, (253, 231, 36, 255)),
                (0.85, (94, 201, 97, 255)),
                (0.65, (32, 144, 140, 255)),
                (0.47, (58, 82, 139, 255)),
                (0.0, (68, 1, 84, 255))]}) 
        # # right side
        # histR = pg.HistogramLUTItem()
        # histR.setImageItem(imgR)
        # histR.setLevels(miin(SxxL), maax(SxxL))
        # histR.gradient.restoreState(
        # {'mode': 'rgb',
        # 'ticks': [(1.0, (253, 231, 36, 255)),
        #         (0.85, (94, 201, 97, 255)),
        #         (0.65, (32, 144, 140, 255)),
        #         (0.47, (58, 82, 139, 255)),
        #         (0.0, (68, 1, 84, 255))]}) 
        
        plotitem.addItem(imgL)
        # plotitem.addItem(imgR)
        plotitem.showGrid(x=True,y=True,alpha = 0.25)
        plotitem.setLimits(xMin=0, xMax=t[-1], yMin=0, yMax=22000)
        return

app = QApplication(sys.argv)
stereo_window = Stereo_visualizer()
mono_window = Mono_visualizer()
apply_stylesheet(app,theme='dark_lightgreen.xml')
mono_window.show()
app.exec_()