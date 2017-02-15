# simpatico_ss
Syntactic Simplification for the SIMPATICO project.

This system implements the syntactic simplification rules proposed by Siddharthan (2004) and Siddharthan and Angrosh (2014).
Our implementation uses the Stanford Dependency Parser available at CoreNLP (http://stanfordnlp.github.io/CoreNLP/).
The Dependency parser is initialised as a server using the code available at https://github.com/Wordseer/stanford-corenlp-python (please refer to this for the specific license).

-----------------------------------------------------------------------
## First Release

This release deals with the simplification of conjoint clauses, relative clauses, appositive phrases and passive voice for the English language.
We also support the simplification of appositive phrases and passive voice for Galician.
Simplifications are made according to the parser tree output, given priority to the relations that are in the top of the tree.
Sentences are simplified recursively until there is nothing more to be simplified.

-----------------------------------------------------------------------
## External Resources/Tool

**English**
Apart from the CoreNLP server code, we also use two external libraries:

1. NodeBox (https://www.nodebox.net/code/index.php/Linguistics#verb_conjugation)
2. Truecaser (https://github.com/nreimers/truecaser)

Such libraries are embedded in this code, but please refer to their licenses before using them. 

For the truecaser a model file .obj is required. Please download the English pre-trained model from https://github.com/nreimers/truecaser/releases and unzip the file on the truecaser folder. You can also train your own truecaser model following the instructions provided in https://github.com/nreimers/truecaser.

**Galician**
You need to download the pre-trained truecase model, dependency parser and POS tagger for Galician:

1. Truecase model (https://www.dcs.shef.ac.uk/people/C.Scarton/resources/distributions.gl.obj) - please place this model into the truecase folder
2. POS tagger (https://www.dcs.shef.ac.uk/people/C.Scarton/resources/galician.tagger)
3. Dependency parser (https://www.dcs.shef.ac.uk/people/C.Scarton/resources/galician.nndep.model.txt.gz)

**Spanish**

You need the Stanford Parser model for Spanish (http://nlp.stanford.edu/software/stanford-spanish-corenlp-2016-10-31-models.jar)

-----------------------------------------------------------------------
## How to run

`python __main__.py [-l {en,gl}] [-d Document]`

The path for the Stanford CoreNLP tool should be changed in simpatico_ss/util.py before use.
The systems also expect a file called 'distributions.obj' in the truecaser folder for English or a file called 'distributions.gl.obj' for Galician. Please use the instructions in External Resources/Tool section.

For Galician, you will also need to place the right path to the POS tagger and Dependency Parser in the 'galician.myproperties.properties'.

-----------------------------------------------------------------------
## Notes about Galician

The dependency parser and POS tagger were trained using the training environment provided by Stanford (dependency parser: http://nlp.stanford.edu/software/nndep.shtml - POS tagger: http://www-nlp.stanford.edu/software/pos-tagger-faq.shtml#train).

The verb conjugation available in the 'gl/' folder is based on the verb conjugation model of NodeBox and uses the lexical resources made available by the Linguakit project (https://github.com/citiususc/Linguakit).


-----------------------------------------------------------------------
## Notes about Spanish

The verb conjugation available in the 'es/' folder is based on the verb conjugation model of NodeBox and uses the lexical resources made available by the Linguakit project (https://github.com/citiususc/Linguakit).

-----------------------------------------------------------------------

**References**

Siddharthan, A. (2004): Syntactic Simplification and Text Cohesion. PhD Thesis, November 2003 OR Technical Report TR-597, University of Cambridge, August 2004. 

Siddharthan, A. and  Mandya, A. (2014): Hybrid text simplification using synchronous dependency grammars with hand-written and automatically harvested rules. Proceedings of the 14th Conference of the European Chapter of the Association for Computational Linguistics (EACL 2014), Gothenburg, Sweden. 
