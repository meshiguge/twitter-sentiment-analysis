# TDM_TB_emot_stem.py
# Authors: Gerard Briones, Kasun Amarasinghe
# Creates the feature vector with unigrams for Task B, stemming and emoticon rentention are used in this version
# Further word saliency is added as well (TF-IDF)
# TAsk : Given a tweet and a topic, clasify it to positive or negative

import csv
import math
import dataCleaner_withStem

# data directory
data_path = 'data/'

# Arff file directory
arff_file_path = 'arff_data/'

# train data file name
data_file = 'data_taskB.tsv'

# Arff
arff_file = 'TB_emot_stem_tfidf.arff'

# all words and frequencies in the training directory
unigrams = {}

# holds the topics and number of tweets
topics = {}

# holds words with a pre defined frequency 
selected_unigrams = {}

# all tweet ids in the data set, stores the sentiment class as the value
tweet_ids = {}

# stores the tweet id and its topic
tweet_topic = {}

# predefined freq threshold
# the minimum frequency a word should appear in the tweet to be selected
freq_thresh = 5

# dicts to hold the sentiment classes that exist and number of elements in each class (training and testing)
sentiment_classes = {'positive':0, 'negative':0} 

# The training and testing TDM/ FV
# TDM - Term Document Matrix, FV - Feature Vector
tdm = {}
tdm_tfIdf = {}

# datareader (input_file, unigrams_dictionary,  tweetIDs_dictionary, SentimentClass_dictionary
# populating the unigrams dictionary
# collects all the unique words that exist in the training set
# these words are considered as the keywords in the feature vector
def dataReader(in_file_path, n_grams, tid_dict, topic_dict, topic_count_dict, sc_dict):
    with open(in_file_path, 'rb') as tsv_in:
        #create csv reader for the input file
        tsv_in = csv.reader(tsv_in, delimiter='\t')

        # File format
        # TweetID | Topic | Tweet | class (sentiment)
        for row in tsv_in:
            #print row
            tid = row[0]
            
            topic = row[1]
            tweet = row[2]
            if len(row)>3:
                
                sentiment = row[3]
                # only consider unique tweets
                if not tid in tid_dict:
                    if sentiment in sc_dict:
                        tid_dict[tid] = sentiment
                        sc_dict[sentiment] += 1
                     
                        # obtaining individual words from the tweet
                        # Special characters, numbers are removed and converted to lower case
                        # first step, removing special characters other than ones related to smileys 
                                               
                        words = dataCleaner_withStem.removeStopWords(dataCleaner_withStem.removeSpecialCharacters(dataCleaner_withStem.convertEmoticons(tweet)),1)
                        topic = dataCleaner_withStem.removeSpecialCharacters(topic)
                        topic_dict[tid] = topic;
                        if topic in n_grams:                       
                            for token in words:
                                if token in n_grams[topic]:
                                    n_grams[topic][token] +=1
                                else:
                                    n_grams[topic][token] = 1
                                    
                        else:
                             n_grams[topic] = {}
                             for token in words:
                                if token in n_grams[topic]:
                                    n_grams[topic][token] +=1
                                else:
                                    n_grams[topic][token] = 1
                                
                        if topic in topic_count_dict:
                            topic_count_dict[topic] += 1
                        else:
                            topic_count_dict[topic] = 1

# Extracts the words with higher frequency than the threshold
# Reduces the sparseness of the matrix
def chooseFrequentWords (n_grams, selected_n_grams, freq):
    # removing words which appear less than the frequency    
    #selected_n_grams = {x:v for (x,v)  in n_grams.items() if v > freq}
    for topic in n_grams:
        for word in n_grams[topic]:
            #print n_grams[word]
            value = n_grams[topic][word]
            if value > freq:
                if topic in selected_n_grams:
                    selected_n_grams[topic][word] = value
                else:
                    selected_n_grams[topic] = {}
                    selected_n_grams[topic][word] = value

# creates the feature vector from the extracted data
def createFV(in_file_path, selected_n_grams, tdm_dict, tid_dict, sc_dict):
    with open(in_file_path, 'rb') as tsv_in:
        # Initializing the TDM (list of dictionaries)
        for tid in tid_dict:
            tdm_dict[tid] = {}
            for topic in selected_n_grams:
                for token in selected_n_grams[topic]:
                    tdm_dict[tid][token] = 0
        
        #create csv reader for the input file
        # TweetID | Topic | Tweet | class (sentiment)
        tsv_in = csv.reader(tsv_in, delimiter='\t')
        for row in tsv_in:
            tid = row[0]
           # topic = row[1]
            tweet = row[2]
            if len(row)>3:
                words = dataCleaner_withStem.removeStopWords(dataCleaner_withStem.removeSpecialCharacters(dataCleaner_withStem.convertEmoticons(tweet)),1)
                #topic = dataCleaner.removeSpecialCharacters(topic)
                
                #words = dataCleaner.removeStopWords(dataCleaner.removeSpecialCharacters(tweet), 1)
                if tid in tid_dict:
                    for topic in selected_n_grams:
                        for token in selected_n_grams[topic]:
                            if token in words:                                
                                    tdm_dict[tid][token]+=1

