#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  4 14:46:30 2017

@author: pnbrown
"""

full_vote_time = 30*60

def voteTimeThrottle(votetime) :
    # returns a multiplier between 0 and 1 that is
    # normalized weight per contributed rshares due to vote timing
    return min(1.0,votetime/full_vote_time)
    
def vshares(R,sim) :
    return (R+sim.S)*(R+sim.S) - (sim.S)**2

class Post :
    def __init__(self,ID,sim,votes=[],rshares=0,rshares2=0,total_weight=0) :
        self.id = ID
        self.votes = votes
        self.rshares = rshares
        self.rshares2 = rshares2
        self.total_weight = total_weight
        self.sim = sim
        self.current_payout = 0
        
    def _vote(self,new_rshares=1e6,votetime=full_vote_time) :
        self.votes.append(Vote(votetime,new_rshares,self))
        self.rshares += new_rshares
        self.total_weight += self.votes[-1]._nominal_weight
        self.rshares2 = vshares(self.rshares,self.sim)
        
        
class Vote :
    def __init__(self,votetime,this_rshares,post) :
        self.votetime=votetime
        self.rshares = this_rshares
        self.postid = post.id
        timeThrot = voteTimeThrottle(votetime)
        R = post.rshares
        B = post.sim.B
        S = post.sim.S
        startWeight = int(B*R/(R+2*S))
        endWeight = int(B*(R+this_rshares)/(R+this_rshares+2*S))
        nominal_weight = endWeight-startWeight
        true_weight = int(timeThrot*nominal_weight)
        self.weight = true_weight
        self._nominal_weight = nominal_weight
        

class SteemSim :
    S = 2e12
    B = 2 ** 64 - 1
    
    def __init__(self,posts=[]) :
        # posts is either list of Post objects or integer number of posts to add
        if isinstance(posts,list) :
            self.posts = posts
        else :
            self.posts = []
            for i in range(0,posts) :
                self.addPost()
        self.total_rshares2 = 0
        self.rewardpool = 100
    
    def addPost(self,num=None) :
        if not num :
            new_id = len(self.posts)
            self.posts.append(Post(new_id,self))
            
    def vote(self,postid,rshares=1e6,votetime=full_vote_time) :
        old_post_rshares2 = self.posts[postid].rshares2
        self.posts[postid]._vote(rshares,votetime)
        self.total_rshares2 += self.posts[postid].rshares2-old_post_rshares2
        self._update_rewards()
        
    def _update_rewards(self) :
        for post in self.posts :
            post.current_payout = post.rshares2/self.total_rshares2*self.rewardpool
            
            
    