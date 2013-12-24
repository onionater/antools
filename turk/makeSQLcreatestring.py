# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 10:44:24 2013

@author: amyskerry
"""
#make new table for NDE_dim
tablename='NDE_dims'
dimensions=['expectedness', 'pleasantness', 'goal_consistency', 'fairness', 'agent_cause', 'agent_intention', 'self_cause', 'close_others', 'control', 'fixing', 'moral', 'confidence', 'suddenness', 'familiarity', 'past_present', 'certainty', 'coping', 'mental_states', 'others_knowledge', 'bodily_disease', 'people', 'relevance', 'freedom', 'pressure', 'consequences', 'safety', 'self_involvement', 'main_character', 'emotion']
createtablestring='CREATE TABLE '+ tablename +'(subjid varchar(20), rownum int(11) NOT NULL AUTO_INCREMENT, primary key (rownum), submission_date DATE,'
for dimen in dimensions:
    qdim=dimen+ ' varchar(20),'
    qdimlabel=dimen+'_qlabel'+ ' varchar(20),'
    qdimemo=dimen+'_qemo'+ ' varchar(20),'
    createtablestring=createtablestring+qdim+qdimemo+qdimlabel
createtablestring=createtablestring+'city varchar(50), country varchar(50), age varchar(20), gender varchar(20), thoughts varchar(500));'


## just to make a new table for NDE
#tablename='NDE_table'
#createtablestring='CREATE TABLE '+ tablename +'(subjid varchar(20), rownum int(11) NOT NULL AUTO_INCREMENT, primary key (rownum), submission_date DATE,'
#for q in range(88):
#    newq= 'q'+str(q)+ ' varchar(20),'
#    newqanswer='correctA'+str(q)+ ' varchar(20),'
#    newqother1= 'q'+str(q)+'otherword1 varchar(20),'
#    newqother2= 'q'+str(q)+'otherword2 varchar(20),'
#    createtablestring=createtablestring+newq+newqanswer+newqother1+newqother2
#createtablestring=createtablestring+'city varchar(50), country varchar(50), age varchar(20), gender varchar(20), thoughts varchar(500));'
    