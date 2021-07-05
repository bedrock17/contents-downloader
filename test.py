

from downloader.naver_webtoon import naver_webtoon_downloader

t = naver_webtoon_downloader()

t.print_info()
t.get_contets_list()
t.download_contents()