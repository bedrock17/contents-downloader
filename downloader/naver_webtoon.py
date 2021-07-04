
from downloader.interface import contents_manager
import requests as req
from bs4 import BeautifulSoup
import os

NAVER_COMIC_PREFIX = "https://comic.naver.com"
NAVER_COMIT_LIST_URI_FORMAT = "/webtoon/list.nhn?titleId=%d&page=%d"
OUTPUT_PREFIX = "output"

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
      param = a['href'].split("?")
      title = int(param[1].split("&")[0].split("=")[1])
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
      print(f"Download comic [{info[0]}][{info[1]}]")
      self.download_comic(info)
  
  def download_comic(self, info):
    pass