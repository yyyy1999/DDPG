# -*- coding: utf-8 -*-
"""

@author: sigaud
"""
import random
from collections import deque
from minibatch import minibatch
from sample import sample
import numpy as np

class replay_buffer(object):
    """
    A sample from an agent environment interaction
    """
    def __init__(self, min_filled,size):
        self.buffer = deque([])
        self.bests = []
        self.sample_minibatch=[]
        self.size = size
        self.min_filled = min_filled
        self.reward_min = float("Inf")
        self.reward_max = -float("Inf")
        
        self.alpha=0.5
        self.distribution=[]

    def flush(self):
        self.buffer = deque([])
            
    def current_size(self):
        return len(self.buffer)
        
    def store_samples_from_batch(self, s_t, a_t, r_t, s_t_next):
        assert(False)
#        self.reward_max = max(r_t, self.reward_max)
#        self.reward_min = min(r_t, self.reward_min)   
#        print self.reward_min, self.reward_max
#        for i in range(len(s_t)):
#            if (self.isFull()):
#                self.buffer[random.randint(self.size/5, self.size-1)] = [list(s_t[i]), list(a_t[i]), r_t[i], list(s_t_next[i])]
#            else:
#                self.buffer.append([list(s_t[i]), list(a_t[i]), r_t[i], list(s_t_next[i])])
        
    def store_one_sample(self, sample):
        self.reward_max = max(sample.reward, self.reward_max)
        self.reward_min = min(sample.reward, self.reward_min)   
        if len(self.bests)==0 or self.bests[-1].reward < sample.reward:
            i=1
            while i<=len(self.bests) and self.bests[-i].reward < sample.reward:
                i+=1
            self.bests.insert(len(self.bests)-i, sample)
            if len(self.bests)>1000:
                self.bests.pop()
        if (self.isFull()):
            # replace an older sample, but protecting the beginning
            self.buffer[random.randint(self.size/5, self.size-1)] = ((self.buffer[0],sample))
        elif len( self.buffer)<5:
            self.buffer.append((1,sample))
        else:
            self.buffer.append((self.buffer[0],sample)) 
            
        if not(self.isFull()):
            self.distribution=[(1.0/i)**self.alpha for i in range(1,self.current_size()+1)] 
            s = sum(self.distribution)
            self.distribution=[i/s for i in self.distribution] 

        
    def isFullEnough(self):
        return (self.current_size()>self.min_filled)

    def isFull(self):
        return (self.current_size()>=self.size)

    def get_state(self,index):
        return self.buffer[index][1].state

    def get_random_minibatch(self,batch_size):
            states = []
            rewards = []
            actions = []
            next_states = []
            for i in range(batch_size):
                if random.uniform(0.0,1.0)<0.1:
                    index= random.randint(0, len(self.bests)-1)
                    sample = self.bests[index]
                else:
                    index= random.randint(0, self.current_size()-1)
                    sample = self.buffer[index]
                    
                states.append(sample.state) #no need to put into [] because it is already a vector
                actions.append(sample.action) #no need to put into [] because it is already a vector
                if self.reward_max-self.reward_min == 0:
                    rewards.append([sample.reward])
                else:                
                    rewards.append([(sample.reward-self.reward_min)/(self.reward_max-self.reward_min)*2.0-1.0])
                #print((sample.reward-self.reward_min)/(self.reward_max-self.reward_min)*2.0-1.0)
                next_states.append(sample.next_state) #no need to put into [] because it is already a vector
            return minibatch(states,actions,rewards,next_states)
   
    def get_td_error_sorted_minibatch(self,batch_size):
            states = []
            rewards = []
            actions = []
            next_states = []
            self.sample_minibatch=[]
            
                        
            
            for i in range(batch_size):
                if random.uniform(0.0,1.0)<0.1:
                    index= random.randint(0, len(self.bests)-1)
                    sample = self.bests[index]
                    self.sample_minibatch.append((0,index))
                else:
#                    index= random.randint(0, self.current_size()-1)
                    index= np.random.choice(range(len(self.buffer)), p=self.distribution)
                    sample = self.buffer[index][1]
                    self.sample_minibatch.append((1,index))
                
                
                states.append(sample.state) #no need to put into [] because it is already a vector
                actions.append(sample.action) #no need to put into [] because it is already a vector
                if self.reward_max-self.reward_min == 0:
                    rewards.append([sample.reward])
                else:                
                    rewards.append([(sample.reward-self.reward_min)/(self.reward_max-self.reward_min)*2.0-1.0])
                #print((sample.reward-self.reward_min)/(self.reward_max-self.reward_min)*2.0-1.0)
                next_states.append(sample.next_state) #no need to put into [] because it is already a vector
            return minibatch(states,actions,rewards,next_states)
   
    def sort_buffer(self):
#        print self.buffer
        s = list(self.buffer).sort(reverse=True)
        self.buffer=  deque(s)
        
    def update_td_error(self,td_err):    
       for i in range(len(td_err)):   
           if self.sample_minibatch[i][0]==1:
               sample =  self.buffer[self.sample_minibatch[i][1]][1]
               self.buffer[self.sample_minibatch[i][1]]=(td_err[i][0],sample)
           