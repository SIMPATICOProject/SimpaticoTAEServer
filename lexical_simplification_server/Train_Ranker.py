import sys
import numpy as np
from lexenstein.features import *
from lib import *
import pickle

def loadResources(path):
        #Open resource file:
        f = open(path)

        #Create resource map:
        resources = {}

        #Read resource paths:
        for line in f:
                data = line.strip().split('\t')
                if data[0] in resources:
                        print 'Repeated resource name: ' + data[0] + '. Please change the name of this resource.'
                resources[data[0]] = data[1]
        f.close()

        #Return resource database:
        return resources

def getAgesList():
	res = set([])
	for i in range(0, 151):
		label = getAgeBand(i)
		res.add(label)
	return res

def getCountryList(configurations):
	url = 'http://'+configurations['main_upm_server_host']+':'+configurations['main_upm_server_port']
	url += '/?request_type=request_countries'
	content = urllib2.urlopen(url).read().strip()
	countries = [c[1] for c in json.loads(content)['target'][0]]
	countries = set(countries)
	return countries

def getLanguagesList(configurations):
	url = 'http://'+configurations['main_upm_server_host']+':'+configurations['main_upm_server_port']
	url += '/?request_type=request_lang'
	content = urllib2.urlopen(url).read().strip()
	languages  = [c[1] for c in json.loads(content)['target'][0]]
	languages = set(languages)
	return languages

def getProficienciesList():
	return set(['A1','A2','B1','B2','C1','C2'])

def getEducationList():
	return set(['primary','secondary','undergraduate','postgraduate'])

def getDisabilitiesList():
	return set(['physical','visual','hearing','mental','intellectual','learning'])

def getFamiliarityList():
	return set(['basic','intermediate','advanced'])

def getDemoData(path):
	dataset = [line.strip().split('\t') for line in open(path)]
	result = []
	for data in dataset:
		age = [getAgeBand(int(data[0]))]
		countries = ['NULL']
		languages = [data[1]]
		proficiency = [data[5]]
		education = [data[4].lower()]
		disability = ['NULL']
		familiarity = ['NULL']	
		newline = [age, countries, languages, proficiency, education, disability, familiarity]
		result.append(newline)
	return result

def getDatabaseData(configurations):
	url = 'http://'+configurations['main_upm_server_host']+':'+configurations['main_upm_server_port']
	url += '/?request_type=request_demo_data_all'
	content = unicode(urllib2.urlopen(url).read().strip())
	demoinfo = json.loads(content)['target'][0]
	demomap = {}
	for line in demoinfo:
		id = line[0]
		age = [getAgeBand(line[1])]
		countries = [line[8]]
		languages = line[9:]
		proficiency = [line[3]]
		education = [line[4]]
		disability = [line[5]]
		familiarity = [line[6]]
		infoline = [age, countries, languages, proficiency, education, disability, familiarity]
		demomap[id] = infoline
	
	url = 'http://'+configurations['main_upm_server_host']+':'+configurations['main_upm_server_port']
	url += '/?request_type=request_inter_data_all&inter_type=lexical'
	content = unicode(urllib2.urlopen(url).read().strip())
	simplifications = json.loads(content)['target'][0]
	simpdata = []
	for simp in simplifications:
		sentence = simp[3].strip()
		index = simp[4].strip()
		target = simp[1].strip()
		sub = simp[2].strip()
		feedback = simp[5]
		if feedback==1:
			aux = [target, sub]
		else:
			aux = [sub, target]
		newinstance = [sentence, aux[0], index, '0:'+aux[1]]
		simpdata.append(newinstance)
	demoids = [simp[-1] for simp in simplifications]
	demodata = [demomap[id] for id in demoids]

	return simpdata, demodata

configurations = loadResources('../configurations.txt')
resources = loadResources('../resources.txt')

ages = getAgesList()
countries = getCountryList(configurations)
languages = getLanguagesList(configurations)
proficiencies = getProficienciesList()
educations = getEducationList()
disabilities = getDisabilitiesList()
familiarities = getFamiliarityList()

fages = OneHotFarm()
fcountries = OneHotFarm()
flanguages = OneHotFarm()
fproficiencies = OneHotFarm()
feducations = OneHotFarm()
fdisabilities = OneHotFarm()
ffamiliarities = OneHotFarm()

fages.addLabels(ages)
fcountries.addLabels(countries)
flanguages.addLabels(languages)
fproficiencies.addLabels(proficiencies)
feducations.addLabels(educations)
fdisabilities.addLabels(disabilities)
ffamiliarities.addLabels(familiarities)

fe = FeatureEstimator(norm=True)
fe.addCollocationalFeature(resources['eng_sub_lm'], 2, 2, 'Simplicity')

df = DemographicFeatureFarm(fages, fcountries, flanguages, fproficiencies, feducations, fdisabilities, ffamiliarities)

#Get data from dataset:
simpdata_dataset = [line.strip().split('\t') for line in open(resources['eng_ls_dataset_nodemo'])]
demodata_dataset = getDemoData(resources['eng_ls_dataset_withdemo'])

#Get data from the database:
simpdata_database, demodata_database = getDatabaseData(configurations)

#Join data:
simpdata = simpdata_dataset + simpdata_database
demodata = demodata_dataset + demodata_database

ranker = SIMPATICORidgeRegressionRanker(fe, df)
ranker.trainRegressionModel(simpdata, demodata)

filehandler = open(resources['eng_ranker_model'], 'w')
pickle.dump(ranker.model, filehandler)
filehandler.close()

filehandler = open(resources['eng_ranker_demofarm'], 'w')
pickle.dump(ranker.demofarm, filehandler)
filehandler.close()

#filehandler = open(resources['eng_ranker_model'], 'r')
#ranker.model = pickle.load(filehandler)
#filehandler.close()

#filehandler = open(resources['eng_ranker_demofarm'], 'r')
#ranker.demofarm = pickle.load(filehandler)
#filehandler.close()

#ranker.trainRegressionModel(simpdata, demodata)
