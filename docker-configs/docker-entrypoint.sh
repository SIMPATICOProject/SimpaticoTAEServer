#!/bin/bash

cd /app/data/stanford-postagger-full-2015-04-20;
java -mx2G -cp "*:lib/*:models/*" edu.stanford.nlp.tagger.maxent.MaxentTaggerServer -model ../data/english.tagger -port 2020 & 
java -mx2G -cp "*:lib/*:models/*" edu.stanford.nlp.tagger.maxent.MaxentTaggerServer -model ../data/spanish.tagger -port 3030 &
java -mx2G -cp "*:lib/*:models/*" edu.stanford.nlp.tagger.maxent.MaxentTaggerServer -model ../data/galician.tagger -port 4040 &
java -mx2G -cp "*:lib/*:models/*" edu.stanford.nlp.tagger.maxent.MaxentTaggerServer -model ../data/italian.tagger -port 5050 &

cd /app/lexical_simplification_server;
nohup python -u Run_TCP_Lexical_Simplifier_Server.py &
cd /app/syntactic_simplification_server;
python -u Run_TCP_Syntactic_Simplifier_Server.py
