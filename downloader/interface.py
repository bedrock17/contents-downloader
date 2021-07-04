from abc import *

class contents_manager(metaclass=ABCMeta):
    contents_provider_name = 'provider'
    contents_provicer_main_page_url = ''

    def print_info(self):
        print("contents_provider_name:", self.contents_provider_name)
        print("contents_provicer_main_page_url:", self.contents_provicer_main_page_url)

    @abstractmethod
    def get_contets_list():
        pass
    
    @abstractmethod
    def download_contents():
        pass