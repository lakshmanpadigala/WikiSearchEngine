from dataclasses import fields
import re
import time
from nltk.corpus import stopwords
import string
import sys
import nltk
from nltk.stem import PorterStemmer
from Stemmer import Stemmer
from nltk.stem import WordNetLemmatizer
from collections import defaultdict
import math

nltk.download('stopwords')
stop_words = set(stopwords.words("english"))
stop_words_dict = defaultdict(int)
for word in stop_words:
    stop_words_dict[word] = 1
ps = PorterStemmer()
STEMMER = Stemmer('english')
LEMMATIZER = WordNetLemmatizer()
# OUT_FOLDER = './output_tail'
# OUT_FOLDER = './output'
OUT_FOLDER = '/home/lakshman_padigala/Desktop/IRE/WikiSearchEngine/2021201069/output'
number_of_index_files = 0
secondary_index_dict = {}
title_offset = []
top_n = 11

def intialize():
    global number_of_index_files
    f = open(OUT_FOLDER + '/stat.txt','r')
    stats = f.read().split('\n')
    f.close()
    stats = stats[:-1]
    number_of_index_files = int(stats[2].split(':')[1].strip())
    # print('abc:',number_of_index_files)
    # print('stats:',stats)

def read_title_offset():
    global title_offset
    filename = OUT_FOLDER + '/title_offset.txt'
    f = open(filename,'r')
    title_offset = f.readlines()
    title_offset = [int(i.strip()) for i in title_offset]
    f.close()
    


def tokenize_data(text):
    '''
    returns list of tokens after cleaning!
    '''
    text = text.encode('ascii','ignore').decode() #remove unicode characters
    text = re.sub("\'", '', text) #remove ' symbol in 's 'ies
    text = re.sub('[%s]' % re.escape(string.punctuation), ' ', text) #remove punctuations
    text = ' '.join([word for word in text.split(' ') if stop_words_dict[word] != 1 ]) #remove stop words
    # print('Text5:',text)
    # text = re.sub(r'&nbsp;|&lt;|&gt;|&amp;|&quot;|&apos;', r' ', text) # removing html entities
    text = ' '.join([word for word in text.split(' ') if (word.isalpha() and len(word) > 1 ) or (word.isnumeric() and len(word) < 5) ]) #or word.isalnum() #remove large numbers len > 4
    # print('Text:',text)
    return text.split(' ')

def stem_words(data):
    # return [LEMMATIZER.lemmatize(word) for word in data]
    return [STEMMER.stemWord(word) for word in data]
    '''stem_words = []
    for word in data:
    stem_words.append(word)#ps.stem(word)
    return stem_words'''

def read_secondary_index():
    global number_of_index_files, secondary_index_dict
    filename = OUT_FOLDER + '/secondary_index.txt'
    f = open(filename,'r')
    for i in range(number_of_index_files):
        line = f.readline().strip()
        line = line.split(':')
        secondary_index_dict[i] = line[1:]
    f.close()
    # pass

def search_index_num(token):
    global secondary_index_dict, number_of_index_files
    for i in range(number_of_index_files):
        if token > secondary_index_dict[i][0] and token < secondary_index_dict[i][1]:
            break
    return i

def process_posting(posting_list):
    dict_doc_freq = {}
    for word in posting_list:
        li = posting_list[word].split(';')[:-1]
        doc_id = {} #doc_id : freq
        for w in li:
            a = re.split('t|b|i|r|l|c',w)
            # print('ab:',a)
            a = [int(i) for i in a]
            doc_id[a[0]] = sum(a[1:])
        dict_doc_freq[word] = doc_id
    return dict_doc_freq #{word: {doc_id:count,doc_id:count,.....}, word2 : { doc_id:count,...........},.............}

def process_posting_field(posting_list,fields):
    dict_doc_freq = {}
    for i,word in enumerate(posting_list):
        li = posting_list[word].split(';')[:-1]
        doc_id = {}
        for w in li:
            a = re.split('(t|b|i|r|l|c)',w)
            # a = [int(a[j]) for j in range(0,len(a)) if j%2 == 0 ]
            # print('ab:',a)
            for j in range(1,len(a)):
                if j%2 == 1:
                    if fields[i] == a[j]:
                        doc_id[int(a[0])] = int(a[j+1])
            if int(a[0]) not in doc_id.keys():
                doc_id[int(a[0])] = 0
        dict_doc_freq[word] = doc_id
    return dict_doc_freq

