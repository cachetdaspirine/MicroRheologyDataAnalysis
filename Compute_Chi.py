import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector


import ipywidgets as widgets
from IPython.display import display


fitting_function= lambda  t,F0,phi,freq,cst : F0*np.cos(2*np.pi*freq*t+phi)+cst

class setup:
    def __init__(self,stiffnesses,xi,amplitude,phase,frequency,data_frame,column_names):
        # here we change the numbering of the two traps, to match the article numbering
        # first extract all the parameters
        self.k1x = stiffnesses['xSignal1']
        self.k1y = stiffnesses['ySignal1']
        self.k2x = stiffnesses['xSignal2']
        self.k2y = stiffnesses['ySignal2']
        self.amplitude = amplitude
        self.phase = phase
        self.freq = frequency
        self.xi = xi
        #self.fit1 = lambda F0,phi,cst,t : fitting_function(F0,phi,self.freq,cst,t)
        #self.fit2 = lambda F0,phi,cst,t : fitting_function(F0,phi,self.freq,cst,t)
        # from this we can deduce the position of the trap.
        self.Xoft = lambda t : np.cos(t * 2*np.pi * self.freq + self.phase) * self.amplitude
        # This is the force graphs
        self. data = data_frame
        self.column_names=column_names
        # we can fit the force difference with the fitting_function
        self.popt_1,self.popt_2 = None,None
        self.xlim=None
        self.ylim=None
        self.make_fit()
    def make_fit(self):
        #self.get_frequencies()
        self.popt_1,pconv_1 = curve_fit(fitting_function,
                                                                    self.data[self.column_names[2]],
                                                                    self.data[self.column_names[0]],
                                                                    p0 = (np.sqrt(np.mean(self.data[self.column_names[0]].head(50)**2)),0.,self.freq,0))
        self.popt_2,pconv_2 = curve_fit(fitting_function,
                                                                    self.data[self.column_names[2]],
                                                                    self.data[self.column_names[1]] 
                                                                    ,p0 = (np.sqrt(np.mean(self.data[self.column_names[1]].head(50)**2)),0.,self.freq,0))
    def show_fit(self):
        fig,ax = plt.subplots()
        self.plot(fig,ax,Force2=False)
        plt.show()
        fig,ax = plt.subplots()
        self.plot(fig,ax,Force1=False)
        plt.show()
        #print(self.popt_1)
        #print(self.popt_2)
    def get_frequencies(self):
        dt = self.data[self.column_names[2]][1]-self.data[self.column_names[2]][0]
        fourier_transform = np.fft.fft(self.data[self.column_names[0]])
        freq = np.fft.fftfreq(self.data[self.column_names[0]].size, d=dt)
        psd = np.abs(fourier_transform) ** 2
        peak_idx = np.argmax( np.abs(psd))
        freq1 = freq[peak_idx]
        self.fit1 = lambda F0,phi,cst,t : fitting_function(F0,phi,freq1,cst,t)

        fourier_transform = np.fft.fft(self.data[self.column_names[1]])
        freq = np.fft.fftfreq(self.data[self.column_names[1]].size, d=dt)
        psd = np.abs(fourier_transform) ** 2
        peak_idx = np.argmax( np.abs(psd))
        freq2 = freq[peak_idx]
        self.fit2 = lambda F0,phi,cst,t : fitting_function(F0,phi,freq2,cst,t)
    def line_select_callback(self,eclick, erelease):
        'eclick and erelease are the press and release events'
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        self.xlim =  (min(x1,x2),max(x1,x2))
        self.ylim = (min(y1,y2),max(y1,y2))
        #print(self.xlim,self.ylim)
    def select_range(self,ShowResult=False):
        fig, ax = plt.subplots()
        self.plot(fig,ax,fit=False)
        xlim = ax.get_xlim()  # Store current xlim
        ylim = ax.get_ylim()  # Store current ylim
        rs = RectangleSelector(ax, self.line_select_callback,
                       useblit=True,
                       button=[1, 3],  # Left and right mouse buttons
                       minspanx=5, minspany=5, # Minimum pixel span
                       spancoords='pixels',
                       interactive=True)
        ax.set_xlim(xlim)  # Reset stored xlim
        ax.set_ylim(ylim)  # Reset stored ylim
        plt.show()
        try:
            while fig.number in plt.get_fignums():
                plt.pause(0.1)
        except:
            plt.close(fig.number)
            raise
        # filter the datas
        #print(self.xlim)
        #print(self.ylim)
        self.data = self.data[(self.data[self.column_names[0]] >= self.ylim[0]) &
                                                (self.data[self.column_names[1]] >= self.ylim[0]) &
                                                (self.data[self.column_names[0]] <= self.ylim[1]) & 
                                                (self.data[self.column_names[1]] <= self.ylim[1]) &
                                                (self.data[self.column_names[2]] >= self.xlim[0]) &
                                                (self.data[self.column_names[2]] <= self.xlim[1]) ]
        if ShowResult:
            fig,ax = plt.subplots()
            self.plot(fig,ax,fit=False)
            plt.show()
    def plot(self,fig,ax,fit=True,Force1=True,Force2=True):
        if Force1:
            ax.plot(self.data[self.column_names[2]],self.data[self.column_names[0]],label='force1')
            if fit:
                ax.plot(self.data[self.column_names[2]],fitting_function(self.data[self.column_names[2]],*self.popt_1),label='fit force 1')
        if Force2:
            ax.plot(self.data[self.column_names[2]],self.data[self.column_names[1]],label='force2')
            if fit:
                ax.plot(self.data[self.column_names[2]],fitting_function(self.data[self.column_names[2]],*self.popt_2),label='fit force 2')
        ax.legend()
    def compute_chi_sys(self):
        F0_1 = self.popt_1[0] * np.exp(1j * self.popt_1[1])
        F0_2 = self.popt_2[0] * np.exp(1j * self.popt_2[1])
        X0_ = self.amplitude * np.exp(1j * self.phase)
        self.chi_sys = (F0_2-F0_1)/(2*X0_)
    def compute_chi(self):
        if not hasattr(self,'chi_sys'):
            self.compute_chi_sys()
        omega = self.freq*2*np.pi
        self.chi = self.chi_sys * (4*self.k1x*self.k2x + 1j*self.xi+omega*(self.k1x+self.k2x))/(2*self.k1x*(2*self.k2x+1j*self.xi*omega) - 4*self.chi_sys * (self.k1x+self.k2x+1j*self.xi*omega))
    def get_fitting_parameters(self):
        return [self.freq,self.phase,self.amplitude]
