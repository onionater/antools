# -*- coding: utf-8 -*-
"""
Created on Thu Mar 27 13:06:37 2014

@author: amyskerry
"""

##make new table for NDE_dim2
#tablename='NDE_dims2'
#emos=['Guilty', 'Content', 'Lonely', 'Excited', 'Hopeful', 'Devastated', 'Proud', 'Apprehensive', 'Disgusted', 'Embarrassed', 'Jealous', 'Joyful', 'Impressed', 'Grateful', 'Terrified', 'Furious', 'Nostalgic', 'Disappointed', 'Annoyed', 'Surprised', 'Neutral']
#dimensions=['expectedness', 'pleasantness', 'goal_consistency', 'fairness', 'agent_cause', 'agent_intention', 'self_cause', 'close_others', 'control', 'altering', 'moral', 'selfesteem', 'suddenness', 'familiarity', 'future', 'past', 'occurred', 'certainty', 'repetition', 'coping', 'mental_states', 'others_knowledge', 'bodily_disease', 'people', 'relevance', 'freedom', 'pressure', 'consequences', 'danger', 'self_involvement', 'main_character', 'remember', 'self_consistency', 'relationship_influence', 'agent_situation', 'attention', 'psychological_change', 'safey', 'knowledge_change', 'emotion']
#createtablestring='CREATE TABLE '+ tablename +'(subjid varchar(20), rownum int(11) NOT NULL AUTO_INCREMENT, primary key (rownum), submission_date DATE,'
#for dimen in dimensions:
#    qdim=dimen+ ' varchar(20),'
#    qdimlabel=dimen+'_qlabel'+ ' varchar(20),'
#    qdimemo=dimen+'_qemo'+ ' varchar(20),'
#    createtablestring=createtablestring+qdim+qdimemo+qdimlabel
#for emo in emos:
#    qemo=emo+ '_extent int(11),'
#    createtablestring=createtablestring+qemo
#createtablestring=createtablestring+'city varchar(50), country varchar(50), age varchar(20), gender varchar(20), thoughts varchar(500),'
#createtablestring=createtablestring+'response_noface int(11), response_intune int(11), response_nothought int(11),  response_needverbal int(11), response_facevoice int(11), response_surprised int(11));'

#tbale for NDE_dim2_control
tablename='NDE_dims2_control'
emos=['Guilty', 'Content', 'Lonely', 'Excited', 'Hopeful', 'Devastated', 'Proud', 'Apprehensive', 'Disgusted', 'Embarrassed', 'Jealous', 'Joyful', 'Impressed', 'Grateful', 'Terrified', 'Furious', 'Nostalgic', 'Disappointed', 'Annoyed', 'Surprised', 'Neutral']
dimensions=['main_character', 'emotion', 'valence', 'arousal', 'afraid_dim', 'happy_dim', 'sad_dim', 'angry_dim']
createtablestring='CREATE TABLE '+ tablename +'(subjid varchar(20), rownum int(11) NOT NULL AUTO_INCREMENT, primary key (rownum), submission_date DATE,'
for dimen in dimensions:
    qdim=dimen+ ' varchar(20),'
    qdimlabel=dimen+'_qlabel'+ ' varchar(20),'
    qdimemo=dimen+'_qemo'+ ' varchar(20),'
    createtablestring=createtablestring+qdim+qdimemo+qdimlabel
for emo in emos:
    qemo=emo+ '_extent int(11),'
    createtablestring=createtablestring+qemo
createtablestring=createtablestring+'city varchar(50), country varchar(50), age varchar(20), gender varchar(20), thoughts varchar(500),'
createtablestring=createtablestring+'response_noface int(11), response_intune int(11), response_nothought int(11),  response_needverbal int(11), response_facevoice int(11), response_surprised int(11));'
