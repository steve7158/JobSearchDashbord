import json
import requests
from typing import List, Dict
import brotli

class WellfoundJobScraper:
    def __init__(self):
        # mimic the browser request
        self.headers = {
            "Accept": "*/*",
            "Accept-encoding": "gzip, deflate, br, zstd",
            "Accept-language": "en-GB,en;q=0.7",
            "Apollographql-client-name": "talent-web",
            "Content-type": "application/json",
            "Origin": "https://wellfound.com",
            "Priority": "u=1, i",
            "Referer": "https://wellfound.com/jobs",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "same-origin", 
            "Sec-Fetch-Site": "same-origin",
            "Sec-Gpc": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "X-Angellist-D-Client-Referrer-Resource": "/jobs",
            "X-Apollo-Operation-Name": "JobSearchResultsX",
            "X-Apollo-Signature" : "1733575053-06CP%2B%2FVaX2DzUxkzcqL2c0XBIwrYw5CLCYLYZIex6bg%3D",
            "X-Requested-With": "XMLHttpRequest",
            "Cookie" : "ajs_anonymous_id=3f74e26f-6910-40a6-8f20-73b54c51cd4c; logged_in=true; _wellfound=7a4a660a0b0493b2d15323a3e3015b4d.i; cf_clearance=59QHPanuNUpB3mseetZLy2awu3UmoaytD.E.KPRw45c-1733480220-1.2.1.1-R8cuEitpoHtMWLrsPywnwYeGF8zB9I1GdzBg8ScWwmn9hPWJNfdZzYDofC63UzgV4S.h0RS9I.89kesiC1I5XFWJY4SEvHCc2p3J5ywF7FrrMAekG2SKCInr9ZiWb7IGKaD5kUPhj_wunW5e_QApgg_s73DL2vpLTtyk1.YupLxh1rYgHDu7aRmsrzFxs4z6UVP7sukPhMIXt2gWMg8C5mb_7R.040GpPyWcqSEa3UqhnJdRj02gCgNoklmKaGM5WPk5czCnsepYIHAQ6sPdA42el3bg6j9lB9zoI1j9uz6EPFIULDp1RqlkgdAEeOm3V5LgawTOYNU9aae4O3Dh12hZzSP_bKf1Zhy0CkzdLZwrFIXKKQMoifr8eLk_aOK._5P3ymrTQr0L2tWcBuK7RT67E4Gg2SbpgkH2CXgJpd0; _mkra_stck=105d3fa4432a62065203cb85b17464b1%3A1733480253.90747; datadome=wipxH3SJIEvYJc4P2fp7b62vuKdJ3faX2lck_~FgGmfkdt~RqG_DBVv1TPWX1GMAh1enVZTBSVfrun188dl4ICIN~T2baoqI~OQMMK899H2l~Gd_xSQYfVC6s7Sybs5z"
        }

        # attach the cookies
        self.cookies = {
            "ajs_anonymous_id": "3f74e26f-6910-40a6-8f20-73b54c51cd4c",
            "logged_in": "true",
            "*wellfound": "7a4a660a0b0493b2d15323a3e3015b4d.i",
            "cf*clearance": "59QHPanuNUpB3mseetZLy2awu3UmoaytD.E.KPRw45c-1733480220-1.2.1.1-R8cuEitpoHtMWLrsPywnwYeGF8zB9I1GdzBg8ScWwmn9hPWJNfdZzYDofC63UzgV4S.h0RS9I.89kesiC1I5XFWJY4SEvHCc2p3J5ywF7FrrMAekG2SKCInr9ZiWb7IGKaD5kUPhj_wunW5e_QApgg_s73DL2vpLTtyk1.YupLxh1rYgHDu7aRmsrzFxs4z6UVP7sukPhMIXt2gWMg8C5mb_7R.040GpPyWcqSEa3UqhnJdRj02gCgNoklmKaGM5WPk5czCnsepYIHAQ6sPdA42el3bg6j9lB9zoI1j9uz6EPFIULDp1RqlkgdAEeOm3V5LgawTOYNU9aae4O3Dh12hZzSP_bKf1Zhy0CkzdLZwrFIXKKQMoifr8eLk_aOK._5P3ymrTQr0L2tWcBuK7RT67E4Gg2SbpgkH2CXgJpd0; _mkra_stck=105d3fa4432a62065203cb85b17464b1%3A1733480253.90747",
            "datadome": "wipxH3SJIEvYJc4P2fp7b62vuKdJ3faX2lck_~FgGmfkdt~RqG_DBVv1TPWX1GMAh1enVZTBSVfrun188dl4ICIN~T2baoqI~OQMMK899H2l~Gd_xSQYfVC6s7Sybs5z"
        }

    def search_jobs(
        self, 
        userCustomJobTitles : List[str]
    ) -> List[Dict]:
        # GraphQL payload to send
        payload = {
            "operationName": "JobSearchResultsX",
            "variables": {
                "filterConfigurationInput": {
                    "page": 1,
                    "customJobTitles": 
                        userCustomJobTitles
                    ,
                    "equity": {
                        "min": None,
                        "max": None
                    },
                    "remotePreference": "REMOTE_OPEN",
                    "salary": {
                        "min": None,
                        "max": None
                    },
                    "yearsExperience": {
                        "min": None,
                        "max": None
                    }
                }
            },
            "extensions": {
                "operationId": "tfe/2aeb9d7cc572a94adfe2b888b32e64eb8b7fb77215b168ba4256b08f9a94f37b"
            }
        }

        try:
            # sending http request with graphql payload
            response = requests.post(
                "https://wellfound.com/graphql",
                json=payload,
                headers=self.headers,
                cookies=self.cookies
            )
            response.raise_for_status()
            if(response.status_code == 403 or response.status_code == 500 or response.status_code == 404) :
                print(f"Error fetching jobs: {e}")
                return False
            
            try:
                # convert the returned data to json
                data = response.json()
                jobs = []
                
                # clean the data to get job name , salary etc
                for edge in data['data']['talent']['jobSearchResults']['startups']['edges']:
                    node = edge.get('node', {})
                    if node.get('__typename') == 'StartupSearchResult':
                        job_listing = node.get('highlightedJobListings', [{}])[0]
                        jobs.append({
                            'job_title': job_listing.get('title', 'N/A'),
                            'company_name': node.get('name', 'N/A'),
                            'salary': job_listing.get('compensation', 'N/A'),
                            'company_type' : 'StartupSearchResult'
                        })
                    elif node.get('__typename') == 'PromotedResult':
                        job_node = node.get('promotedStartup', node)
                        job_listing = job_node.get('highlightedJobListings', [{}])[0]
                        jobs.append({
                            'job_title': job_listing.get('title', 'N/A'),
                            'company_name': job_node.get('name', 'N/A'),
                            'salary': job_listing.get('compensation', 'N/A'),
                            'company_type' : 'PromotedResult'
                        })
                    elif node.get('__typename') == 'FeaturedStartups':
                        for featured_job in node.get('featuredStartups', []):
                            job_node = featured_job.get('promotedStartup', featured_job)
                            job_listing = job_node.get('highlightedJobListings', [{}])[0]
                            jobs.append({
                                'job_title': job_listing.get('title', 'N/A'),
                                'company_name': job_node.get('name', 'N/A'),
                                'salary': job_listing.get('compensation', 'N/A'),
                                'company_type' : 'FeaturedStartups'
                            })
                 
                # return final result            
                return jobs
                
            except json.JSONDecodeError as e:
                # first hit endpoint -> /graphql -> data encoded (br) -> json()
                # subsequent req -> you dont need to decode it
                # binary / br 
                print("JSON Decode Error , attempting brotli decoding")
                decompressed_data = brotli.decompress(response.content)
                data = json.loads(decompressed_data)
                print('decompressed data : ',data) 
                return False          

        except requests.RequestException as e:
            print(f"Error fetching jobs: {e}")
            return False
    
    def send_message(
        self, 
        userMessage : str
    ) -> List[Dict]:
        # GraphQL payload to send
        payload = {
            "operationName": "CandidateSendMessage",
            "variables": {
                "input": {
                    "id": "965987617",
                    "type": "JOBPAIRING",
                    "body": userMessage
                }
            },
            "extensions": {
                "operationId": "tfe/1ee8d94da36a0811d05340d91a4427175dbb8abfafe2dab802483d375fdcfb7d"
            }
        }

        try:
            # sending http request with graphql payload
            response = requests.post(
                "https://wellfound.com/graphql",
                json=payload,
                headers=self.headers,
                cookies=self.cookies
            )
            response.raise_for_status()
            
            data = response.json()
            
            if(response.status_code == 200 or response.status_code == 201):
                return data 

        except requests.RequestException as e:
            print(f"Error sending messages: {e}")
            return False

    
    def get_all_messages(
        self
    ) -> List[Dict]:
        # GraphQL payload to send
        payload = {
            "operationName": "ConversationModal",
            "variables": {
                "id": "965987617",
                "type": "JOBPAIRING"
            },
            "extensions": {
                "operationId": "tfe/c53fe96a11cd1ea9563628fa1f30097ea8c80ba3867a81b486e77d400e3fb7da"
            }
        }

        try:
            # sending http request with graphql payload
            response = requests.post(
                "https://wellfound.com/graphql",
                json=payload,
                headers=self.headers,
                cookies=self.cookies
            )
            response.raise_for_status()
            
            data = response.json()
            
            if(response.status_code == 200 or response.status_code == 201):
                return data 

        except requests.RequestException as e:
            print(f"Error sending messages: {e}")
            return False



