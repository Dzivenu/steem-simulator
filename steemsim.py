#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  4 14:46:30 2017

@author: pnbrown
"""

class Post :
    def __init__(self,ID,votes=[],rshares=0,rshares2=0) :
        self.id = ID
        self.votes = votes
        self.rshares = rshares
        self.rshares2 = rshares2

class SteemSim :
    def __init__(self,posts=[]) :
        # posts is either list of Post objects or integer number of posts to add
        if isinstance(posts,list) :
            self.posts = posts
        else :
            self.posts = []
            for i in range(0,posts) :
                self.addPost()
    
    def addPost(self,num=None) :
        if not num :
            new_id = len(self.posts)
            self.posts.append(Post(new_id))
            