def get_page_rank(a):
    global number_of_index_files
    page_rank= defaultdict(int)
    for word,pages in a.items():
        for page,freq in pages.items():
            page_rank[page] += (freq)*(math.log(number_of_index_files/(1+len(pages))))
    # print(page_rank)
    pr = []
    for key in page_rank:
        pr.append(list([page_rank[key],key]))
    pr.sort(key = lambda x: x[0] , reverse=True)
    final_order = []
    for item in pr:
        final_order.append(item[1])
    # print(final_order)
    return final_order
    # print(pr)

def plain_query(search_tokens):
    # index_file_num = []
    posting_list = {}
    for token in search_tokens:
        index = search_index_num(token)
        # index_file_num.append()
        filename = OUT_FOLDER + '/finalindex' + str(index) + '.txt'
        f = open(filename,'r')
        while True:
            line = f.readline().strip()
            if not line:
                break
            word = line.split(':')[0].strip()
            if word == token:
                posting_list[word] = line.split(':')[1].strip()
                break
        # if token not in posting_list.keys():
        #     posting_list[token] = '' #check for 20k word not present
    dict_doc_freq = process_posting(posting_list)
    result = get_page_rank(dict_doc_freq)
    # print('abc:',dict_doc_freq)
    return result

def field_query(search_tokens,fields):
    posting_list = {}
    for token in search_tokens:
        index = search_index_num(token)
        # index_file_num.append()
        filename = OUT_FOLDER + '/finalindex' + str(index) + '.txt'
        f = open(filename,'r')
        while True:
            line = f.readline().strip()
            if not line:
                break
            word = line.split(':')[0].strip()
            if word == token:
                posting_list[word] = line.split(':')[1].strip()
                break
        # if token not in posting_list.keys():
        #     posting_list[token] = '' #check for 20k word not present
    # print('ab:',posting_list)
    # print('abc:',fields)
    dict_doc_freq = process_posting_field(posting_list,fields)
    result = get_page_rank(dict_doc_freq)
    # print('abc:',dict_doc_freq)
    return result

def process_query(query):

    if re.match(r'[t|b|i|c|l|r]:',query):
        temp_tokens = query.split(':')
        curr_feild = temp_tokens[0]
        field_dict = {}
        search_tokens = []
        for i in range(1,len(temp_tokens)):
            words = temp_tokens[i].split(' ')
            num_words = 0
            if i == len(temp_tokens)-1:
                num_words = len(words)
            else:
                num_words = len(words)-1
            for j in range(0,num_words):
                field_dict[words[j]] = curr_feild
                # fields.append(curr_feild)
                search_tokens.append(words[j])
            curr_feild = words[-1]
        search_tokens = tokenize_data(' '.join(search_tokens))
        fields = [field_dict[key] for key in search_tokens ]
        search_tokens = stem_words(search_tokens)

        result = field_query(search_tokens,fields)
        # print(f'Field Query:{search_tokens}, Fields:{fields}')
        return result

    search_tokens = tokenize_data(query)
    search_tokens = stem_words(search_tokens)
    result = plain_query(search_tokens)
    # print(f'Plain query:{search_tokens}')
    return result

def write_result(result, time):
    global title_offset, top_n
    if len(result) > top_n :
        result = result[:top_n]
    # print('result:',result)
    file_seek = [title_offset[i-1] for i in result]
    filename = OUT_FOLDER + '/titles.txt'
    f = open(filename,'r')
    filename_r = OUT_FOLDER + '/queries_op.txt'
    w = open(filename_r,'a')
    for i in range(len(result)):
        f.seek(file_seek[i])
        title = f.readline().split(':')
        title = ' '.join(title[1:])
        w.write(f'{result[i]}, {title}')
    w.write(str(time))
    w.write('\n\n')
    f.close()
    w.close()


if __name__ == "__main__":
    intialize()
    read_secondary_index()
    read_title_offset()
    # print(title_offset)
    fname = sys.argv[1]
    # fp = open('queries.txt','r')#argv[1]
    fp = open(fname,'r')
    # fp = open('q.txt','r')#argv[1]
    queries = fp.read().split('\n')
    fp.close()
    queries = queries[:-1]
    for line in queries:
        start_time = time.time()
        result = process_query(line.lower())
        write_result(result, time.time() - start_time)
    print('-------search completed-------')
     