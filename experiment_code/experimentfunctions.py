  
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 07 17:15:37 2017

@author: Elle
"""

import numpy as np 
from math import atan2, degrees
from psychopy import visual
import random

class RandomDotKinematogram:
    def __init__(self, win,nDots, minDistance, maxDistance, dotSize, mu, sigma, pixPerSecond,flipcos = False):
        self.win = win
        self.nDots = nDots
        self.minDistance = minDistance
        self.maxDistance = maxDistance
        self.dotSize = dotSize
        self.pixPerSecond = pixPerSecond
        self.mu = mu
        self.sigma = sigma
        self.rotationMatrix = np.array([[np.cos(np.pi),np.sin(np.pi)],[-np.sin(np.pi),np.cos(np.pi)]])
        
        self.dotPositions = []        
        for dot in range(self.nDots):
            overlap = True 
            while overlap: 
                r = random.uniform(self.minDistance,self.maxDistance**2) 
                randomAngle=random.uniform(0,1)*2*np.pi
                # calculate x and y position 
                dot_x = np.sqrt(r)*np.cos(randomAngle)
                dot_y = np.sqrt(r)*np.sin(randomAngle)
                
                if not self.dotPositions:
                    break 
               
                diff = np.array(self.dotPositions) - np.array([dot_x,dot_y])
                tmp = abs(diff) < self.dotSize 
                if not True in tmp[:,1] & tmp[:,0]:
                    overlap = False 
        
            # append to list 
            self.dotPositions.append([dot_x, dot_y])    
            
        self.dotPositions = np.array(self.dotPositions)    
        if self.sigma == 0:
            dotDirections = np.array(self.nDots*[self.mu])
        else:
            dotDirections = np.random.normal(self.mu,self.sigma,self.nDots)
        if flipcos:
            self.dotVelocities = np.column_stack((np.sin(np.deg2rad(dotDirections)),np.cos(np.deg2rad(dotDirections))))
        else:
            self.dotVelocities = np.column_stack((np.cos(np.deg2rad(dotDirections)),np.sin(np.deg2rad(dotDirections))))
        
        #create stimulus 
        self.stim = visual.ElementArrayStim(self.win, elementTex = 'none',elementMask = 'circle', nElements=self.nDots, 
                                        sizes=self.dotSize, xys = self.dotPositions,colors = (1,1,1),contrs = 0.5) 
    
    # Return the mean velocity vector and the mean direction of all the dots
    def get_sample_mean(self):
        mean_vector = np.mean(self.dotVelocities, 0)
        mean_dir    = np.arctan2(mean_vector[1],mean_vector[0])
        return [mean_vector, mean_dir]
    
    # Moves each dot according to its velocity vector for a time interval delta_t (assumed given in seconds)
    def update(self,delta_t):
        self.dotPositions += self.pixPerSecond*delta_t*self.dotVelocities
        
        invalidPositions = np.where(np.square(self.dotPositions[:,0]) + np.square(self.dotPositions[:,1]) > self.maxDistance**2)
        self.dotPositions[invalidPositions,:] = np.dot(self.dotPositions[invalidPositions,:],self.rotationMatrix)
        self.dotPositions[invalidPositions,:] += self.pixPerSecond*delta_t*self.dotVelocities[invalidPositions,:]
        self.stim.xys = self.dotPositions
        pass
    
    def draw(self):
        self.stim.draw()
        
    def save_stim_data(self, filename):
        f = open(filename,'w')
        f.write('x,y,dx,dy' + '\n')
        for i in range(self.nDots):
            data = [self.dotPositions[i][0],self.dotPositions[i][1],self.dotVelocities[i][0], self.dotVelocities[i][1]]
            data = [str(d) for d in data]
            f.write(','.join(data) + '\n')
        f.close()
    
def angle2pix(size_in_deg,h,d,r):
    # Calculate the number of degrees that correspond to a single pixel. This will
    # generally be a very small value, something like 0.03.
    deg_per_px = degrees(atan2(.5*h, d)) / (.5*r)
    # Calculate the size of the stimulus in degrees
    size_in_px = size_in_deg / deg_per_px
    return size_in_px 

def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    return(rho, phi)

def pol2cart(rho, phi):  
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return(x, y)   

def reset_dots(n_reset, min_dist, max_dist):
    
    deg = np.random.uniform(min_dist,max_dist**2, size = n_reset)
    
    randomAngle=np.random.uniform(0,1, size = n_reset)*2*np.pi
                                 
    # calculate x and y position 
    dot_x = np.sqrt(deg)*np.cos(randomAngle)
    dot_y = np.sqrt(deg)*np.sin(randomAngle)

    return np.array(zip(dot_x, dot_y))

def calc_intersection_points(new_x, new_y, old_x, old_y, rho, center_x, center_y):

#==============================================================================
# x1 = 1 * np.cos(np.deg2rad(135))
# y1 = 1 * np.sin(np.deg2rad(135))
# 
# x2 = .5 * np.cos(np.deg2rad(90))
# y2 = .5 * np.sin(np.deg2rad(90))
# 
#==============================================================================

    old = np.vstack((old_x, old_y)).T
    new = np.vstack((new_x, new_y)).T
                   
    coef = np.array([np.polyfit(old[i, :], new[i,:], 1) for i in range(old.shape[0])])
    
    a = coef[:,0]
    b = coef[:,1]
    
    r = rho
    p = center_x
    q = center_y
    
    A = a**2 + 1
    B = 2 * ((a * b) - (a * q) - p)
    C = (q**2 - r**2 + p**2 - (2 * b * q) + b**2)
    
    B**2 - 4 * A * C 
    
    x1_new = (-B + np.sqrt((B**2)-4*A*C)) / (2 * A)
    x2_new = (-B - np.sqrt((B**2)-4*A*C)) / (2 * A)
    
    y1_new = a * x1_new + b
    y2_new = a * x2_new + b
    
    new_1 = np.array([x1_new, y1_new]).T
    new_2 = np.array([x2_new, y2_new]).T
    
    dist_1 = np.linalg.norm(new - new_1, axis=1)
    dist_2 = np.linalg.norm(new - new_2, axis=1)
    
    dist = np.array([dist_1, dist_2]).T
    print np.array([np.where(dist[i,:] == np.max(dist[i,:])) for i in range(dist.shape[0])]).shape
    idx = np.array([np.where(dist[i,:] == np.max(dist[i,:])) for i in range(dist.shape[0])])[:,0,0]
    is_points = np.dstack((new_1, new_2))
    new_final = np.array([is_points[i, :, idx[i]] for i in range(is_points.shape[0])])
    
    return new_final