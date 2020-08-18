# pip install cfscrape

import cfscrape
from bs4 import BeautifulSoup as bs
import os
import time
import sys
from multiprocessing.dummy import Pool
import io
import re
import shutil
from PIL import Image
from PIL import ImageFile
import traceback
import datetime
import string
import requests
from operator import itemgetter

domain_name = 'https://www.creativeuncut.com/'
start = time.time()

scraper1 = requests.Session()
scraper1.trust_env = False

# scraper1 = cfscrape.create_scraper()

foldername1 = "Docs"
d1 = 0

if not os.path.exists(foldername1):
  os.makedirs(foldername1)

with scraper1.get("https://www.creativeuncut.com/game-art-galleries.html") as mainhtml1:
  if mainhtml1.status_code == 200:
    pagesoup1 = bs(mainhtml1.content)
    print('Finished Getting Main Page')
  else:
    print('Main Link is not working')
    sys.exit(0)

all_posts = pagesoup1.find_all('div',attrs={'class':'ag'})
all_posts = all_posts[2:]
no_of_posts = len(all_posts)
print('Number Of Posts : ',no_of_posts)

url_title = []
all_post_urls_with_title = []
t_counter1 = 0
for t_count in range(no_of_posts):
  t_counter1 += 1
  url = domain_name + all_posts[t_count].a['href']
  title = all_posts[t_count].text
  all_post_urls_with_title.append(["{:03d}".format(t_counter1),title,url])
  # print('No : {} Title : {}'.format(t_count-2,title))
  url_title.append( title + '----' + url )


with open(foldername1 + '/all_posts.txt', 'w', encoding='utf-8') as f1:
  f1.write('\n'.join(url_title))

test_list1 = []
test_list1.append(['44444','1bitHeart','https://www.creativeuncut.com/art_1bitheart_a.html'])


enable_print = 0
empty_posts = []
ready_posts = []
error_posts = []
not_found_posts = []
start = time.time()
noofcores = 4
m1 = 4
noofthreads = noofcores * m1

t_counter2 = 0
def movscr(post):
  global t_counter2
  t_counter2 += 1
  print(t_counter2)
  
  img_numbering   = 0
  page_numbering  = 0
  current_page_no = 0
  no_of_pages     = 0
  
  movurl   = post[2]
  movname  = post[1]
  mov_s_no = post[0]

  movresponse = scraper1.get(movurl)
  retrycount = 1
  while movresponse.status_code != 200 and retrycount <= 1:
    movresponse = scraper1.get(movurl)
    retrycount += 1
  if movresponse.status_code != 200:
    not_found_posts.append([mov_s_no,img_numbering,no_of_pages,movurl,movname])
    return False
  else:
    soup1 = bs(movresponse.content, 'html.parser')
    pages_list = soup1.find('div',attrs={'class':'r_float'})
    next_pages = pages_list.find_all('a',attrs={'class':'gn'})
    no_of_pages = len(next_pages) + 1
    if enable_print == 1:
      print('No of pages : ',no_of_pages)
    
    for each_page in range(current_page_no,no_of_pages):
      if enable_print == 1:
        print("For ",each_page,':')
      table_list1 = soup1.find('div',attrs={'class':'glry'})
      if enable_print == 1:
        print('Table : ',table_list1)
      if table_list1 != None:
        all_img_in_page = table_list1.find_all('div',attrs={'class':'th'})
        img_numbering += len(all_img_in_page)



      table_list2 = soup1.find('div',attrs={'class':'gbox'})
      if table_list2 != None:
        all_img_in_page = table_list2.find_all('div',attrs={'class':'gl'})
        img_numbering += len(all_img_in_page)

      if table_list1 == None and table_list2 == None:
        empty_posts.append([mov_s_no,img_numbering,no_of_pages,movurl,movname])
        return False

      if enable_print == 1:
        print('Image Count : ',img_numbering)
      current_page_no += 1
      if current_page_no < no_of_pages:
        if enable_print == 1:
          print('New Page :',current_page_no)
        page_numbering += 1
        if enable_print == 1:
          print('Page Number : ',page_numbering)
        img_numbering -= 1

        next_page_url = domain_name + next_pages[current_page_no - 1]['href']
        if enable_print == 1:
          print('Next page url : ',next_page_url)

        movresponse = scraper1.get(next_page_url)
        retrycount = 1
        while movresponse.status_code != 200 and retrycount <= 1:
          movresponse = scraper1.get(movurl)
          retrycount += 1
        if movresponse.status_code != 200:
          error_posts.append([mov_s_no,img_numbering,no_of_pages,movurl,movname])
        else:
          soup1 = bs(movresponse.content, 'html.parser')
        if enable_print == 1:
          print('End of FOR loop for page no : ',current_page_no)
  ready_posts.append([mov_s_no,img_numbering,no_of_pages,movurl,movname])


pool1 = Pool(noofthreads)
pool1.map(movscr,all_post_urls_with_title)
# pool1.map(movscr,all_post_urls_with_title)
pool1.close()
pool1.join()

