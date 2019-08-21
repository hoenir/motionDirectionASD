#==============================================================================
#     Import libraries
#==============================================================================
from psychopy import prefs
prefs.general['audioLib'] = ['pygame']
import pyglet
from psychopy import visual, event, data, core, clock, monitors, sound
from pygame import mixer
from experimentfunctions import RandomDotKinematogram
import random 
import numpy as np 
import os, time, sys 
import generalSettings as GS
import pandas as pd
#==============================================================================
# Experimental settings 
#==============================================================================
pp = "pm"
session_id = 1
debug = 0 
exp = 'motionCompact'
root_folder =  r'C:\Users\u0103239\Desktop\vis_experiment'
if not os.path.isdir(root_folder):
    print "Error: Could not find the root folder " + root_folder
    sys.exit()

#==============================================================================
# Experimental variables  
#==============================================================================
# Block parameters (7 blocks total), each element contains mu and sigma values for sampling trial
#  directions
BLOCK_PARAMETERS = [[68,20],
                    [68,20],
                    [68,20],
                    [22,20]]

# Variation around the mean direction within each trial
TRIAL_SIGMA = [[10, 40],
               [10, 40],
               [10, 40],
               [10, 40]]

# Number of trials per block, make sure this number is a multiple of the number
#  of different trial sigmas, so that each individual trial sigma occurs equally often
freqs =  [1, 3, 7, 12, 17, 20, 17, 12, 7, 3, 1] #[1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1]
devs  = [-50,-40,-30,-20,-10,0,10,20,30,40,50]
N_PRACTICE_TRIALS = 0
N_TRIALS=sum(freqs)/2

# Number of degrees that the rod changes on each frame, if the arrow keys are pressed
oriDeltaChange = 1.3

FIXATION_DURATION = 0.5
ISI_DURATION = 0.5
CONFIRMATION_DURATION = 0.1
FEEDBACK_DURATION = 0.1

BLOCK_1_SLIDE = 10
BLOCK_2_SLIDE = 11
BLOCK_3_SLIDE = 12
BLOCK_4_SLIDE = 13
BLOCK_5_SLIDE = 14
BLOCK_6_SLIDE = 15
BLOCK_7_SLIDE = 16
BLOCK_8_SLIDE = 17

#==============================================================================
# Create trial structure             
#==============================================================================
experiment_parameters = []

for i in range(N_PRACTICE_TRIALS):
    trial_parameters = {'block_index':-1,
                        'block_trial':-1,
                        'block_mu' : -1,
                        'block_sigma': -1,
                        'trial_mu_deviation':0,
                        'trial_mu': np.random.randint(0,359),
                        'trial_sigma' : 5,
                        'initial_ori': random.randint(0,359),
                        'response': 0,
                        'rt': 0}
    experiment_parameters.append(trial_parameters)
        
for block_index in range(len(BLOCK_PARAMETERS)):
    block_mu = BLOCK_PARAMETERS[block_index][0]
    block_sigma = BLOCK_PARAMETERS[block_index][1]
    
    trial_sigmas = [10]*N_TRIALS + [40]*N_TRIALS
    trial_mu_deviation = []
    for i in range(len(freqs)):
        trial_mu_deviation.extend([devs[i]]*freqs[i])
    random.shuffle(trial_sigmas)
    random.shuffle(trial_mu_deviation)
    
    for trial_index in range(len(trial_mu_deviation)):
        trial_parameters = {'block_index':(2*block_index) + trial_index//N_TRIALS,
                            'block_trial':trial_index%N_TRIALS,
                            'block_mu' : block_mu,
                            'block_sigma': block_sigma,
                            'trial_mu_deviation':trial_mu_deviation[trial_index],
                            'trial_mu': block_mu-trial_mu_deviation[trial_index], 
                            'trial_sigma' : trial_sigmas[trial_index],
                            'initial_ori': random.randint(0,359),
                            'response': 0,
                            'rt': 0}
        experiment_parameters.append(trial_parameters)

