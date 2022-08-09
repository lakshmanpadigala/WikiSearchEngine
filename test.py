from cgitb import handler
import xml.sax

class PageHandler(xml.sax.ContentHandler):

    def __init__(self):
        self.count = 0
        self.current = ''
        self.title = ''
        self.text = ''
        self.id = ''
        self.id_count = 0

    def startElement(self, name, attri):
        self.current = name
        if name == "page":
            # self.id_count = 0
            self.count += 1
        elif name == "id":
            self.id_count += 1
        

    def characters(self,content):
        if self.current == "title":
            self.title += content
        elif self.current == "id" and self.id_count==1:
            self.id = content
        elif self.current == "text":
            self.text += content
    
    def endElement(self,name):
        if self.current == "page" and self.count < 11:
            i = Indexing()
            dict = {}
            dict['title'] = self.title
            dict['id'] = self.id
            dict['text'] = self.text
            i.preProcess(dict)

        elif self.current == "title":
            print(f"Title: {self.title}")
        # elif self.current == "id" and self.id_count==1:
        #     print(f"Id: {self.id}")
        # elif self.current == "text" and self.count < 10:
        #     print(f"Text length: {len(self.text)} , Count: {self.count}")
        #     print(f"Text: {self.text}")
        #     # f = open("demo.txt", "a")
        #     # s = self.title + ":" + self.text
        #     # f.write(s)
        #     # f.write("________________________________________________")
        #     # f.write(self.text)
        #     # f.close()
        self.current = ''
        self.title = ''
        self.text = ''
        self.id = ''


class Indexing():
    def __init__(self):
        self.count = 0
    def preprocess(dict):
        fp = open('text_file.txt', 'a')
        fp.write(dict['text'])
        fp.write('\n\n.....................................................................................\n\n')
        fp.close()
        pass


if __name__ == "__main__" :
    handler = PageHandler()
    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)
    parser.parse('data/enwiki-20220720-pages-articles-multistream15.xml-p15824603p17324602')
    