print('Length of Empty Posts : ',len(empty_posts))
print('Length of Success Posts : ',len(ready_posts))
print('Length of Error Posts : ',len(error_posts))

# ready_posts

# sorted(ready_posts,key=itemgetter(1))

temp_list1 = []
# temp_list1.append('Serial_No,Images_Count,Pages_Count,URL,Title')
for each_line in ready_posts:
  sno = each_line[0]
  no_img = str(each_line[1])
  no_page = str(each_line[2])
  url = each_line[3]
  title = each_line[4].replace(',','_')
  temp_list1.append(','.join([sno,no_img,no_page,url,title]))
text_content_CU = '\n'.join(temp_list1)

with open('Creative-Uncut.com.csv','w',encoding='utf-8') as f1:
  f1.write(text_content_CU)

headers1 = {
    'User-agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.76 Safari/537.36',
    'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding' : 'gzip,deflate,sdch',
    'Referer' : 'https://www.creativeuncut.com/gallery-32/1bh-logo.html'
}

res = scraper1.get('https://www.creativeuncut.com/gallery-32/art/1bh-logo.jpg',headers=headers1)
retrycount = 1
while res.status_code != 200 and retrycount <= 1:
  res = scraper1.get('https://www.creativeuncut.com/gallery-32/art/1bh-logo.jpg',headers=headers1)
  retrycount += 1
movimgname = '1.jpg'
if 'image' not in res.headers.get("content-type", ''):
  print('https://www.creativeuncut.com/gallery-32/art/1bh-logo.jpg','Image NOt found for ',movimgname)
else:
  print('Success')

error_download_page = []
error_download_img = []
empty_posts = []
start = time.time()
noofcores = 4
m1 = 4
noofthreads = noofcores * m1
srcfoldername = 'Docs'
srcfilename = 'all_posts.txt'

desfoldername1 = 'Data1'

alphabetfolderlist = '1ABCDEFGHIJKLMNOPQRSTUVWXYZ'
alphabetfolderlist1 = [i1 for i1 in alphabetfolderlist]
alphabetfolderlist1.append('The')
for tempfoldername in alphabetfolderlist1:
  if not os.path.exists(desfoldername1+'/'+tempfoldername):
    os.makedirs(desfoldername1+'/'+tempfoldername)

ImageFile.LOAD_TRUNCATED_IMAGES = True

