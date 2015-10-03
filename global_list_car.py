# -*- coding: utf-8 -*-
"""
Created on Sat Oct  3 15:47:18 2015

@author: hustf
"""

#simulation config
#times of simulation
time = 300 
#cycle (s)
cycle = 90
#green time of cycle (s)
green = 40

#create car config
#shortest headway of cars (s)
limitheadway = 2
#Straight cars config
stlamda = (1/6)
stinitnum = 30
#left cars
leftlamda=(1/18)
leftinitnum = 20

#interaction config
#the left-turn cars will cross when there is a Straight gap larger than crossgap
crossgap = 3
#left cars go first when green onset (0:off 1:on)
leftgofirst = 0