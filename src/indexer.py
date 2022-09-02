# !pip install PyStemmer

from typing import DefaultDict
from unicodedata import category
import xml.sax
import re
from nltk.corpus import stopwords
import string
from collections import defaultdict
import nltk
from nltk.stem import PorterStemmer
from Stemmer import Stemmer
from nltk.stem import WordNetLemmatizer
from collections import defaultdict
import json
import time
import sys
import os
import heapq

start_time = time.time()
nltk.download('stopwords')
stop_words = set(stopwords.words("english"))
url_stop_words = ["http", "https", "www", "ftp", "com", "net", "org","edu","gov","jpg","uk","jgeg","htm","in","ac","net","ww3", "archives", "pdf", "html", "png", "txt", "redirect"]
stop_words_dict = defaultdict(int)
for word in stop_words:
    stop_words_dict[word] = 1
ps = PorterStemmer()
STEMMER = Stemmer('english')
LEMMATIZER = WordNetLemmatizer()

page_count = 0
temp_index_file_count = 0
temp_index = defaultdict(list)
title_id_dict = {}
secondary_index_dict = {} #to store file number: [starting word,last word]

WRITE_FOR_PAGES = 5000
SIZE_OF_FINAL_INDEX_FILE = 10485760
WORDS_IN_EACH_FINAL_INDEX = 20000
# OUT_FOLDER = './output_tail'
# OUT_FOLDER = './output'
OUT_FOLDER = './2021201069/output'
total_number_of_tokens_parsed = 0
permanent_index_num = 0
number_of_words_in_last_index = 0
title_offset = []
# extractor = URLExtract()

"""####pre-processing...!"""

