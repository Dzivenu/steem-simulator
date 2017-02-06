#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  4 14:46:30 2017

@author: pnbrown
"""

full_vote_time = 30*60
curation_pct = 0.25

def voteTimeThrottle(votetime) :
    # returns a multiplier between 0 and 1 that is
    # normalized weight per contributed rshares due to vote timing
    return min(1.0,votetime/full_vote_time)
    
def weightForRshares(post_rshares,vote_rshares,sim) :
    R = post_rshares
    B = sim.B
    S = sim.S
    startWeight = int(B*R/(R+2*S))
    endWeight = int(B*(R+vote_rshares)/(R+vote_rshares+2*S))
    nominal_weight = endWeight-startWeight
    return nominal_weight
    
def vshares(R,sim) :
    return (R+sim.S)*(R+sim.S) - (sim.S)**2

class Post :
    def __init__(self,ID,sim,votes=None,rshares=0,rshares2=0,total_weight=0) :
        self.id = ID
        if votes is None :
            self.votes = []
        else :
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
        nominal_weight = weightForRshares(post.rshares,this_rshares,post.sim)
        true_weight = int(timeThrot*nominal_weight)
        self.weight = true_weight
        self._nominal_weight = nominal_weight
        self.naive_curation_reward = 0
        

class SteemSim :
    S = 2e12
    B = 2 ** 64 - 1
    
    def __init__(self,posts=None) :
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
            
    def check_curation_reward(self,postid,rshares=1e6,votetime=full_vote_time) :
        p = self.posts[postid]
        current_rshares = p.rshares
        current_weight = p.total_weight
        new_rshares = p.rshares+rshares
        nom_weight = weightForRshares(current_rshares,rshares,self)
        weight = voteTimeThrottle(votetime)*nom_weight
        wfrac = weight/(current_weight+nom_weight) # frac of post's weight that new vote gets
        # now compute new post payout
        new_rshares2 = vshares(new_rshares,self)
        new_total_reward = new_rshares2/(self.total_rshares2+new_rshares2-p.rshares2)*self.rewardpool # not right yet
        return wfrac*new_total_reward*curation_pct
        
    def vote(self,postid,rshares=1e6,votetime=full_vote_time) :
        p = self.posts[postid]
        old_post_rshares2 = p.rshares2
        p._vote(rshares,votetime)
        v = p.votes[-1]
        self.total_rshares2 += self.posts[postid].rshares2-old_post_rshares2
        self._update_rewards()
        v.naive_curation_reward = v.weight/p.total_weight*p.current_payout*curation_pct
        
        
    def _update_rewards(self) :
        for post in self.posts :
            post.current_payout = post.rshares2/self.total_rshares2*self.rewardpool
            
    def best_post_to_vote(self,rshares=1e6,votetime=full_vote_time) :
        next_curation = [self.check_curation_reward(i,rshares,votetime) for i in range(0,len(self.posts))]
        max_cur = max(next_curation)
        best_post = next_curation.index(max_cur)
        return best_post
        
    def vote_myopically(self,num_votes,rshares=1e6,votetime=full_vote_time) :
        payouts = []
        for i in range(int(num_votes)) :
            self.vote(self.best_post_to_vote(rshares,votetime),rshares,votetime)
            payouts.append([p.current_payout for p in self.posts])
        return payouts
        
    def payouts(self) :
        return [p.current_payout for p in self.posts]
        
    def curation_myopic(self,rshares=1e6,votetime=full_vote_time) :
        return [self.check_curation_reward(i,rshares,votetime) for i in range(len(self.posts))]