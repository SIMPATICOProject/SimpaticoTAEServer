## Content:

	architecture: Folder containing a visual description of the architecture of the first version of the TAE server.
	lexical_simplification_server: Folder containing the code for the local Lexical Simplification server of SIMPATICO.
	syntactic_simplification_server: Folder containing the code for the local Syntactic Simplification server of SIMPATICO.
	main_TAE_server: Folder containing the code for the TAE web server of SIMPATICO.
	resources.txt: File containing a map of resources to be used by the simplification servers of SIMPATICO.
	configurations.txt: File containing port configurations for the servers.

## Installation instructions:

	1) In order to run the servers, you will need a Python 2.6+ installation (preferably Anaconda), and a Java 1.8+ installation.

	2) Install the following Python 2 libraries:

		kenlm
		gensim
		nltk
		sklearn
		keras
		numpy
		langdetect
		h5py
	
	3) Download or clone the code from https://github.com/SIMPATICOProject/SimpaticoTAEServer onto a folder of choice (ex: /home/user/SimpaticoTAEServer).
	
	4) Download the data pack from http://www.quest.dcs.shef.ac.uk/simpatico/simplifier_data.tar.gz and unpack it into the root folder of the code (ex: resulting in /home/user/SimpaticoTAEServer/data). These are the files referenced in the "resources.txt" file.
	
	5) Download the Stanford Tagger (full) from http://nlp.stanford.edu/software/stanford-postagger-full-2015-04-20.zip and unpack it into a folder of choice (ex: /home/user/stanford-postagger-full-2015-04-20).
	
	6) The version 3.7.0 of the Stanford CoreNLP is already available in the data pack. 
		- However, if you want to use a different version, you can download from http://stanfordnlp.github.io/CoreNLP/. In this case you will need to change the path to your CoreNLP version into the resources.txt file (corenlp_dir parameter).

## Running instructions:

	1) In order to run a fully functional version of the SIMPATICO TAE server, you will have to run the following components:
	
		- The Stanford Tagger server for English and Spanish: Receives requests from the Lexical Simplification local server for tagging.
		- The Stanford Dependency Parser servers: Receives requests from the Syntactic Simplification local server for parsing.
		- The Lexical Simplification local server: Receives requests from the main TAE web server for lexical simplifications.
		- The Syntactic Simplification local server: Receives requests from the main TAE web server for syntactic simplifications.
		- The main TAE web server: Receives requests from the web for Text Adaptation.
		
	2) How to run the Stanford Tagger servers for English and Spanish:
	
		Go to the folder where you unpacked the Stanford Tagger and run the following command:
		
			java -mx2G -cp "*:lib/*:models/*" edu.stanford.nlp.tagger.maxent.MaxentTaggerServer -model ./models/wsj-0-18-bidirectional-distsim.tagger -port 2020 &
			java -mx2G -cp "*:lib/*:models/*" edu.stanford.nlp.tagger.maxent.MaxentTaggerServer -model ./models/spanish-distsim.tagger -port 3030 &
			
		Then you will have a tagging servers running at ports 2020 and 3030. The ports chosen MUST be the ones specified on the "configurations.txt" file.
		
	3) How to run the Stanford parser servers:
	
		These servers are run when the syntactic simplifier server is started, therefore, there is no need to run them externally.
	
	4) How to run the Lexical Simplification local server:
	
		Navigate to the "lexical_simplification_server" folder, then run the following command:
			
			nohup python Run_TCP_Lexical_Simplifier_Server.py &
			
		Then you will have a server receiving requests at the "ls_local_server_port" port specified in the "configurations.txt" file.
		
	5) How to run the Syntactic Simplification local server:
	
		Navigate to the "syntactic_simplification_server" folder, then run the following command:
		
			nohup python Run_TCP_Syntactic_Simplifier_Server.py &
			
		Then you will have a server receiving requests at the "ss_local_server_port" port specified in the "configurations.txt" file.
	
	6) How to run the main TAE web server:
	
		Navigate to the "main_TAE_server" folder, then run the following command:
		
			nohup python Run_TAE_Simplification_Server.py &
		
		Then you will have a server receiving requests at the "main_tae_server_port" port specified in the "configurations.txt" file.
		
## Testing instructions:

	1) How to test the Stanford Tagger server:
	
		Go to the folder where you unpacked the Stanford Tagger and run the following command:
		
			java -cp stanford-postagger.jar edu.stanford.nlp.tagger.maxent.MaxentTaggerServer -client -port 2020
			
		Then just type a complete English sentence and press enter. The port chosen MUST be the one specified on the "configurations.txt" file.
			
	2) How to test the Lexical Simplification local server:
	
		Navigate to the "lexical_simplification_server/tests" folder, then run the following commands:
			
			python English_Test_Simplifier.py
			python Spanish_Test_Simplifier.py
			python Galician_Test_Simplifier.py
			python Italian_Test_Simplifier.py
			
		You should receive responses with simplifications after a few seconds.
		You can also open the aforementoined scripts to see how they work.
		
	3) How to test the Syntactic Simplification local server:
		Navigate to the "syntactic_simplification_server/tests" folder, then run the following commands:
			
			python English_Test_Simplifier.py
			python Galician_Test_Simplifier.py
			python Spanish_Test_Simplifier.py
			
		You should receive responses with simplifications after a few seconds.
		You can also open the aforementoined scripts to see how they work.
	
	4) How to test the main TAE web server:
	
		Navigate to the "main_TAE_server/tests" folder, then run the following commands:
		
			python Lexical_English_Test.py
			python Lexical_Spanish_Test.py
			python Lexical_Galician_Test.py
			python Lexical_Italian_Test.py
			python Syntactic_English_Test.py
			python Syntactic_Galician_Test.py
			python Syntactic_Spanish_Test.py
		
		Then you will have a server receiving requests at the "main_tae_server_port" port specified in the "configurations.txt" file.
		You can also test it from a web browser through URLs such as:
		
			http://<server_ip>:<main_tae_server_port>/?type=lexical&target=unorthodox&sentence=His%20fighting%20technique%20is%20very%20unorthodox%20.&index=5
			http://<server_ip>:<main_tae_server_port>/?type=lexical&target=collegamento&sentence=gestione%20dati%20del%20nucleo%20familiare%20in%20caso%20di%20casa%20famiglia%20(%20nucleo%20familiare%20)%20-%20da%20collegamento%20all’%20anagrafe%20.&index=16'
			http://<server_ip>:<main_tae_server_port>/?type=lexical&target=medran&sentence=Os%20líquens%20que%20medran%20no%20residuo%20asfáltico%20suxiren%20a%20sua%20.&index=3
			http://<server_ip>:<main_tae_server_port>/?type=syntactic&sentence=His%20fighting%20technique%20is%20very%20unorthodox%20.
			http://<server_ip>:<main_tae_server_port>/?type=syntactic&sentence=Os%20líquens%20que%20medran%20no%20residuo%20asfáltico%20suxiren%20a%20sua%20.
