# import pandas as pd
import numpy as np
from urllib.parse import urlparse
import ipaddress
import re
import requests
import os
import base64
from urllib.parse import urlparse, quote

class FeatureExtractor:
    def __init__(self):
        self.columns = [
            'having_IP_Address', 'URL_Length', 'Shortining_Service', 'having_At_Symbol',
            'double_slash_redirecting', 'Prefix_Suffix', 'having_Sub_Domain', 'SSLfinal_State',
            'Domain_registeration_length', 'Favicon', 'port', 'HTTPS_token', 'Request_URL',
            'URL_of_Anchor', 'Links_in_tags', 'SFH', 'Submitting_to_email', 'Abnormal_URL',
            'Redirect', 'on_mouseover', 'RightClick', 'popUpWidnow', 'Iframe', 'age_of_domain',
            'DNSRecord', 'web_traffic', 'Page_Rank', 'Google_Index', 'Links_pointing_to_page',
            'Statistical_report'
        ]

    def check_phishtank(self, url: str) -> int:
        """
        Interacts with the PhishTank API (or simple public check) to verify if a URL is a known phishing site.
        Returns: 
           -1 (Phishing - Found in database)
            0 (Unknown/Error)
            1 (Legitimate - Not found)
        """
        try:
            # Using the checkurl method. API key recommended for higher limits.
            api_key = os.getenv("PHISHTANK_API_KEY") 
            params = {
                'format': 'json',
                'url': url
            }
            if api_key:
                params['app_key'] = api_key
            
            # Note: PhishTank checkurl is a POST request typically, but some endpoints allow GET.
            # Official docs say POST to http://checkurl.phishtank.com/checkurl/
            response = requests.post("http://checkurl.phishtank.com/checkurl/", data=params, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                # PhishTank JSON format: {'results': {'in_database': True, 'valid': True}}
                if result.get('results', {}).get('in_database'):
                    if result['results']['valid']:
                        return -1 # It IS a valid phishing site
                return 1 # Not in database or not valid anymore
        except Exception as e:
            print(f"PhishTank API Error: {e}")
            return 0
        return 1

    def extract_features(self, url: str) -> np.ndarray:
        data = {}
        
        # 1. IP Address handling
        try:
            ipaddress.ip_address(urlparse(url).netloc)
            data['having_IP_Address'] = -1  # Phishing
        except:
            data['having_IP_Address'] = 1   # Legitimate

        # 2. URL Length
        if len(url) < 54:
            data['URL_Length'] = 1
        elif len(url) >= 54 and len(url) <= 75:
            data['URL_Length'] = 0
        else:
            data['URL_Length'] = -1

        # 3. Shortening Service (Simplified regex)
        match = re.search('bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|'
                        'yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|'
                        'short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|'
                        'doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|'
                        'db\.tt|qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|'
                        'q\.gs|is\.gd|po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|'
                        'x\.co|prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|tr\.im|link\.zip\.net', url)
        data['Shortining_Service'] = -1 if match else 1

        # 4. @ Symbol
        data['having_At_Symbol'] = -1 if '@' in url else 1

        # 5. Double Slash Redirect
        data['double_slash_redirecting'] = -1 if url.rfind('//') > 7 else 1

        # 6. Prefix Suffix (-)
        data['Prefix_Suffix'] = -1 if '-' in urlparse(url).netloc else 1

        # 7. Sub Domain (heuristic)
        dots = urlparse(url).netloc.count('.')
        if dots == 1:
            data['having_Sub_Domain'] = 1
        elif dots == 2:
            data['having_Sub_Domain'] = 0
        else:
            data['having_Sub_Domain'] = -1

        # 8. SSL Final State (Simple check)
        # Note: Real implementation would check cert age. Here we check protocol.
        if url.startswith('https'):
            data['SSLfinal_State'] = 1
        else:
            data['SSLfinal_State'] = -1
            
        # --- Simplified heuristics ---
        data['Domain_registeration_length'] = 0 
        data['Favicon'] = 0 
        data['port'] = 1 
        
        # HTTPS token in domain
        data['HTTPS_token'] = -1 if 'https' in urlparse(url).netloc else 1
        
        data['Request_URL'] = 1 
        data['URL_of_Anchor'] = 0
        data['Links_in_tags'] = 0
        data['SFH'] = 1
        data['Submitting_to_email'] = 1
        
        # Abnormal URL (if hostname not in URL)
        data['Abnormal_URL'] = 1
        
        # IMPROVED HEURISTICS: Check for suspicious keywords
        suspicious_keywords = ['login', 'signin', 'verify', 'update', 'account', 'banking', 'secure', 'confirm', 'wallet']
        url_lower = url.lower()
        for keyword in suspicious_keywords:
             if keyword in url_lower and 'google' not in url_lower and 'microsoft' not in url_lower:
                  data['Abnormal_URL'] = -1
                  break

        data['Redirect'] = 0
        data['on_mouseover'] = 1
        data['RightClick'] = 1
        data['popUpWidnow'] = 1
        data['Iframe'] = 1
        data['age_of_domain'] = 0 
        data['DNSRecord'] = 0 
        data['web_traffic'] = 0 
        data['Page_Rank'] = 0
        data['Google_Index'] = 0
        data['Links_pointing_to_page'] = 0
        data['Statistical_report'] = 0

        # Create Numpy Array (Ordered by self.columns)
        features_list = [data[col] for col in self.columns]
        return np.array(features_list).reshape(1, -1)
