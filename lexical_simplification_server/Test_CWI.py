from lib import *
import shelve

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

configurations = loadResources('../configurations.txt')
resources = loadResources('../resources.txt')

freq_map = shelve.open(resources['eng_sub_shelf'], protocol=pickle.HIGHEST_PROTOCOL)
mean_freq = float(resources['eng_mean_freq'])
std_freq = float(resources['eng_std_freq'])
min_proportion = float(resources['eng_min_proportion'])
cwi = EnglishComplexWordIdentifier(freq_map, mean_freq, std_freq, min_proportion)

targets = ['domestic', 'addressed', 'liable', 'discounts', 'exemptions', 'severely', 'jointly', 'separately']

for target in targets:
	simp = cwi.getSimplifiability(target)
	print target, simp
