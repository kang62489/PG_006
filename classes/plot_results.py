import pandas as pd
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (QMainWindow,
                               QVBoxLayout,
                               QHBoxLayout,
                               QPushButton,
                               QLineEdit,
                               QWidget,
                               QStackedLayout,
)

import matplotlib
from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg,
    NavigationToolbar2QT as NavigationToolbar
)
matplotlib.use('QtAgg')

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=6, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        
class PlotResults(QMainWindow):
    def __init__(self, set_dfs, title_left="title_1", title_right="title_2", ylim=None, xlabel = 'xlabel', ylabel='ylabel'):
        super().__init__()
        self.title_left = title_left
        self.title_right = title_right
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.ylim = ylim
        
        self.layout_main = QVBoxLayout()
        self.layout_ctrls = QHBoxLayout()
        self.layout_ctrls.setAlignment(Qt.AlignCenter)
        self.layout_stackedDisp = QStackedLayout()
        
        self.btn_left = QPushButton("<")
        self.btn_right = QPushButton(">")
        self.btn_left.setFixedSize(50, 40)
        self.btn_right.setFixedSize(50, 40)
        
        self.btn_left.clicked.connect(self.lastPage)
        self.btn_right.clicked.connect(self.nextPage)
        
        self.le_pageDisp = QLineEdit("1")
        self.le_pageDisp.setFixedSize(60, 50)
        self.le_pageDisp.setAlignment(Qt.AlignCenter)
        self.le_pageDisp.textChanged.connect(self.validateInupt)

        self.layout_ctrls.addWidget(self.btn_left)
        self.layout_ctrls.addWidget(self.le_pageDisp)
        self.layout_ctrls.addWidget(self.btn_right)
        self.layout_main.addLayout(self.layout_ctrls)
        
        self.set_dfs = set_dfs
        self.keys = list(self.set_dfs.keys())
        self.readDataFrames()
        
        if len(self.keys) == 2:
            widget_all = self.plot_all_on_one()
            self.layout_stackedDisp.addWidget(widget_all)
            self.plot_each_group()
        
        elif len(self.keys) == 4:
            self.plot_each_group()
            
        elif len(self.keys) == 3:
            self.plot_peaks()
            
        else:
            pass

        self.layout_main.addLayout(self.layout_stackedDisp)
        
        # A widget to hold everything
        w_main = QWidget()
        w_main.setLayout(self.layout_main)
        
        # Set the central widget of the Window.
        self.setCentralWidget(w_main)
    
    def lastPage(self):
        page = int(self.le_pageDisp.text())
        if page > 1:
            page -= 1
            self.le_pageDisp.setText(str(page))
            self.layout_stackedDisp.setCurrentIndex(page-1)
    
    def nextPage(self):
        page = int(self.le_pageDisp.text())
        if page < self.layout_stackedDisp.count():
            page += 1
            self.le_pageDisp.setText(str(page))
            self.layout_stackedDisp.setCurrentIndex(page-1)
            
    def enterPage(self):
        page = int(self.le_pageDisp.text())
        if page <= self.layout_stackedDisp.count() and page > 0:
            self.layout_stackedDisp.setCurrentIndex(page-1)
            
    def validateInupt(self):
        self.validator = QIntValidator(1, self.layout_stackedDisp.count())
        self.le_pageDisp.setValidator(self.validator)
        if self.le_pageDisp.hasAcceptableInput():
            self.le_pageDisp.setStyleSheet("color: black")
            self.enterPage()
            self.le_pageDisp.setValidator(None)
        else:
            self.le_pageDisp.setStyleSheet("color: red")
            self.le_pageDisp.setValidator(None)
    
    def readDataFrames(self):
        self.df_loaded = []
        for key in self.keys:
            self.df_loaded.append(self.set_dfs[key])
        
        self.df_columns =[]    
        for df in self.df_loaded:
            self.df_columns.append(df.columns.tolist())
    
    def plot_all_on_one(self):
        subWindow_1_all = MplCanvas()
        subWindow_2_all = MplCanvas()
        layout_subWindows = QHBoxLayout()
        layout_leftWindow = QVBoxLayout()
        layout_rightWindow = QVBoxLayout()
        
        for col_1, col_2 in zip(self.df_columns[0][1:], self.df_columns[1][1:]):
            self.df_loaded[0].plot(ax=subWindow_1_all.axes, x=self.df_columns[0][0], y=col_1, kind='line',
                                   ylim=self.ylim, xlabel=self.xlabel, ylabel=self.ylabel, title=self.title_left, grid=True)
            self.df_loaded[1].plot(ax=subWindow_2_all.axes, x=self.df_columns[1][0], y=col_2, kind='line',
                                   ylim=self.ylim, xlabel=self.xlabel, ylabel=self.ylabel, title=self.title_right, grid=True)
            
        toolbar_1_all = NavigationToolbar(subWindow_1_all, self)
        toolbar_2_all = NavigationToolbar(subWindow_2_all, self)
        layout_leftWindow.addWidget(toolbar_1_all)
        layout_leftWindow.addWidget(subWindow_1_all)
        layout_rightWindow.addWidget(toolbar_2_all)
        layout_rightWindow.addWidget(subWindow_2_all)
        
        layout_subWindows = QHBoxLayout()
        layout_subWindows.addLayout(layout_leftWindow)
        layout_subWindows.addLayout(layout_rightWindow)
        
        widget_all = QWidget()
        widget_all.setLayout(layout_subWindows)
        return widget_all
    
    def plot_each_group(self):
        if len(self.keys) == 2:
            for col_1, col_2 in zip(self.df_columns[0][1:], self.df_columns[1][1:]):
                layout_subWindows = QHBoxLayout()
                layout_leftWindow = QVBoxLayout()
                layout_rightWindow = QVBoxLayout()
                
                subWindow_1 = MplCanvas()
                self.df_loaded[0].plot(ax=subWindow_1.axes, x=self.df_columns[0][0], y=col_1, kind='line',
                                       ylim=self.ylim, xlabel=self.xlabel, ylabel=self.ylabel, title=self.title_left, grid=True)
                toolbar_1 = NavigationToolbar(subWindow_1, self)
                
                subWindow_2 = MplCanvas()
                self.df_loaded[1].plot(ax=subWindow_2.axes, x=self.df_columns[1][0], y=col_2, kind='line',
                                       ylim=self.ylim, xlabel=self.xlabel, ylabel=self.ylabel, title=self.title_right, grid=True)
                toolbar_2 = NavigationToolbar(subWindow_2, self)
                
                layout_leftWindow.addWidget(toolbar_1)
                layout_leftWindow.addWidget(subWindow_1)
                layout_rightWindow.addWidget(toolbar_2)
                layout_rightWindow.addWidget(subWindow_2)
                
                layout_subWindows.addLayout(layout_leftWindow)
                layout_subWindows.addLayout(layout_rightWindow)
                
                widget_holding_subWindows = QWidget()
                widget_holding_subWindows.setLayout(layout_subWindows)
                self.layout_stackedDisp.addWidget(widget_holding_subWindows)
        
        elif len(self.keys) == 4:
            for col_1, col_2 in zip(self.df_columns[0][1:], self.df_columns[1][1:]):
                layout_subWindows = QHBoxLayout()
                layout_leftWindow = QVBoxLayout()
                layout_rightWindow = QVBoxLayout()
                
                subWindow_1 = MplCanvas()
                self.df_loaded[0].plot(ax=subWindow_1.axes, x=self.df_columns[0][0], y=col_1, kind='line',
                                       ylim=self.ylim, xlabel=self.xlabel, ylabel=self.ylabel, title=self.title_left, grid=True, label=col_1)
                self.df_loaded[2].plot(ax=subWindow_1.axes, x=self.df_columns[2][0], y=col_1, kind='line',
                                       ylim=self.ylim, xlabel=self.xlabel, ylabel=self.ylabel, title=self.title_left, grid=True, label=col_1+ "(fitted)")
                toolbar_1 = NavigationToolbar(subWindow_1, self)
                
                subWindow_2 = MplCanvas()
                self.df_loaded[1].plot(ax=subWindow_2.axes, x=self.df_columns[1][0], y=col_2, kind='line',
                                       ylim=self.ylim, xlabel=self.xlabel, ylabel=self.ylabel, title=self.title_right, grid=True, label=col_2)
                self.df_loaded[3].plot(ax=subWindow_2.axes, x=self.df_columns[3][0], y=col_2, kind='line',
                                       ylim=self.ylim, xlabel=self.xlabel, ylabel=self.ylabel, title=self.title_right, grid=True, label=col_2+ "(fitted)")
                toolbar_2 = NavigationToolbar(subWindow_2, self)
                
                layout_leftWindow.addWidget(toolbar_1)
                layout_leftWindow.addWidget(subWindow_1)
                layout_rightWindow.addWidget(toolbar_2)
                layout_rightWindow.addWidget(subWindow_2)
                
                layout_subWindows.addLayout(layout_leftWindow)
                layout_subWindows.addLayout(layout_rightWindow)
                
                widget_holding_subWindows = QWidget()
                widget_holding_subWindows.setLayout(layout_subWindows)
                self.layout_stackedDisp.addWidget(widget_holding_subWindows)
        else:
            pass
    
    def plot_peaks(self):
        row = 0
        for col_1, col_2 in zip(self.df_columns[0][1:], self.df_columns[1][1:]):
                layout_subWindows = QHBoxLayout()
                layout_leftWindow = QVBoxLayout()
                layout_rightWindow = QVBoxLayout()
                peak_data = self.df_loaded[2].iloc[row:row+1, :]
                
                subWindow_1 = MplCanvas()
                self.df_loaded[0].plot(ax=subWindow_1.axes, x=self.df_columns[0][0], y=col_1, kind='line',
                                       ylim=self.ylim, xlabel=self.xlabel, ylabel=self.ylabel, title=self.title_left, grid=True)
                x_peak_1 = peak_data[self.df_columns[2][0]].values[0]
                y_peak_1 = peak_data[self.df_columns[2][1]].values[0]
                
                subWindow_1.axes.plot(x_peak_1, y_peak_1, 'rx', markersize=10)
                subWindow_1.axes.annotate(f'{y_peak_1:.2f}', xy=(x_peak_1, y_peak_1), xytext=(-10, 8),textcoords='offset points',color='r')
                subWindow_1.axes.axvspan(xmin=0, xmax=1.5, alpha=0.3, color='green', label='Searching Range')
                toolbar_1 = NavigationToolbar(subWindow_1, self)
                
                subWindow_2 = MplCanvas()
                self.df_loaded[1].plot(ax=subWindow_2.axes, x=self.df_columns[1][0], y=col_2, kind='line',
                                       ylim=self.ylim, xlabel=self.xlabel, ylabel=self.ylabel, title=self.title_right, grid=True)
                
                x_peak_2 = peak_data[self.df_columns[2][2]].values[0]
                y_peak_2 = peak_data[self.df_columns[2][3]].values[0]
        
                subWindow_2.axes.plot(x_peak_2, y_peak_2, 'rx', markersize=10)
                subWindow_2.axes.annotate(f'{y_peak_2:.2f}', xy=(x_peak_2, y_peak_2), xytext=(-10, 8), textcoords='offset points',color='r')
                subWindow_2.axes.axvspan(xmin=0, xmax=1.5, alpha=0.3, color='green', label='Searching Range')
                toolbar_2 = NavigationToolbar(subWindow_2, self)
                
                layout_leftWindow.addWidget(toolbar_1)
                layout_leftWindow.addWidget(subWindow_1)
                layout_rightWindow.addWidget(toolbar_2)
                layout_rightWindow.addWidget(subWindow_2)
                
                layout_subWindows.addLayout(layout_leftWindow)
                layout_subWindows.addLayout(layout_rightWindow)
                
                widget_holding_subWindows = QWidget()
                widget_holding_subWindows.setLayout(layout_subWindows)
                self.layout_stackedDisp.addWidget(widget_holding_subWindows)
                row += 1