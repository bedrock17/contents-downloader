

from downloader.interface import contents_manager
import requests as req
from bs4 import BeautifulSoup
import os
import time
import json
import os.path


NAVER_COMIC_PREFIX = "https://comic.naver.com"
NAVER_COMIT_LIST_URI_FORMAT = "/webtoon/list.nhn?titleId=%d&page=%d"
NAVER_COMIT_DETAIL_URI_FORMAT = "/webtoon/detail.nhn?titleId=%d&no=%d"
OUTPUT_PREFIX = "output"

header = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"}

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

def download_comic_list(title_id: int, name: str, target_path: str):
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
      downlaod_comic(title_id, no, comic_link.string, target_path)

    page_index += 1

def downlaod_comic(title_id: int, comic_no: int, title_name: str, target_path: str):
  print("downlaod comic", title_id, comic_no, title_name)

  download_path = target_path + "/" + str(title_id) + "/" + str(comic_no)

  meta_path = download_path + "/meta.json"
  
  if os.path.isfile(meta_path):
    return

  page_link = NAVER_COMIC_PREFIX + NAVER_COMIT_DETAIL_URI_FORMAT % (title_id, comic_no)

  os.makedirs(download_path, exist_ok=True)

  print(page_link)

  page_text = req.get(page_link).text

  time.sleep(1)
  soup = BeautifulSoup(page_text, 'html.parser')
  comic_img_list = soup.select("div.wt_viewer > img")

  images = []
  for image in comic_img_list:
    image_path = download_path + "/" + image['id'] + ".jpg"

    images.append(image['id'] + ".jpg")

    res = req.get(image['src'], headers=header)

    print(image['src'])

    with open(image_path, "wb") as f:
      f.write(res.content)
      f.close()
    
  meta = json.dumps(
    {
      'title_id': title_id,
      'title': title_name,
      'comic_no': comic_no,
      'images': images
    }, 
    ensure_ascii=False
  )

  with open(meta_path, "wt") as f:
    f.write(meta)
    f.close()
    
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
    target_path = OUTPUT_PREFIX + "/" + self.contents_provider_name
    os.makedirs(OUTPUT_PREFIX + "/" + self.contents_provider_name, exist_ok=True)

    for info in self.contents_info_list:
      title_id, name = info
      print(f"Download comic [{title_id}][{name}]")
      download_comic_list(title_id, name, target_path)
  
