# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 22:52:05 2015

@author: hustf
"""

import random
import time
import global_list_car as config

class Car:
    def __init__(self,id,gu=50,gs=10,lamda=(1/6)):
        self.__id = id
        self.state = 0 #0为排队
        self.index = 0 #车队中的顺序编号
        self.speed = random.gauss(gu,gs)
        self.headway = random.expovariate(lamda)
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
    def __init__(self,pid,initnum,lamda=(1/6)):
        self.id = pid
        self.platoon = {}
        self.initnum = initnum
        self.lamda = lamda
        self.count = 0
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
            self.platoon[carid] = Car(carid)
        
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
                 
        
class Simulation:
    def __init__(self,time = config.time,cycle = config.cycle,green = config.green):
        self.time = time
        self.cycle = cycle
        self.green = green
        self.red = self.cycle - self.green
        self.sigstate = 0 #0:red 1:green
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
            print ('---The %d times of this simulation---' % i)
            self.SimulationOneTime()
            
    def SimulationOneTime(self):
        for i in range(self.cycle):
            self.SimulationStep(i)
              
    def SimulationStep(self,sec):
        self.JudgeSec(sec)
        if self.sigstate == 0:
            self.control.RedLogic(sec)
        else:
            self.control.GreenLogic(sec)
        
        
class Control:
    def __init__(self):
        self.stplatoon = Platoon(0,config.stinitnum,config.stlamda) 
        self.leftplatoon = Platoon(1,config.leftinitnum,config.leftlamda)
        self.crossgap  = config.crossgap
        self.leftcrossnum = 0
        
    def RedCarComeUpdate(self,platoon,sec):
        if platoon.IsCome(sec):
            if platoon.platoon[platoon.lastcarindex].index == 0:
                platoon.platoon[platoon.lastcarindex].UpdateHeadway(0)
            else:
                platoon.platoon[platoon.lastcarindex].UpdateHeadway()
        else:
            pass
        
    def RedLogic(self,sec):
        self.RedCarComeUpdate(self.stplatoon,sec)
        self.RedCarComeUpdate(self.leftplatoon,sec)
    
    def GreenLogic(self,sec):
        pass
    
    
#calculate the program run time
def gettime(fun):
    start = time.clock()
    fun()
    print('cost time: %.2fs'%(time.clock()-start))

def main():
    sim = Simulation()
    sim.SimulationRun() 
    for i in range(10):
        sim.control.leftplatoon.platoon[i].ShowCar()     
        
#    sp = Platoon(1,20)
#    for i in sp.platoon:
#        sp.platoon[i].ShowCar()
#    
#    print('\n')    
#    sp.DeleteCar(0)
#    for i in sp.platoon:
#        sp.platoon[i].ShowCar()
#        
#    print('\n')
#    print(sp.cometime)
#    for i in range(90):
#        print('index:%d , iscarcome:%s'%(sp.lastcarindex,sp.IsCome(i)))
        
        
if __name__=='__main__':
    gettime(main)
        