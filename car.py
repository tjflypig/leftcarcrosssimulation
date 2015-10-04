# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 22:52:05 2015

@author: hustf
"""

import random
import time
import global_list_car as config

class Car:
    def __init__(self,id,lamda,gu=50,gs=10):
        self.__id = id
        self.lamda = lamda
        self.state = 0 #0: not in line 1:in line
        self.index = 0 #the index in a platoon
        self.speed = random.gauss(gu,gs)
        self.headway = random.expovariate(self.lamda)
        #print ('Creat a car ,id is %d,speed is %.2f,headway is %.2f'%(self.id,self.speed,self.headway))
    
    def GetId(self):
        return self.__id 
        
    def UpdateHeadway(self,newheadway = config.limitheadway):
        self.headway = newheadway
    
    def UpdateIndex(self,newindex):
        self.index = newindex
 
    def UpdateSpeed(self,newspeed):
        self.speed = newspeed

    def UpdateState(self,newstate):
        self.state = newstate

    def ShowCar(self):
        print ('car information: id:%d,headway:%.2f,index:%d'%(self.GetId(),self.headway,self.index))

'''
class StCar(Car):
    def __init__(self,id):
        Car.__init__(self,id)
        
    def SetpMoving(self,a):
        newspeed = self.speed + a
        self.UpdateSpeed(newspeed)
        

class LeftCar(Car):
    def __init__(self,id):
        Car.__init__(self,id)      
'''
#key class of this program, the Straight and left cars will be put into a platoon        
class Platoon:
    def __init__(self,pid,initnum,lamda):
        self.id = pid
        self.platoon = {}
        self.initnum = initnum
        self.lamda = lamda
        self.count = 0
        self.comenum = 0 # total come cars in this platoon
        self.crossnum = 0 #total cross cars in this platoon
        self.lastcarindex = -1  #last come car
        self.cometime = {}
        self.CreatCars()
        self.CreatPlatoon()        
        
    #initialization functions of Platoon    
    def AddCar(self,carid):
        self.platoon[carid] = Car(carid,self.lamda)
        self.platoon[carid].UpdateIndex(self.count)
        self.count += 1
        try:
            if self.platoon[carid].headway < config.limitheadway:
                self.platoon[carid].UpdateHeadway()
            if self.platoon[carid].speed > self.platoon[carid - 1].speed:
                self.platoon[carid].speed = self.platoon[carid - 1].speed
        except:
            pass

    def CreatCars(self):
        for carid in range(self.initnum):
            self.platoon[carid] = Car(carid,self.lamda)
        
    def CreatPlatoon(self):
        for carid in self.platoon:
            self.AddCar(self.platoon[carid].GetId())
            if carid == 0:
                self.cometime[carid] = self.platoon[carid].headway
            else:
                self.cometime[carid] = self.cometime[carid -1] + self.platoon[carid].headway
     
    def DeleteCar(self,carid):
        del self.platoon[carid]
        self.count -=1
        for Car in self.platoon:
            self.platoon[Car].UpdateIndex(self.platoon[Car].index - 1)
        for i in range(1,len(self.platoon)+1):
            self.platoon[i-1] = self.platoon[i]
        del self.platoon[len(self.platoon)-1]
            
            
    def IsCome(self,sec):     
        if self.lastcarindex == -1:
            if sec > self.cometime[0] - 1: # pay attention of the first step of time
                self.lastcarindex += 1                
                return True
            else:
                return False
        else:
             if sec > self.cometime[self.lastcarindex + 1] - 1:
                 self.lastcarindex += 1                 
                 return True
             else:
                 return False
                 
    def ShowPlatoon(self):
        print('init car num = %d,cars come in this cycle = %d, total cross cars = %d'%(self.count,self.comenum,self.crossnum))
        
class Simulation:
    def __init__(self,time = config.time,cycle = config.cycle,green = config.green):
        self.time = time
        self.cycle = cycle
        self.green = green
        self.red = self.cycle - self.green
        self.sigstate = 0 #0:red 1:green
        self.passgreen = -1
        self.passred = -1
        self.control = Control()
    
    def UpdateConfig(self,time,cycle,green):
        self.time = time
        self.cycle = cycle
        self.green = green
        self.red = self.cycle - self.green      
        
    def JudgeSec(self,sec):
        if  sec < self.red:
            self.sigstate = 0
        else:
            self.sigstate = 1
    
    def SimulationRun(self):
        for i in range(self.time):
            print ('---The %d time of this simulation---' % (i+1))
            self.SimulationOneTime()
            self.SimulationShow()
    
    def SimulationInit(self):
        self.passgreen = -1
        self.passred = - 1
        self.control.InitControl()
        
    def SimulationOneTime(self):
        self.SimulationInit()
        for i in range(self.cycle):
            self.SimulationStep(i)
              
    def SimulationStep(self,sec):
        self.JudgeSec(sec)
        if self.sigstate == 0:
            self.control.RedLogic(sec)
            self.passred += 1
        else:
            self.control.GreenLogic(sec)
            self.passgreen += 1
    
    def SimulationShow(self):
        print('total come st cars: %d, cross cars: %d'%(self.control.stplatoon.comenum,self.control.stplatoon.crossnum))
        print('total come left cars:%d, crass cars: %d'%(self.control.leftplatoon.comenum,self.control.leftplatoon.crossnum))
        
        
class Control:
    def __init__(self):
        self.stplatoon = Platoon(0,config.stinitnum,config.stlamda) 
        self.leftplatoon = Platoon(1,config.leftinitnum,config.leftlamda)
        self.crossgap  = config.crossgap
    
    def InitControl(self):
        self.stplatoon = Platoon(0,config.stinitnum,config.stlamda) 
        self.leftplatoon = Platoon(1,config.leftinitnum,config.leftlamda)

#if a platoon cannot go away,it must judge the next car come and line up    
    def HoldCarComeUpdate(self,platoon,sec):
        if platoon.IsCome(sec):
            platoon.comenum += 1
            if platoon.platoon[platoon.lastcarindex].index == 0:
                platoon.platoon[platoon.lastcarindex].UpdateHeadway(0)
                platoon.platoon[platoon.lastcarindex].UpdateState(1)
            else:
                platoon.platoon[platoon.lastcarindex].UpdateHeadway()
                platoon.platoon[platoon.lastcarindex].UpdateState(1)
        else:
            pass
        
#if a platoon is going away,it must judge the next car come and the car line up or cross        
    def PassCarComeUpdate(self,platoon,sec):
        if platoon.IsCome(sec):
            platoon.comenum += 1
            if platoon.platoon[platoon.lastcarindex].index != 0:
                platoon.platoon[platoon.lastcarindex].UpdateHeadway()
                platoon.platoon[platoon.lastcarindex].UpdateState(1)
        else:
            pass

#cross interaction between of left and straight    
    def GreenInterAction(self):
        if self.stplatoon.platoon[0].headway > self.crossgap:
            self.CarGoUpdate(self.leftplatoon)
            self.CarHoldUpdate(self.stplatoon)
        else:
            self.CarGoUpdate(self.stplatoon)
            self.CarHoldUpdate(self.leftplatoon)
    
    def CarHoldUpdate(self,platoon):
        platoon.platoon[0].UpdateHeadway(0)       
        
    def CarGoUpdate(self,platoon):
        if platoon.platoon[0].headway == 0:
            platoon.DeleteCar(0)
            platoon.crossnum += 1
            platoon.platoon[0].UpdateHeadway(platoon.platoon[0].headway - 1)
        else:
            platoon.platoon[0].UpdateHeadway(platoon.platoon[0].headway - 1)
    
    def RedLogic(self,sec):
        self.HoldCarComeUpdate(self.stplatoon,sec)
        self.HoldCarComeUpdate(self.leftplatoon,sec)

#It is the logic of green time
#If leftcrossconfig = 1 the left cars will go in front of straight at the begining of green  
    def GreenLogic(self,sec,leftcrossconfig = config.leftgofirst):
        self.PassCarComeUpdate(self.stplatoon,sec)
        self.PassCarComeUpdate(self.leftplatoon,sec)
        self.GreenInterAction()
    
    
#calculate the program run time
def gettime(fun):
    start = time.clock()
    fun()
    print('-----------------finished-----------------')
    print('cost time: %.2fs'%(time.clock()-start))

def main():
    sim = Simulation()
    sim.SimulationRun() 
#    sp = Platoon(1,10,(1/6))
#    for i in sp.platoon:
#        sp.platoon[i].ShowCar()
#    print(sp.platoon)
#    print('\n')    
#    sp.DeleteCar(0)
#    print(sp.platoon)
#    for i in sp.platoon:
#        sp.platoon[i].ShowCar()
                
        
if __name__=='__main__':
    gettime(main)
        