class pre_processing():

    def __init__(self,dict):
        self.id = dict['id']
        self.title = dict['title']
        self.text = dict['text']

    def create_word_freq_dict(self,tokens):
      dict = defaultdict(int)
      for word in tokens:
        dict[word] += 1
      return dict

    def get_body(self,data):
        data = self.tokenize_data(data, False)
        data = self.stem_words(data)
        return data

    def stem_words(self,data):
      # return [LEMMATIZER.lemmatize(word) for word in data]
      return [STEMMER.stemWord(word) for word in data]
      # return data
      '''stem_words = []
      for word in data:
        stem_words.append(word)#ps.stem(word)
      return stem_words'''

    def tokenize_data(self,text,url):
        '''
        returns list of tokens after cleaning!
        '''
        text = text.lower()
        text = text.encode('ascii','ignore').decode() #remove unicode characters
        if url == False:
          text = re.sub("http*\S+", " ", text) #remove urls
        text = re.sub("\'", '', text) #remove ' symbol in 's 'ies
        text = re.sub('[%s]' % re.escape(string.punctuation), ' ', text) #remove punctuations
        text = re.sub(r'&nbsp;|&lt;|&gt;|&amp;|&quot;|&apos;', r' ', text) # removing html entities
        if url==False:
          text = ' '.join([word for word in text.split(' ') if stop_words_dict[word] != 1 ]) #remove stop words
        else:
          text = ' '.join([word for word in text.split(' ') if word not in url_stop_words ]) #remove stop words like www,org,in.., 
        text = ' '.join([word for word in text.split(' ') if (word.isalpha() and len(word) > 1 )  or (word.isnumeric() and len(word) < 5) ]) #or word.isalnum() #remove large numbers len > 4
        return text.split()

    def get_title(self,title):
        title = self.tokenize_data(title, False)
        title = self.stem_words(title)
        return title

    def get_info(self,data):#{{infobox((.|\n)*)}}
        # info = re.search(r'\{\{infobox((.|\n)*)\}\}',info_data)
        info_data = []
        body_data = []
        info_flag = False
        data = data.split('\n')
        n = len(data)
        for i in range(n):
          if info_flag==False: 
            if re.search(r'\{\{infobox',data[i]):
              info_flag = True
              info_data.append(re.sub(r'\{\{infobox',' ',data[i]))
            else:
              body_data.append(data[i])
            if i > 20: #check for infobox in first 20 lines.
              break
          elif info_flag:
            if data[i] == '}}' :
              body_data = body_data + data[i+1 : ]
              break
            else:
              info_data.append(data[i])
        if info_flag==False:
          body_data = body_data + data[i+1 : ]
        info_data = (' '.join(info_data))
        info_data = self.tokenize_data(info_data , False)
        info_data = self.stem_words(info_data)
        return ('\n'.join(body_data)) , info_data

    def get_references(self,data):
        # refs = re.findall(r'\{\{refbegin\}\}(.*?)\{\{refend\}\}',data)
        # print("Ref:",refs)
        refs = []
        data = data.split('\n')
        for line in data:
          if line and line[0] == '*':
            refs.append(line)
        data = self.tokenize_data(' '.join(refs),True)
        data = self.stem_words(data)
        return data

    def get_categories(self,cat_data):
        temp = re.findall(r'\[\[category:(.*?)\]\]',cat_data)
        # print(temp)
        cat_data = ' '.join(temp)
        # for line in temp:
        #     cat_data += ' '.join(temp)
        #     cat_data += ' '
        data = self.tokenize_data(cat_data,False)
        data = self.stem_words(data)
        return data
    
    def get_links(self,text):
      '''
      returns the processed words from the links in text.
      '''
      text = text.split('\n')
      links = []
      link_regex = re.compile('https?:\/\/\S+')
      for line in text:
        # urls = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', line)
        # reg = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|(([^\s()<>]+|(([^\s()<>]+)))))+(?:(([^\s()<>]+|(([^\s()<>]+))))|[^\s`!()[]{};:'\".,<>?«»“”‘’]))"
        # urls = re.findall(reg, line)
        urls = link_regex.findall(line)
        links = links + urls
        # for url in urls:
        #   links.append(url)
      return self.tokenize_data(' '.join(links),True)

    '''urls = extractor.find_urls(str(text))
    print('url size:',len(urls))
    data = self.tokenize_data(' '.join(urls) , True)
    return data
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)'''
      
    def preProcess(self):
      # print("Pre-processing..!")
      #File Id and Title Mapping
      # f = open('Title_Id.txt','a')
      # f.write(f'{self.id} : {self.title} \n')
      # f.close()
      #title, body, info, categories, links, references
      self.text = self.text.strip() #removes extra space
      self.text = self.text.lower() #converts to lowercase
      tit = []
      body = []
      info = []
      links = []
      categories = []
      references = []
      tit = self.get_title(self.title)
      self.text , info = self.get_info(self.text)
      links = self.get_links(self.text)
      data = re.split(r'== ?references ?==',self.text)
      body = self.get_body(data[0])
      if len(data) >= 2:
          categories = self.get_categories(data[1])
          references = self.get_references(data[1])
      # fp = open('text_file.txt', 'a')
      # fp.write(f'\n..................{self.id}, {self.title}.....................................\n')
      # fp.write(f'......Title:{tit}\n')
      # fp.write(f'......Infobox:{info}\n\n')
      # fp.write(f'......Links:{links}\n\n')
      # fp.write(f'......Body: {body}\n')
      # fp.write(f'Cate:{categories}\n')
      # fp.write(f'References:{references}\n')
      # fp.close()
      return self.create_word_freq_dict(tit),self.create_word_freq_dict(body),self.create_word_freq_dict(info),self.create_word_freq_dict(categories),self.create_word_freq_dict(links),self.create_word_freq_dict(references)

"""###File Handling..!"""

