
from ast import parse
from downloader.interface import contents_manager
import requests as req
from bs4 import BeautifulSoup
import os

NAVER_COMIC_PREFIX = "https://comic.naver.com"
NAVER_COMIT_LIST_URI_FORMAT = "/webtoon/list.nhn?titleId=%d&page=%d"
OUTPUT_PREFIX = "output"

def parse_get_param(uri: str, key: str) -> str:
  ret = ""
  param = uri.split("?")[1]
  lst = param.split("&")
  for item in lst:
    if item.find(key) >= 0:
      _, v = item.split("=")
      ret = v
      break
  return ret

def download_comic_list(title_id, name):
  continue_download = True
  page_index = 1

  download_visit = {}

  while continue_download:

    page_link = NAVER_COMIC_PREFIX + NAVER_COMIT_LIST_URI_FORMAT % (title_id, page_index)

    page_text = req.get(page_link).text

    soup = BeautifulSoup(page_text, 'html.parser')
    
    comic_link_list = soup.select("td.title > a")
    
    for comic_link in comic_link_list:

      no = int(parse_get_param(comic_link['href'], "no"))

      if no in download_visit:
        continue_download = False
        break

      download_visit[no] = True
      print(name, comic_link.string, no)
      downlaod_comic(no, name)

    page_index += 1

def downlaod_comic(comic_no, title_name):
  print("downlaod comic", comic_no, title_name)
  # 해당 회수에 맞춰 URI를 만들고
  # 페이지를 받은다음
  # 해당화를 저장할 폴더를 만들고
  # 페이지를 파싱해서
  # 이미지를 순서대로 리스트로 만들어서
  # 이미지를 하나하나 받고
  # metadata를 json으로 하나 만들어야함 (해당화에 이름등을 저장)
  

class naver_webtoon_downloader(contents_manager):

  contents_info_list = []

  def __init__(self) -> None:
    super().__init__()
    self.contents_provider_name = "NAVER"
    self.contents_provicer_main_page_url = "https://comic.naver.com/webtoon/weekday.nhn"

  def get_contets_list(self):
    response = req.get(self.contents_provicer_main_page_url)
    # print(response.text)

    soup = BeautifulSoup(response.text, 'html.parser')

    listarea = soup.select(".list_area.daily_all")

    linklist = listarea[0].select("a.title")

    #페이지에서 현재 연재중인 작품 리스트 수집
    contents_info_list = []
    for a in linklist:
      title = int(parse_get_param(a['href'], "title"))
      contents_info_list.append((title, a.string))
    
    #중복제거
    self.contents_info_list = list(set(contents_info_list))
    self.contents_info_list.sort()

    # debug
    # for info in contents_info_list:
    #   print(info)
    # print(len(self.contents_info_list))

    return self.contents_info_list
    
  def download_contents(self):
    os.makedirs(OUTPUT_PREFIX + "/" + self.contents_provider_name, exist_ok=True)

    for info in self.contents_info_list:
      title_id, name = info
      print(f"Download comic [{title_id}][{name}]")
      download_comic_list(title_id, name)
  
