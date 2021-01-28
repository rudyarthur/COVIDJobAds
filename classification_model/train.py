from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.tree import DecisionTreeClassifier

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold
from sklearn.metrics import confusion_matrix, balanced_accuracy_score, plot_confusion_matrix, cohen_kappa_score

import matplotlib.pyplot as plt
import numpy as np
from zipfile import ZipFile
from collections import Counter
import json
from clean import *

import joblib

data = [];
labels = [];
with open("seeds.txt", 'r') as infile:
		for i,line in enumerate(infile):
			words = line.split()
			labels.append( words[1] )
			data.append( " ".join(words[3:]) )

test_pipe = Pipeline([
			('vectorizer', CountVectorizer( ngram_range=(1,2)  )),
			('classifier', DecisionTreeClassifier(random_state=0) ),
		]);

###########
##TESTING##
###########
print("training")
X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, random_state=33)

test_pipe.fit(X_train, y_train)
sa = test_pipe.score(X_test, y_test)
predicted_labels = test_pipe.predict(X_test)
ba = balanced_accuracy_score(y_test, predicted_labels)
ck = cohen_kappa_score(y_test, predicted_labels)
print( "Subset Accuracy: {:.3f}, Balanced Accuracy: {:.3f}, Cohen Kappa: {:.3f}".format( sa, ba, ck ) )

sectors = ['marketing', 'surveyor', 'assistant', 'physio', 'labourer', 'electrician', 'security', 'hr', 'vehicle', 'recruitment', 
'solicitor', 'project', 'storemanager', 'customer', 'garage', 'sale', 'property', 'teacher', 'nurse', 'care', 'software', 'engineer', 
'data', 'delivery', 'warehouse', 'hotel', 'cleaner', 'server', 'support', 'hgv', 'production', 'accountant', 'finance', 'account', 
'receptionist', 'business', 'administrator']

C = confusion_matrix(y_test, predicted_labels, sectors);
comps = {}
for i in range(len(C)):
	for j in range(i):
		print(C[i,j])
		if C[i,j] >= 1:
			comps[ (i,j) ] = C[i,j]
for p in sorted(comps, key=comps.get):
	print( sectors[p[0]], sectors[p[1]], comps[p] )

print( "total test", np.sum(C) );
print( "total wrong", sum(comps.values()) );
		
plot_confusion_matrix(test_pipe, X_test, y_test)  
plt.savefig('confusion.png')  



# save the model to
filename = 'topic_model.sav'

# Fit the model
pipe = Pipeline([
			('vectorizer', CountVectorizer( ngram_range=(1,2) ) ),
			('classifier', DecisionTreeClassifier(random_state=0) ),
		]);
print("fitting")
pipe.fit(data, labels)
joblib.dump(pipe, filename)

##make sure we can load the model
lpipe = joblib.load(filename)
 



num_classified = Counter();
unclassified = Counter();
numjobs = 0;
zip_file = ZipFile("/path/to/data.zip")
for k,f in enumerate(zip_file.namelist()):
	if k % 100 == 0: print(k)			
	with zip_file.open(f) as infile:  
		if f.split(".")[-1] != "json": continue;
		js = infile.read().decode('utf8')
		job = json.loads(js)
		if 'jobTitle' in job and job['jobTitle'] is not None:
			clean_doc = " ".join(tokenise(job['jobTitle']  + " " +  str_or_none(job['jobDescription'])))
			tag = lpipe.predict([clean_doc])
			numjobs += 1
			num_classified[ tag[0] ] += 1
			if tag == 'other':
				unclassified[ " ".join(tokenise(job['jobTitle'])) ] += 1

print(n, unclassified.most_common(40), sum(unclassified.values()) )
print(n, numjobs, sum(num_classified.values()))
print(n, num_classified, sum(unclassified.values())/numjobs )


			
