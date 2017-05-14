MUSST: multilingual syntactic simplification tool

Content:

	syntactic_simplification_server: Folder containing the code for the local MUSST server.
	resources.txt: File containing a map of resources to be used by the simplification servers.
	configurations.txt: File containing port configurations for the servers.

Installation instructions:

	1) In order to run the servers, you will need a Python 2.6+ installation (preferably Anaconda), and a Java 1.8+ installation.

	2) Install the following Python 2 libraries:

		kenlm
		sklearn
		numpy
		grammar-check
		scipy
	
	3) Download or clone the code from https://github.com/SIMPATICOProject/SimpaticoTAEServer/tree/emnlp2017-demo/ onto a folder of choice (ex: /home/user/SimpaticoTAEServer).
	
	4) Download the data pack from https://www.dcs.shef.ac.uk/people/C.Scarton/resources/emnlp2017_demo_data.tar.gz and unpack it into the root folder of the code (ex: resulting in /home/user/SimpaticoTAEServer/data). These are the files referenced in the "resources.txt" file.
	
	5) The version 3.7.0 of the Stanford CoreNLP is already available in the data pack. 
		- However, if you want to use a different version, you can download from http://stanfordnlp.github.io/CoreNLP/. In this case you will need to change the path to your CoreNLP version into the resources.txt file (corenlp_dir parameter).

Running instructions:

* You can run MUSST locally:

	Navigate to the "syntactic_simplification_server/simpatico_ss" folder.
	
	Usage: __main__.py [-h] [-l {en,it,es}] [-d D] [-comp] [-conf]
	
	optional arguments:
  		-h, --help     show this help message and exit
  		-l {en,it,es}  language
  		-d D           document to be simplified (with one sentence per line)
  		-comp          use the complexity checker sentence selection
  		-conf          use the confidence model
		
	Example of usage for English:
	
	python __main__.py -l en -d ../tests/examples.en -comp -conf
	
	(Please note that the confidence model is only applied for English.)
	
* You can run MUSST as a server:

	1) In order to run a fully functional version of the MUSST, you will have to run the following components:
	
		- The Stanford Dependency Parser servers: Receives requests from the Syntactic Simplification local server for parsing.
		- The Syntactic Simplification local server: Receives requests from the main TAE web server for syntactic simplifications.
		
		
	2) How to run the Stanford parser servers:
	
		These servers are run when the syntactic simplifier server is started, therefore, there is no need to run them externally.
	
		
	3) How to run the Syntactic Simplification local server:
	
		Navigate to the "syntactic_simplification_server" folder, then run the following command:
		
			nohup python Run_TCP_Syntactic_Simplifier_Server.py &
			
		Then you will have a server receiving requests at the "ss_local_server_port" port specified in the "configurations.txt" file.
	
		
	Testing instructions:
		
	1) How to test the Syntactic Simplification local server:
		Navigate to the "syntactic_simplification_server/tests" folder, then run the following commands:
			
			python English_Test_Simplifier.py
			python Italian_Test_Simplifier.py
			python Spanish_Test_Simplifier.py
			
		You should receive responses with simplifications after a few seconds.
		You can also open the aforementoined scripts to see how they work.