class PageHandler(xml.sax.ContentHandler):

  def construct_title_offset_file(self):
    global title_offset
    filename = OUT_FOLDER + '/title_offset.txt'
    f = open(filename,'w')
    for i in title_offset:
      f.write(f'{str(i)}\n')
    # f.write('\n'.join(title_offset))
    f.close()
    print('Title Offset File Created..!')
    del title_offset

  def get_directory_size(self,directory):
    """Returns the `directory` size in bytes."""
    total = 0
    try:
      # print("[+] Getting the size of", directory)
      for entry in os.scandir(directory):
        if entry.is_file():
          # if it's a file, use stat() function
          total += entry.stat().st_size
    except PermissionError:
        # if for whatever reason we can't open the folder, return 0
        return 0
    return total/1024/1024/1024

  def construct_stat_file(self):
    global page_count, permanent_index_num, total_number_of_tokens_parsed,number_of_words_in_last_index
    f = open(OUT_FOLDER + '/stat.txt','a')
    f.write(f'Pages Indexed: {str(page_count)}\n')
    size = self.get_directory_size(OUT_FOLDER)
    f.write(f'Size of Index:{size}GB\n')
    f.write(f'Number of Files Indexed:{str(permanent_index_num+1)}\n')
    f.write(f'Number of tokens in last Index file:{str(number_of_words_in_last_index)}\n')
    f.write(f'Number of Tokens Parsed:{str(total_number_of_tokens_parsed)}\n')
    f.close()

  def construct_secondary_index_file(self):
    global secondary_index_dict
    filename = OUT_FOLDER + '/secondary_index.txt'
    f = open(filename,'a')
    for key in secondary_index_dict:
      f.write(f'{str(key)}:{secondary_index_dict[key][0]}:{secondary_index_dict[key][1]}\n')
    f.close()
    print('Secondary Index File Constructed..!')
    pass

  def index_dicts(self,tit,body,info,category,links,references):
    global page_count , temp_index_file_count , temp_index , title_id_dict, title_offset
    list_of_voc = list(set( list(tit.keys()) + list(body.keys()) + list(info.keys()) + list(category.keys()) + list(links.keys()) + list(references.keys())))
    for word in list_of_voc:
      word_ind = str(page_count) #+ ' '
      # if tit[word] > 0 :
      #   word_ind = word_ind + 't' + str(tit[word])
      header = ['t','b','i','c','l','r']
      position = 0
      for dic in [tit,body,info,category,links,references]:
        if dic[word] > 0:
          word_ind = word_ind + header[position] + str(dic[word])
        position += 1
        # word_ind = word_ind + str(dic[word]) + ' '
      temp_index[word].append(word_ind)
    if int(page_count) % WRITE_FOR_PAGES == 0:
      # print() #//WRITE_FOR_PAGES
      print("---  seconds: %s ---" % (time.time() - start_time) , ' Pages done:' , page_count)
      '''
      1. save the words ind to new file
      2. add page id's and title to title file 
      '''
      index = []
      for key in sorted(temp_index.keys()):
        string = key + ':' + ';'.join(temp_index[key]) + ';'
        index.append(string)
      filename = OUT_FOLDER + '/index' + str(temp_index_file_count) + '.txt'
      with open(filename,'w') as f:
        f.write('\n'.join(index))
      f.close()
      filename = OUT_FOLDER + '/titles.txt'
      f = open(filename,'a')
      for key in title_id_dict.keys():
        title_offset.append(f.tell())
        f.write(f'{key}:{title_id_dict[key].strip()}\n')
      f.close()
      temp_index_file_count += 1
      temp_index = defaultdict(list)
      title_id_dict = {}

  def handle_remaining_ind(self):
    global page_count , temp_index_file_count , temp_index , title_id_dict, title_offset
    index = []
    for key in sorted(temp_index.keys()):
      string = key + ':' + ';'.join(temp_index[key]) + ';'
      index.append(string)
    filename = OUT_FOLDER + '/index' + str(temp_index_file_count) + '.txt'
    with open(filename,'w') as f:
      f.write('\n'.join(index))
    f.close()
    filename = OUT_FOLDER + '/titles.txt'
    f = open(filename,'a')
    for key in title_id_dict.keys():
      title_offset.append(f.tell())
      f.write(f'{str(key)}:{title_id_dict[key].strip()}\n')
    f.close()
    temp_index_file_count += 1
    temp_index = defaultdict(list)
    title_id_dict = {}

  def merge_int_index_files(self):
    print('Merging fo temperory index files started..!')
    global temp_index_file_count , secondary_index_dict , total_number_of_tokens_parsed, permanent_index_num, number_of_words_in_last_index
    file_readers = {}
    curr_line = {}
    heap = []
    file_complete_flag = [True for i in range(temp_index_file_count)]
    word_postings = {}
    data_list = []
    str_len_data_list = 0
    word_from_file = defaultdict(list)
    permanent_index_num = 0

    for i in range(temp_index_file_count):
      filename = OUT_FOLDER + '/index' + str(i) + '.txt'
      file_readers[i] = open(filename,'r')

    for i in range(temp_index_file_count):
      curr_line[i] = file_readers[i].readline().strip()
      curr_word = curr_line[i].split(':')[0]
      word_from_file[curr_word].append(i)

      if curr_word in word_postings.keys():
        word_postings[curr_word] += curr_line[i].split(':')[1]
        #TODO  word_postings[curr_word] = word_postings[curr_word] + ';' + curr_line[i].split(':')[1]
      else:
        word_postings[curr_word] = curr_line[i].split(':')[1]
      
      if curr_word not in heap:
        heapq.heappush(heap , curr_word)

    count = 0
    while any(file_complete_flag):
      min_word = heapq.heappop(heap)
      count += 1
      #TODO can create offset file for keys if required..
      new_posting = min_word + ':' + word_postings[min_word]
      word_postings.pop(min_word)
      for file_num in word_from_file[min_word]:
        curr_line[file_num] = file_readers[file_num].readline().strip()
        if curr_line[file_num] == '':
          file_complete_flag[file_num] = False
          file_readers[file_num].close()
          os.remove(OUT_FOLDER + '/index' + str(file_num) + '.txt')
        else:
          curr_word = curr_line[file_num].split(':')[0]
          word_from_file[curr_word].append(file_num)

          if curr_word in word_postings.keys():
            word_postings[curr_word] += curr_line[file_num].split(':')[1]
          else:
            word_postings[curr_word] = curr_line[file_num].split(':')[1]
          
          if curr_word not in heap:
            heapq.heappush(heap , curr_word)
      word_from_file.pop(min_word)
      data_list.append(new_posting)
      str_len_data_list += len(new_posting)
      if count > 0 and  str_len_data_list > SIZE_OF_FINAL_INDEX_FILE: #count % WORDS_IN_EACH_FINAL_INDEX  == 0: #sys.getsizeof(data_list) > SIZE_OF_FINAL_INDEX_FILE: #
        filename = OUT_FOLDER + '/finalindex' + str(permanent_index_num) + '.txt'
        f = open(filename,'a')
        f.write('\n'.join(data_list))
        f.close()
        first = data_list[0].split(':')[0]
        last = data_list[-1].split(':')[0]
        secondary_index_dict[permanent_index_num] = [first,last]
        total_number_of_tokens_parsed += len(data_list)
        data_list = []
        str_len_data_list = 0
        permanent_index_num += 1
    filename = OUT_FOLDER + '/finalindex' + str(permanent_index_num) + '.txt'
    f = open(filename,'a')
    f.write('\n'.join(data_list))
    f.close()
    number_of_words_in_last_index = len(data_list)
    first = data_list[0].split(':')[0]
    last = data_list[-1].split(':')[0]
    secondary_index_dict[permanent_index_num] = [first,last]
    total_number_of_tokens_parsed += len(data_list)
    print('Merging fo temperory index files completed..!')

  def __init__(self):
    # self.count = 0
    # self.index_file_count = 1
    # self.invered_index = {}
    #{key1 : { t:{docId:count,docId:count,............},i:{docId:count},b:{docId:count},c:{docId:count},l:{docId:count},r:{docId:count} } 
    # key2 :.................................................................
    # key3 :................................................................. }
    self.current = ''
    self.title = ''
    self.text = ''
    self.id = ''
    self.id_count = 0
    self.dict = {}
    self.doc_id = ''

  def startElement(self, name, attri):
    self.current = name
    if name == "id":
        self.id_count += 1

  def characters(self,content):
    if self.current == "title":
        self.title += content
    elif self.current == "id" and self.id_count==1:
        self.id = content
        doc_id = self.id
    elif self.current == "text":
        self.text += content

  def endElement(self,name):
    global page_count, title_id_dict
    self.current = name
    if self.current == "page":
        # print(f"Count: {self.count}")
        page_count  = page_count + 1
        # if(page_count % 10000 == 0):
        #   print('Page_count:',page_count)
        i = pre_processing(self.dict)
        tit,body,info,categories,links,references = i.preProcess()
        title_id_dict[page_count] = self.title.lower()
        # print("len of dict:",len(title_id_dict))
        self.index_dicts(tit,body,info,categories,links,references)
        self.current = ''
        self.title = ''
        self.text = ''
        self.id = ''
        self.dict = {}
        self.id_count = 0
    elif self.current == "title":
        self.dict['title'] = self.title
        # print(f"Title: {self.title}    |count: {self.count}")
    elif self.current == "text":
        self.dict['text'] = self.text
    elif self.current == "id" and self.id_count==1:
        self.dict['id'] = self.id

# !rm text_file.txt
# !rm ./output/*

if __name__ == "__main__" :
  handler = PageHandler()
  parser = xml.sax.make_parser()
  parser.setContentHandler(handler)
  # parser.parse('data/enwiki-20220720-pages-articles-multistream15.xml')
  # parser.parse('/media/lakshman_padigala/Storage/IRE/enwiki-20220820-pages-articles-multistream.xml')
  # parser.parse('data/tail.xml')
  fname = sys.argv[1]
  parser.parse(fname)
  handler.handle_remaining_ind()
  handler.merge_int_index_files() #merge Index files
  handler.construct_secondary_index_file()
  handler.construct_stat_file()
  handler.construct_title_offset_file()
  print("---  seconds: %s ---" % (time.time() - start_time))
  # print('title offset:', title_offset)