headers = ('trial_index','block_index','block_trial','block_mu','block_sigma','trial_mu_deviation','trial_mu','trial_sigma','trial_mean','initial_ori','final_ori','rt')        
df = pd.DataFrame(experiment_parameters, columns=headers)
df.to_csv(root_folder + '/parameter_test.csv')
#%%
#==============================================================================
# Create data file 
#==============================================================================
data_dir = root_folder + '/data_fishing/'
dateStr = time.strftime("%b_%d_%H%M", time.localtime())  # add the current time

filename = pp + "_" + str(session_id) + "_" + dateStr 
output_file_handle = open(data_dir + filename + ".csv",'w')

headers = ('trial_index','block_index','block_trial','block_mu','block_sigma','trial_mu_deviation','trial_mu','trial_sigma','trial_mean','initial_ori','final_ori','rt')
output_file_handle.write(','.join(headers) + '\n')

#==============================================================================
# Create monitor and window
#==============================================================================
# open window
mon = monitors.Monitor(name = 'exp') 
win = visual.Window(size= (GS.hRes, GS.vRes), color=GS.backCol, units='pix',fullscr = debug!=1, waitBlanking=True)

# key handler for keydown events
key = pyglet.window.key
keyboard = key.KeyStateHandler()
win.winHandle.push_handlers(keyboard)

#==============================================================================
# Create stimuli 
#==============================================================================
nFishies = 0
fishingRodRadius = GS.maxDistance + GS.dotSize

# Create and configure text stimuli
startText = visual.TextStim(win, text='Press spacebar to start the experiment', color='white', height=20)
breakText = visual.TextStim(win, text='Time for a break, press spacebar to continue', color='white', height=20)
practiceInstruction  = visual.TextStim(win,"Vanaf nu begint het echte experiment! Druk op de spatiebalk als je er klaar voor bent.",units='norm',height=0.05,wrapWidth=1.5)
fishScore=visual.TextStim(win,str(nFishies).zfill(3),units='norm',pos=[0.95,0.9],height=0.05,wrapWidth=1.5)

