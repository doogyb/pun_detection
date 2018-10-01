
# coding: utf-8

# In[11]:


import json
from src.data_processing import print_progress

def ranked_vectors(path):
    subs = []
    for index in range(1780):
        print_progress(index, 1780)
        full_path = "results/{}/{}".format(path, index)
        with open(full_path) as f:
            subs.append(json.load(f))
    return subs


# In[12]:


def number_of_substitutions(index, subs):
    tot_sum = 0
    for k, v in subs[index].items():
        tot_sum += len(v)
    return tot_sum


# In[13]:


def generate_ranked_vector(index, mvl, subs):
    vec = [0] * mvl
    scores = []
    for k, v in subs[index].items():
        scores.extend([score[1] for score in v])
    vec[:len(scores)] = list(sorted(scores, reverse=True))
    
    return vec


# In[14]:


import numpy as np


# Load the vectors, dump as binary

# In[15]:


locations = (['phonetic_filter_no_pos',
              'phonetic_filter_with_pos',
              'all_trigram_no_pos',
              'all_trigram_with_pos'])


# In[16]:


# max_columns = 10000
# for p in locations:
    
#     subs = ranked_vectors(p)
#     max_vector_length = (min(max(number_of_substitutions(i, subs) 
#                              for i in range(1780)),
#                              max_columns)) 
    
#     vectors = ([generate_ranked_vector(i, max_vector_length, subs) 
#                 for i in range(1780)])
#     X = np.array(vectors)
#     with open('vectors/{}.np'.format(p), 'wb') as f:
#         np.save(f, X)


# In[17]:


from src.data_processing import load_data
task1, task2, task3, min_pairs, strings, pun_strings = load_data()


# In[18]:


with open("vectors/phonetic_filter_with_pos.np", 'rb') as f:
    X = np.load(f)


# In[19]:


y = np.array([int(context['pun']) for context in task1])


# In[20]:


# from sklearn.model_selection import KFold

# kf = KFold(n_splits=10)
# kf.get_n_splits(X)


# columns = 10
# from sklearn.metrics import classification_report
# for train_index, test_index in kf.split(X):
    
#     print(train_index)
#     X_train, X_test = X[train_index, :columns], X[test_index, :columns]
#     y_train, y_test = y[train_index], y[test_index]
    
#     clf = svm.SVC()
#     clf.fit(X_train, y_train)
#     print(classification_report(y_test, clf.predict(X_test)))
#     input()   


# In[ ]:


from sklearn.model_selection import cross_val_score
from sklearn import svm
examples = 333

clf = svm.SVC(kernel='poly', verbose=True)
scores = cross_val_score(clf, X[:examples, :3], y[:examples,], cv=3)


# In[22]:


print(scores)

