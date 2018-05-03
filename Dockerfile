FROM ubuntu:16.04

WORKDIR /app
COPY . /app

RUN apt-get update
# install jdk8
RUN apt-get install -y openjdk-8-jdk


# pip
RUN apt-get install -y python-pip
RUN pip install --upgrade pip

# python deps
RUN pip install kenlm
RUN pip install gensim
RUN pip install nltk==3.2.5 # to fix with correct version
RUN pip install sklearn
RUN pip install keras
RUN pip install numpy
RUN pip install h5py
RUN pip install tensorflow===1.3.0
RUN pip install langdetect
RUN pip install pexpect
RUN pip install unidecode

# fix sources relative to nltk v3.2.5
RUN cp docker-configs/fix_nltk_srcs/Run_TCP_Syntactic_Simplifier_Server.py syntactic_simplification_server/Run_TCP_Syntactic_Simplifier_Server.py
RUN cp docker-configs/fix_nltk_srcs/simpatico_ss/simplify.py syntactic_simplification_server/simpatico_ss/simpatico_ss/simplify.py
RUN cp docker-configs/fix_nltk_srcs/simpatico_ss_gl/simplify.py syntactic_simplification_server/simpatico_ss/simpatico_ss_gl/simplify.py

# copy resource file
RUN cp docker-configs/resources.txt /app/resources.txt
RUN chmod +x /app/docker-configs/docker-entrypoint.sh

CMD /app/docker-configs/docker-entrypoint.sh