# Create Image stimuli
bearFishing = visual.ImageStim(win,"images\\bear_fishing_1.png",units = 'norm', pos=[-0.8,0.8], opacity=0.75)
fishingRod = visual.ImageStim(win,"images\\fishing_rod.png",size=[int(GS.maxDistance + GS.dotSize)/2, int(GS.maxDistance + GS.dotSize)/2],units='pix')
fish_1 = visual.ImageStim(win,"images\\fish_1.png",units='norm',pos = [0.8,0.85],opacity=1,size=[0.15,0.2])
rSize = np.sqrt(2)*fishingRod.size[0]
fishingRod.size *= (fishingRodRadius/rSize)
rSize = np.sqrt(2)*fishingRod.size[0]/2
lure   = visual.ImageStim(win,"images\\aas.png",units='pix',pos = [-(win.size[0]//2)+200,340])

instructionImages = []
for slideIndex in range(1,18):
    slide = visual.ImageStim(win, root_folder + '\\instructions\\Slide' + str(slideIndex) + '.PNG')
    instructionImages.append(slide)

# Create Shapestim
fixStim = visual.Circle(win, radius= GS.feedbackdotSize, fillColor= 'black', lineColor = 'black') 
trueDirectionLine = visual.Line(win,start=[0,0],end=[10,10],units='pix',lineWidth=2.5)
sampleDirectionLine = visual.Line(win, start=[0,0],end=[10,10],units='pix',lineWidth=2.5)
fishCircle  = visual.Circle(win,radius = GS.maxDistance + GS.dotSize,edges=64,lineWidth=2.5)

# Progress bar
progress_bar_height = 600
progressBarContainer = visual.Rect(win, pos=[-(win.size[0]//2)+200,0], height=progress_bar_height,width=80, units='pix',lineWidth=1)
progressBar = visual.Rect(win, pos=[-(win.size[0]//2)+200,0], height=progress_bar_height-2,width=78, units='pix',fillColor="#E38965",lineColor="#E38965")

# Set Autodraw list
# Autodraw means these stimuli will automatically be drawn when a win.flip() command is executed
autoDrawList = [fishCircle,fixStim,fish_1,fishScore, progressBarContainer, progressBar, lure]

# Load bubble sound
mixer.init()
effect = mixer.Sound(root_folder + '\\bubbles.mp3')
effect.play()
core.wait(0.5)
#==============================================================================
# Start trial loop
#==============================================================================
# Show initial instructions
    
for slideIndex in range(1,10):
    instructionImages[slideIndex-1].draw()
    win.flip()
    event.waitKeys(keyList=['space'])
for s in autoDrawList:
    s.setAutoDraw(True)
    
# And go over all trials
opponentFishies = 0

currentBlock = -1
blockTrialIndex = 0
for trial_index in range(len(experiment_parameters)): 
    if currentBlock > -1:
        blockTrialIndex += 1
    
    
    
    if experiment_parameters[trial_index]['block_index'] != currentBlock:
        blockTrialIndex = 0
        currentBlock = experiment_parameters[trial_index]['block_index']
        
        for s in autoDrawList:
            s.setAutoDraw(False)
           
        if opponentFishies < (nFishies-1):
            opponentFishies = np.random.randint(opponentFishies, nFishies-1)
        
        myText = visual.TextStim(win, str(opponentFishies), units='pix',pos=[1018-640,-(451-360)], color=(-1,-1,-1), height=28)
        opText = visual.TextStim(win, str(nFishies), units='pix',pos=[718-640,-(451-360)], color=(-1,-1,-1),height = 28)
        
        if currentBlock == 0:
            practiceInstruction.draw()
        elif currentBlock == 1:
            instructionImages[BLOCK_1_SLIDE-1].draw()
        elif currentBlock == 2:
            instructionImages[BLOCK_2_SLIDE-1].draw()
        elif currentBlock == 3:
            instructionImages[BLOCK_3_SLIDE-1].draw()
        elif currentBlock == 4:
            instructionImages[BLOCK_4_SLIDE-1].draw()
        elif currentBlock == 5:
            instructionImages[BLOCK_5_SLIDE-1].draw()
        elif currentBlock == 6:
            instructionImages[BLOCK_6_SLIDE-1].draw()
        elif currentBlock == 7:
            instructionImages[BLOCK_7_SLIDE-1].draw()
        elif currentBlock ==8:
            instructionImages[BLOCK_8_SLIDE-1].draw()
        
        if currentBlock > 0:
            myText.draw()
            opText.draw()
        win.flip()
        event.waitKeys(keyList=['space'])
            
        for s in autoDrawList:
            s.setAutoDraw(True)
        
    progressBar.height = int(((N_TRIALS-blockTrialIndex)/float(N_TRIALS))*(progress_bar_height-2))
    progressBar.pos[1] = -int(0.5*(progress_bar_height-progressBar.height))
    
    # 1. Initialize all parameters and stimuli
    experiment_parameters[trial_index]['trial_index'] = trial_index
    trial_mu = experiment_parameters[trial_index]['trial_mu']
    trial_sigma = experiment_parameters[trial_index]['trial_sigma']
    fishingRod.ori = experiment_parameters[trial_index]['initial_ori']
    trueDirectionLine.end = [rSize*np.cos(np.deg2rad(trial_mu)), rSize*np.sin(np.deg2rad(trial_mu))]
    dotStim = RandomDotKinematogram(win, GS.nDots, GS.minDistance, GS.maxDistance,GS.dotSize,trial_mu,trial_sigma,GS.pixPersecond)
    sampleDirection = dotStim.get_sample_mean()
    experiment_parameters[trial_index]['trial_mean'] = sampleDirection[1]
    sampleDirectionLine.end = [rSize*2*np.cos(sampleDirection[1]), rSize*2*np.sin(sampleDirection[1])]
    
    # 2. Draw fixation stimulus:
    #    Play sound and initialy wiggle the fixation dot
    t = core.getTime()
    fixationPeriod = True
    mixer.music.load(root_folder + '\\bubbles.mp3')
    mixer.music.play(0)
    basePos = fixStim.pos
    while fixationPeriod:
        if (core.getTime() -t) < 0.5:
            fixStim.pos = [basePos[0] + np.random.uniform(-5,5),basePos[1] + np.random.uniform(-5,5)]
        elif (core.getTime()-t) < 1.5:
            fixStim.pos = basePos
        else:
            break
        fixStim.draw()
        win.flip()
    
    
    # 2. Draw the moving dots
    i = 0;    
    t_0 = core.getTime()
    t = core.getTime()
    while core.getTime()-t_0 < (GS.presentationDur/1000.0):   
        # Get the elapsed time, to properly update the dotStim
        t_now = core.getTime()
        delta_t = t_now - t
        t = t_now
        dotStim.update(delta_t)
        #print delta_t
        # Draw all the components
        dotStim.draw()
        win.flip()
        i = i+1 

    print core.getTime() - t_0
    # 3. Collect participant response
    responded = False
    event.clearEvents()
    t = core.getTime()
    while not responded:
        key_list = event.getKeys(['escape','left','right','space','f','s'])
        if 'f' in key_list:
            oriDeltaChange += .5
            print oriDeltaChange
        elif 's' in key_list:
            oriDeltaChange =  max(0,oriDeltaChange-.5)
        elif 'escape' in key_list:
            win.close()
        elif keyboard[key.LEFT]:
            fishingRod.ori -= oriDeltaChange
        elif keyboard[key.RIGHT]:
            fishingRod.ori += oriDeltaChange
        elif 'space' in key_list:
            responded = True
            break
        
        fishingRod.pos = [rSize*np.cos(np.deg2rad(45-fishingRod.ori)),rSize*np.sin(np.deg2rad(45-fishingRod.ori))]
        fishingRod.draw()
        win.flip()
    rt = core.getTime() - t
    
    # 4. Update the score 
    subjectDirection = (-1*(fishingRod.ori-45))%360
    meanDirection = np.rad2deg(sampleDirection[1])
    experiment_parameters[trial_index]['final_ori'] = subjectDirection
    experiment_parameters[trial_index]['rt'] = rt
    
    ori_diff = subjectDirection - meanDirection
    if ori_diff > 180:
        ori_diff -= 360
    elif ori_diff < -180:
        ori_diff += 360
      
    #print subjectDirection
    #print meanDirection
    #print ori_diff
    #print " "
    amplitude = 0
    if abs(ori_diff) <= 10:
        nFishies += 3
        amplitude = 0.01
    elif abs(ori_diff) <= 20:
        nFishies += 2
        amplitude = 0.005
    elif abs(ori_diff) <= 30:
        nFishies += 1
        amplitude = 0.0025
    fishScore.text = str(nFishies).zfill(3)
        
    # 5. Display confirmation and feedback
    t = core.getTime()
    basePos = fish_1.pos
    feedbackCompleted = False
    while not feedbackCompleted:
        t_now = core.getTime() - t
        # Wiggle the fish
        if t_now -t < 0.3:
            fish_1.pos = [basePos[0] + np.random.uniform(-amplitude,amplitude),basePos[1] + np.random.uniform(-amplitude,amplitude)]
        else:
            fish_1.pos = basePos
            
        # Display a confirmation sequence + feedback sequence
        if t_now < CONFIRMATION_DURATION:
            fishingRod.draw()
        if CONFIRMATION_DURATION < t_now < CONFIRMATION_DURATION + FEEDBACK_DURATION:
            sampleDirectionLine.draw()
        if t_now >= CONFIRMATION_DURATION + FEEDBACK_DURATION:
            #fish_1.pos = basePos
            feedbackCompleted = True
            break
        win.flip()    
      
    # 6. Write trial data output
    outputLine = [str(experiment_parameters[trial_index][h]) for h in headers]
    outputLine = ','.join(outputLine)
    output_file_handle.write(outputLine + '\n')
    dotStim.save_stim_data(root_folder + '\\data_fishing\\' + filename + "_trial_" + str(trial_index) + ".csv")    
        
    win.flip()    
    clock.wait(ISI_DURATION)


output_file_handle.close()
# Turn of all display elements and show final instruction screen
for s in autoDrawList:
            s.setAutoDraw(False)


myText = visual.TextStim(win, str(opponentFishies), units='pix',pos=[1018-640,-(451-360)], color=(-1,-1,-1), height=28)
opText = visual.TextStim(win, str(nFishies), units='pix',pos=[718-640,-(451-360)], color=(-1,-1,-1),height = 28)
instructionImages[BLOCK_8_SLIDE-1].draw()
myText.draw()
opText.draw()
win.flip()
event.waitKeys(keyList=['space'])
win.close()
