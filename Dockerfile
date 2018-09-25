FROM ubuntu:18.04

RUN apt-get update && \
    apt-get install -y openjdk-8-jdk &&\
    apt-get install -y python-pip python3-pip &&\
    apt-get install -y supervisor &&\
    apt-get clean

RUN pip install --upgrade pip

RUN mkdir -p /var/log/supervisor

RUN pip install kenlm &&\
    pip install gensim &&\
    pip install nltk==3.2.5 &&\
    pip install sklearn &&\
    pip install keras &&\
    pip install numpy &&\
    pip install h5py &&\
    pip install tensorflow===1.3.0 &&\
    pip install langdetect &&\
    pip install pexpect &&\
    pip install unidecode &&\
    pip install grammar_check
WORKDIR /app
COPY . /app

# fix sources relative to nltk v3.2.5
RUN sed -i -e 's/from nltk.tokenize/from nltk.tokenize.stanford/' syntactic_simplification_server/simpatico_ss/simpatico_ss/simplify.py
RUN sed -i -e 's/from nltk.tokenize/from nltk.tokenize.stanford/' syntactic_simplification_server/simpatico_ss/simpatico_ss_es/simplify.py
RUN sed -i -e 's/from nltk.tokenize/from nltk.tokenize.stanford/' syntactic_simplification_server/simpatico_ss/simpatico_ss_gl/simplify.py
RUN sed -i -e 's/from nltk.tokenize/from nltk.tokenize.stanford/' syntactic_simplification_server/simpatico_ss/simpatico_ss_it/simplify.py

# copy resource file
COPY ./docker-configs/resources.txt /app/resources.txt
COPY ./docker-configs/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8080 2020 3030 4040 5050 1414 1515

CMD ["/usr/bin/supervisord"]
