import json
from logger import logger

class tools:
    def __init__(self, json_address):
        self.json_address = json_address
        
    def load_titles(self):
        try:
            with open(self.json_address, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading titles: {e}")
            return {}

    def save_titles(self, data):
        try:
            with open(self.json_address, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Error in saving titles: {e}")
            return False
    
    def delete(self, title, user_id):
        try:
            data = self.load_titles()
            for d in data[user_id]:
                if title == d[2]:
                    data[user_id].remove(d)
                    self.save_titles(data)
                    return True
            return "UNKNOWN_TITLE"
        except Exception as e:
            logger.error(f"Error in deleting an ad: {e}")
            return False
    
    def add(self, link_page, link_ad, title, user_id):
        try:
            title = str(title)
            link_page = str(link_page)
            link_ad = str(link_ad)
            status = None
            
            data = self.load_titles()
            data.setdefault(user_id, []).append([link_page, link_ad, title, status])
            self.save_titles(data)
            
            return True
        except Exception as e:
            logger.error(f"Error in adding an ad: {e}")
            return False 
    
    def view_ads(self, user_id):
        try:
            data = self.load_titles()
            titles = [i[2] for i in data.get(user_id, [])]
            if not titles:
                return "NO_TITLE"
            msg = "آگهی های شما :" + "\n" + "\n".join(titles)
            return msg
        except Exception as e:
            logger.error(f"Error in getting view of ads: {e}")
            return False 
