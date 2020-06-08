import pandas as pd
import numpy as np
import scipy.integrate as integrate
from scipy.optimize import fsolve
from scipy import signal
from scipy import fft, fftpack
from scipy.signal import hilbert


#This group of functions are to be used for power quality assessments 

def harmonics(x,freq):
    """
    Calculates the harmonics from time series of voltage or current based on IEC 61000-4-7. 

    Parameters
    -----------
    x: pandas Series of DataFrame
        timeseries of voltage or current
    
    freq: float
        frequency of the timeseries data [Hz]
    
    Returns
    --------
    harmonics: float? Array? 
        harmonics of the timeseries data
    """
    
    x.to_numpy()
    
    a = np.fft.fft(x,axis=0)
    
    amp = np.abs(a) # amplitude of the harmonics
    #print(len(amp))
    freqfft = fftpack.fftfreq(len(x),d=1./freq)
    ##### NOTE: Harmonic order is fft freq/ number of fundamentals in the sample time period, look int if this is what I should be using
    ### Note: do I need to impliment the digital low pass filter equations ???

    harmonics = pd.DataFrame(amp,index=freqfft)
    
    harmonics=harmonics.sort_index(axis=0)
    #print(harmonics)
    hz = np.arange(0,3000,5)
    
    ind=pd.Index(harmonics.index)
    indn = [None]*np.size(hz)
    i = 0
    for n in hz:
        indn[i] = ind.get_loc(n, method='nearest')
        i = i+1
    
    harmonics = harmonics.iloc[indn]
    
    return harmonics


def harmonic_subgroups(harmonics, frequency): 
    """
    calculates the harmonic subgroups based on IEC 61000-4-7

    Parameters
    ----------
    harmonics: pandas Series or DataFrame 
        RMS harmonic amplitude indexed by the harmonic frequency 
    frequency: int
        value indicating if the power supply is 50 or 60 Hz. Valid input are 50 and 60

    Returns
    --------
    harmonic_subgroups: array? Pandas?
        harmonic subgroups 
    """
    #assert isinstance(frequency, {60,50]), 'Frequency must be either 60 or 50'

    #def subgroup(h,ind):
        

    if frequency == 60:
        
        hz = np.arange(1,3000,60)
    elif frequency == 50: 
        
        hz = np.arange(1,2500,50)
    else:
        print("Not a valid frequency")
        pass
    
    j=0
    i=0
    cols=harmonics.columns
    #harmonic_subgroups=[None]*np.size(hz)
    harmonic_subgroups=np.ones((np.size(hz),np.size(cols)))
    for n in hz:

        harmonics=harmonics.sort_index(axis=0)
        ind=pd.Index(harmonics.index)
        
        indn = ind.get_loc(n, method='nearest')
        for col in cols:
            harmonic_subgroups[i,j] = np.sqrt(np.sum([harmonics[col].iloc[indn-1]**2,harmonics[col].iloc[indn]**2,harmonics[col].iloc[indn+1]**2]))
            j=j+1
        j=0
        i=i+1
        #print(harmonic_subgroups)
    
    harmonic_subgroups = pd.DataFrame(harmonic_subgroups,index=hz)

    return harmonic_subgroups

def total_harmonic_current_distortion(harmonics_subgroup,rated_current):    #### might want to rename without current since this can be done for voltage too

    """
    Calculates the total harmonic current distortion (THC) based on IEC 62600-30

    Parameters
    ----------
    harmonics_subgroup: pandas DataFrame or Series
        the subgrouped RMS current harmonics indexed by harmonic order
    
    rated_current: float
        the rated current of the energy device in Amps
    
    Returns
    --------
    THC: float
        the total harmonic current distortion 
    """
    #print(harmonics_subgroup)
    harmonics_sq = harmonics_subgroup.iloc[2:50]**2

    harmonics_sum=harmonics_sq.sum()

    THC = (np.sqrt(harmonics_sum)/harmonics_subgroup.iloc[1])*100

    return THC

def interharmonics(harmonics,frequency):
    """
    calculates the interharmonics ffrom the harmonics of current

    Parameters
    -----------
    harmonics: pandas Series or DataFrame 
        RMS harmonic amplitude indexed by the harmonic frequency 

    frequency: int
        value indicating if the power supply is 50 or 60 Hz. Valid input are 50 and 60

    Returns
    -------
    interharmonics: pandas DataFrame
        interharmonics groups
    """
    #Note: work on the data types, df, Series, numpy to streamline this. Will I ever pass multiple columns of harmonics??
    #assert isinstance(frequency, {60,50]), 'Frequency must be either 60 or 50'

    if frequency == 60:
        
        hz = np.arange(0,3000,60)
    elif frequency == 50: 
        
        hz = np.arange(0,2500,50)
    else:
        print("Not a valid frequency")
        pass
    j=0
    i=0
    cols=harmonics.columns
    interharmonics=np.ones((np.size(hz),np.size(cols)))
    for n in hz: 
        harmonics=harmonics.sort_index(axis=0)
        ind=pd.Index(harmonics.index)
        
        indn = ind.get_loc(n, method='nearest')  
        if frequency == 60:
            subset = harmonics.iloc[indn+1:indn+11]**2
            subset = subset.squeeze()
        else: 
            subset = harmonics.iloc[indn+1:indn+7]**2
            subset = subset.squeeze()
        for col in cols:
            interharmonics[i,j] = np.sqrt(np.sum(subset))
            j=j+1
        j=0
        i=i+1
    
    
    interharmonics = pd.DataFrame(interharmonics,index=hz)

    return interharmonics