finished_post_count = 0
have_count1 = 0
have_posts = []
def movscr(post):
  global finished_post_count,have_count1,have_posts
  movurl = post[2]
  movname1 = post[1]

  if movname1[0] == 'A' or movname1[0] == 'a' or movname1[0] == 'Æ':
    tempmovfoldername = 'A'
  elif movname1[0] == 'B' or movname1[0] == 'b':
    tempmovfoldername = 'B'
  elif movname1[0] == 'C' or movname1[0] == 'c':
    tempmovfoldername = 'C'
  elif movname1[0] == 'D' or movname1[0] == 'd':
    tempmovfoldername = 'D'
  elif movname1[0] == 'E' or movname1[0] == 'e' or movname1[0] == 'É' :
    tempmovfoldername = 'E'
  elif movname1[0] == 'F' or movname1[0] == 'f':
    tempmovfoldername = 'F'
  elif movname1[0] == 'G' or movname1[0] == 'g':
    tempmovfoldername = 'G'
  elif movname1[0] == 'H' or movname1[0] == 'h':
    tempmovfoldername = 'H'
  elif movname1[0] == 'I' or movname1[0] == 'i':
    tempmovfoldername = 'I'
  elif movname1[0] == 'J' or movname1[0] == 'j':
    tempmovfoldername = 'J'
  elif movname1[0] == 'K' or movname1[0] == 'k':
    tempmovfoldername = 'K'
  elif movname1[0] == 'L' or movname1[0] == 'l':
    tempmovfoldername = 'L'
  elif movname1[0] == 'M' or movname1[0] == 'm':
    tempmovfoldername = 'M'
  elif movname1[0] == 'N' or movname1[0] == 'n':
    tempmovfoldername = 'N'
  elif movname1[0] == 'O' or movname1[0] == 'o' or movname1[0] == 'Ö' :
    tempmovfoldername = 'O'
  elif movname1[0] == 'P' or movname1[0] == 'p':
    tempmovfoldername = 'P'
  elif movname1[0] == 'Q' or movname1[0] == 'q':
    tempmovfoldername = 'Q'
  elif movname1[0] == 'R' or movname1[0] == 'r':
    tempmovfoldername = 'R'
  elif movname1[0] == 'S' or movname1[0] == 's':
    tempmovfoldername = 'S'
  elif movname1[0] == 'T' or movname1[0] == 't':
    tempmovfoldername = 'T'
    if movname1[:4].lower() == 'the ':
      tempmovfoldername = 'The'
  elif movname1[0] == 'U' or movname1[0] == 'u':
    tempmovfoldername = 'U'
  elif movname1[0] == 'V' or movname1[0] == 'v':
    tempmovfoldername = 'V'
  elif movname1[0] == 'W' or movname1[0] == 'w':
    tempmovfoldername = 'W'
  elif movname1[0] == 'X' or movname1[0] == 'x':
    tempmovfoldername = 'X'
  elif movname1[0] == 'Y' or movname1[0] == 'y':
    tempmovfoldername = 'Y'
  elif movname1[0] == 'Z' or movname1[0] == 'z':
    tempmovfoldername = 'Z'
  else:
    tempmovfoldername = '1'

  string1 = movname1
  string1 = string1.replace('?', '_')
  string1 = string1.replace(':', '_')
  string1 = string1.replace('/', '_')
  string1 = string1.replace('\\', '_')
  string1 = string1.replace('*', '_')
  string1 = string1.replace('"', '_')
  string1 = string1.replace('<', '_')
  string1 = string1.replace('>', '_')
  string2 = string1.replace('|', '_')

  desfoldername = desfoldername1+'/'+ tempmovfoldername + '/' + string2
  
  if not os.path.exists(desfoldername):
    os.makedirs(desfoldername)

  if not os.path.exists(desfoldername + '/Details.txt'):
    movresponse = scraper1.get(movurl,headers=headers1)
    retrycount = 1
    while movresponse.status_code != 200 and retrycount <= 1:
      movresponse = scraper1.get(movurl,headers=headers1)
      retrycount += 1
    if movresponse.status_code != 200:
      error_download.append[movname1,movurl]
      return False
    else:
      soup1 = bs(movresponse.content, 'html.parser')
      pages_list = soup1.find('div',attrs={'class':'r_float'})
      next_pages = pages_list.find_all('a',attrs={'class':'gn'})
      no_of_pages = len(next_pages) + 1

      img_numbering = 0
      page_numbering = 0
      current_page_no = 0
      img_url_list = []
      for each_page in range(current_page_no,no_of_pages):
        all_img_in_page = []
        
        table_list1 = soup1.find('div',attrs={'class':'glry'})
        if table_list1 != None:
          all_img_in_page = table_list1.find_all('div',attrs={'class':'th'})

        table_list2 = soup1.find('div',attrs={'class':'gbox'})
        if table_list2 != None:
          all_img_in_page = table_list2.find_all('div',attrs={'class':'gl'})

        if table_list1 == None and table_list2 == None:
          empty_posts.append([mov_s_no,img_numbering,no_of_pages,movurl,movname])
          print('Empty Posts Found')
          return False


        for each_img in all_img_in_page:
          img_numbering += 1
          t_url1 = domain_name + each_img.div.a['href']
          t_url2 = domain_name + each_img.div.a.img['src'].replace('_s.jpg','.jpg')
          img_url_list.append(t_url2)
          headers1['Referer'] = t_url1

          res = scraper1.get(t_url2,headers=headers1)
          retrycount = 1
          while res.status_code != 200 and retrycount <= 1:
            res = scraper1.get(t_url2,headers=headers1)
            retrycount += 1
          global d1
          d1 = res.content
          movimgname = "{:03d}".format(img_numbering) + '.' + string.ascii_lowercase[page_numbering] + '.' + t_url2[t_url2.rfind('/')+1:]
          if 'image' not in res.headers.get("content-type", ''):
            error_download_img.append([movname1,movurl,t_url2])
            print(t_url2,'Image NOt found for ',movimgname,' ',movname1)
          else:
            i = Image.open(io.BytesIO(res.content))
            tempdownloadingimagename = 'zzzz-' + movimgname
            i.save(desfoldername+'/'+  tempdownloadingimagename)
            shutil.move(desfoldername+'/'+  tempdownloadingimagename, desfoldername+'/'+ movimgname)
            # print(t_url2,'Image found for ',movimgname,' ',movname1)
        current_page_no += 1
        if current_page_no < no_of_pages:
          page_numbering += 1

          next_page_url = domain_name + next_pages[current_page_no - 1]['href']

          movresponse = scraper1.get(next_page_url,headers=headers1)
          retrycount = 1
          while movresponse.status_code != 200 and retrycount <= 1:
            movresponse = scraper1.get(movurl,headers=headers1)
            retrycount += 1
          if movresponse.status_code != 200:
            erroroccured(movline)
            incerror()
          else:
            soup1 = bs(movresponse.content, 'html.parser')

    finished_post_count += 1
    detail_content_raw = [
                          'Title    : {}'.format(movname1),
                          'URL      : {}'.format(movurl),
                          'No IMGs  : {}'.format(img_numbering),
                          'No Pages : {}'.format(page_numbering),
                          '\n',
                          'IMG URLS :\n{}'.format('\n'.join(img_url_list))
                          
                          ]
    detail_content = '\n'.join(detail_content_raw)
    with open(desfoldername + '/Details.txt','w') as f1:
      f1.write(detail_content)
    print('Finished Count : {:03d} IMG Count : {:03d} Title : {} URL : {}'.format(finished_post_count,img_numbering,movname1,movurl)) 
  else:
    have_count1 += 1
    have_posts.append(movurl)
    print('Have Count = ',have_count1)
 


pool1 = Pool(noofthreads)
pool1.map(movscr,all_post_urls_with_title)
pool1.close()
pool1.join()
