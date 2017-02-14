Content:

	architecture: Folder containing a visual description of the architecture of the first version of the TAE server.
	lexical_simplification_server: Folder containing the code for the local Lexical Simplification server of SIMPATICO.
	main_TAE_server: Folder containing the code for the TAE web server of SIMPATICO.
	resources.txt: File containing a map of resources to be used by the simplification servers of SIMPATICO.
	[carol] (ss folder, etc)

Installation instructions:

	1) In order to run the servers, you will first need to install the following Python 2 libraries:

		urllib2
		kenlm
		gensim
		nltk
		sklearn
		keras
		numpy
		pickle
		[carol] (mais libraries?)
	
	2) Download or clone the code from https://github.com/SIMPATICOProject/SimpaticoTAEServer onto a folder of choice (ex: /home/user/SimpaticoTAEServer).
	
	3) Download the data pack from http://www.quest.dcs.shef.ac.uk/simpatico/simplifier_data.tar.gz and unpack it into the root folder of the code (ex: resulting in /home/user/SimpaticoTAEServer/data). These are the files referenced in the "resources.txt" file.
	
	4) Download the Stanford Tagger (full) from http://nlp.stanford.edu/software/stanford-postagger-full-2015-04-20.zip and unpack it into a folder of choice (ex: /home/user/stanford-postagger-full-2015-04-20).
	
	5) [carol] Download the Stanford Parser from...

Running instructions:

	1) In order to run a fully functional version of the SIMPATICO TAE server, you will have to run xxx components:
	
		- The Stanford Tagger server for English
		- The Stanford Parser servers for English and Galician [carol]
		- The Lexical Simplification local server
		- The Syntactic Simplification local server
		- The main TAE web server
		
	2) How to run the Stanford Tagger server for English:
	
		Go to the folder where you unpacked the Stanford Tagger and run the following command:
		
			java -mx2G -cp "*:lib/*:models/*" edu.stanford.nlp.tagger.maxent.MaxentTaggerServer -model ./models/wsj-0-18-bidirectional-distsim.tagger -port 2020 &
			
		Then you will have a tagging server running at port 2020. The port chosen must be the one specified on the "configurations.txt" file.