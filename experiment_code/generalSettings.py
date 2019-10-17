# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 09:02:46 2017

@author: Elle
"""

from experimentfunctions import angle2pix   
import numpy as np 


#screen settings 
hRes = 1366           # horizontal resolution (pix)
vRes = 768             # vertical resolution   (pix)
screenHeight = 22#27.3       # height of screen in    (cm) 
screenDistance = 57#57     # distance to screen     (cm) 
refreshrate = 60        # refreshrate of the screen (Hz) 
backCol = 'gray'        # background color of the screen 

#######################
## stimulus settings ##
########################

# the dots 
nDots = 100                                                           # number of dots presented 
dotSizeDegree = 0.44                                                  # dotsize in degrees/visual angle                                             
dotSize = angle2pix(dotSizeDegree,screenHeight,screenDistance,vRes)   # size of the dots in pixels (first entry of angle2pix is size in degrees)
minDistance = 0                                                       # min distance from center of screen to a dot (pix)
maxDistance = angle2pix(7.5,screenHeight,screenDistance,vRes)         # max distance of screen center to a dot (pix)
cyclesPerDegree = 3.4 
cyclesPerElement = dotSizeDegree*cyclesPerDegree 
presentationDur = 600 # in ms
presentationDurFrames = np.ceil(presentationDur/(1000.0/refreshrate))

# the feedback stimulus 
feedbackdotSize = angle2pix(0.30,screenHeight,screenDistance,vRes)    # size of the feedback dot (pix)

# information for the distributions 
nSamples = nDots 
sigma = np.array([0,2,4,8,16,32]) # external noise levels
sigmaCompact = np.array([0,-1])   # 0 = zero-noise condition; -1 = high-noise condition
                       
# general QUEST settings 
nQtrials = 75
gamma = 0.5
delta = 0.01
pThreshold = 0.82 

# fixed mu for the efficient experiments 
fixedMuMotion = 45
fixedMuOrientation = 22.5
fixedMuSize = 0.5

# break settings 
breakTrial = 50 # take a break after this many trials (would be nice if this devides the experiment in equal parts)

# number of repetitions for the efficient tasks 
nReps = 3
nCatchTrialsCompact = 75
nCatchTrials = 75
fixedSigma = 0.5 

def questSettings(experiment): 
    
    ####################################
    # experiment specific QUEST settings 
    #####################################
    
    ##################
    # long experiments
    ##################
    
    if experiment == 'ori': 
        # orientation  
        startVals = [np.log10(2.5),np.log10(2.5),np.log(2.5),np.log10(10),np.log10(10),np.log10(30),np.log10(30)]
        questSD = [3]*7
        questRange = [None,None,None,None,None,None,None]
        minVals = [-3,-3,-3,-3,-3,-3,-3]
        maxVals = [np.log10(60),np.log10(60),np.log10(60),np.log10(60),np.log10(60),np.log10(60),np.log10(60)]
        
    elif experiment == 'motion': 
    
        # motion 
        startVals = [np.log10(4),np.log10(10),np.log10(10)]
        questSD = [np.log10(10),np.log10(10),np.log10(10)]
        questRange = [None,None,None]
        minVals = [-3,-3,-3]
        maxVals = [np.log10(40),np.log10(40),np.log10(40)]
        
    elif experiment == 'size': 
        # size 
        startVals = [np.log10(0.2),np.log10(0.3),np.log10(0.5)]
        questSD = [np.log10(3),np.log10(3),np.log10(3)] 
        questRange = [None,None,None]
        minVals = [None,None,None]
        maxVals = [np.log10(2),np.log10(2),np.log10(2)]
    
    #####################
    # compact experiments 
    #####################
    
    elif experiment == 'oriCompact':
        # orientation 
        startVals = [np.log10(2.5),-np.log10(30)]
        questSD = [np.log10(3),np.log10(3)] 
        questRange = [None,None]
        minVals = [-5,-5]
        maxVals = [np.log10(40),None]
    
    elif experiment == 'motionCompact': 
    
        startVals = [np.log10(4),-np.log10(50)]
        questSD = [np.log10(3),np.log10(5)] 
        questRange = [None,None]
        minVals = [-5,-5]
        maxVals = [np.log10(40),None]
    
    elif experiment == 'sizeCompact': 
    
        startVals = [np.log10(0.5),-np.log10(.5)]
        questSD =  [3,3]#[np.log10(3),np.log10(3)] 
        questRange = [None,None]
        minVals = [None,None]
        maxVals = [np.log10(2),None]
    
    else:
        raise ValueError('Wrong input!')
        
    return startVals,questSD, questRange, minVals, maxVals  

# motion settings
dotLifeInMs = 1000 
dotLifeInFrames = np.ceil(dotLifeInMs/(1000.0/refreshrate))
nMotionDots = 300

degreePerSecond = 3
pixPersecond = angle2pix(degreePerSecond,screenHeight,screenDistance,vRes)
pixPerFrame = pixPersecond/refreshrate

# catch trial information 
sdCatch = 0.5
intensityCatchMotion = 45
intensityCatchSize = 0.5 
intensityCatchOrientation = 22.5 