# performs the TFIDF enhancement on the TDM 
def tfIDF(selected_n_grams, tid_dict, tdm_dict, tdm_dict_tfidf):
    
    doc_freq = {} # holds the number of tweets that words occur in
    tf = {} # holds the term frequency value for each word 
    idf = {} # holds the idf 
    words = {} # holds the number of words in each tweet
    
    #print tdm_dict
    #for token in selected_n_grams:
        #doc_freq[token] =  0
    
    # counting the frequency of occurance for each word and calculating TF for each word
    for tid in tid_dict:
        for topic in selected_n_grams:
            for token in selected_n_grams[topic]:
                if(tdm_dict[tid][token]>0):
                    #print tid
                    if token in doc_freq:
                        doc_freq[token]+=1
                    else:
                        doc_freq[token] = 1
                        
                    if tid in words:
                        words[tid] += 1
                    else:
                        words[tid] = 1
      
    #calculating Term frequency
    for tid in tid_dict:
        tf[tid] = doc_freq
        tf[tid] = {x:0 for (x,v)  in tf[tid].items()}
        for token in doc_freq:
            if tid in words:
                tf[tid][token] = float(tdm_dict[tid][token])/float(words[tid])
            
    #Calculating inverse document frequency
    idf = doc_freq
    idf = {x:0 for (x,v)  in idf.items()}
    for token in doc_freq:
        idf[token] = math.log(float(len(tid_dict))/float(doc_freq[token]))
        
    #tdm_dict_tfidf = tdm_dict
     
    # final tf-idf 
    for tid in tid_dict:
        tdm_dict_tfidf[tid] = tdm_dict[tid]
        tdm_dict_tfidf[tid] = {x:0 for (x,v)  in tdm_dict_tfidf[tid].items()}
        for topic in selected_n_grams:
            for token in selected_n_grams[topic]:
                tdm_dict_tfidf[tid][token] = tf[tid][token] * idf[token]
   
    
# writes the created feature vector to a file
def writeFVtoARFF(out_file_path, selected_n_grams, tdm_dict, tid_dict, topic_dict, sc_dict, header):
    # creating the Training ARFF file
    fp = open(out_file_path, 'w')
    fp.write("@RELATION\t"+header+"\n")

    counter = 1
    for topic in selected_n_grams:
        for words in selected_n_grams[topic].keys():
            fp.write("@ATTRIBUTE\t"+str(counter)+"_"+str(words)+"\tREAL\n")
            counter +=1
    
    fp.write("@ATTRIBUTE\ttopic\t{")
    counter = 0
    for topic in selected_n_grams:
        if (counter < len(topics)-1):
            tw = topic.split()
            for t in tw:
                fp.write(t)
            fp.write(',')
        else:
            fp.write(topic)
            
    fp.write('}\n')
          
    fp.write("@ATTRIBUTE\tclass\t{")
    counter = 0
    for st in sc_dict:
        if(counter<len(sc_dict.keys())-1):
        # Objective tweets are considered as neutral         
            if st != 'objective':
                fp.write(st)
                fp.write(',')
        else:
            fp.write(st)
        counter+=1
    fp.write('}\n')
    fp.write("\n")
    fp.write("@DATA\n")

    for tid in tid_dict:
        for topic in selected_n_grams:
            for token in selected_n_grams[topic]:
                fp.write(str(tdm_dict[tid][token])+",")
        
        tw = tweet_topic[tid].split()
        for t in tw:
                fp.write(t)
                
        fp.write(',')
        fp.write(tid_dict[tid])
        fp.write("\n")
    
    fp.close()

def getStats(n_grams, tid_dict, selected_n_grams, sc_dict):
    print 'Number of tweets: '
    print len(tid_dict)
    print '\ntotal topics: '
    print len(n_grams)
    print '\nclass distribution: '
    print sc_dict

# Reading the training dataset
dataReader(data_path + data_file, unigrams, tweet_ids, tweet_topic, topics, sentiment_classes)

# Extracting words above frequency threshold 
chooseFrequentWords(unigrams, selected_unigrams, freq_thresh)

#printing stats
#getStats(unigrams, tweet_ids, selected_unigrams, sentiment_classes)
#
## Creating the FV/TDM
createFV(data_path + data_file, selected_unigrams, tdm, tweet_ids,  sentiment_classes)
#print tdm
## enhancing the FV/TDM with TF-IDF
tfIDF(selected_unigrams, tweet_ids, tdm, tdm_tfIdf)
#
## Writing FV/TDM to file
writeFVtoARFF(arff_file_path+arff_file, selected_unigrams, tdm_tfIdf, tweet_ids, tweet_topic, sentiment_classes, 'Sentiment_Analysis_TaskB_emot_stem_tfidf')