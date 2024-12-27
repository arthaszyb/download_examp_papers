import requests
import os
import errno
from bs4 import BeautifulSoup

subject_list = ["Maths","Chinese", "English", "Science"] 
grade = "P4"
year_list = ["2019"] # %25 means "all" in ascII
stage_list = ["ca1",'sa1', 'ca2', 'sa2']

subject_choose = subject_list[0]
stage_choose = stage_list[-1] 

#download dir path
download_dir = f"/Users/sean.zhou/Downloads/testpapersfree/{grade}/{subject_choose}/"

#The main domain name
domain_name = "https://www.testpapersfree.com"

def download_pdf(url: str, save_path: str) -> None:
    '''
    Download a PDF from the given URL and save it to the specified path.
    Create the directory if it does not exist.
    '''
    if not os.path.exists(os.path.dirname(save_path)):
        try:
            print("Path does not exist, creating directory: " + save_path)
            os.makedirs(os.path.dirname(save_path))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    response = requests.get(url, timeout=10) # Send a GET request to the URL with a timeout
    
    # Check if the request was successful
    if response.status_code == 200:
        # Write the content of the response to a file'
        file_path = os.path.join(save_path, url.split('/')[-1])
        with open(file_path, 'wb') as pdf_file:
            pdf_file.write(response.content)
        print(f'PDF file has been downloaded and saved as: {file_path}')
    else:
        print(f'Failed to download PDF. Status code: {response.status_code}')

def parse_context(url: str):
    '''
    Parse the HTML content of the given URL using BeautifulSoup and return the parsed content.
    '''
    
    response = requests.get(url, timeout=10) # Send a GET request to the page with a timeout

    # Parse the content of the page with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

#main
if __name__ == "__main__":
    # The URL of the page with the test papers
    for _year in year_list:
        paper_list_url = f'{domain_name}/{stage_choose}/?level={grade}&year={_year}&subject={subject_choose}&type={stage_choose}&school=%25&Submit=Show+Test+Papers'
        # Get all the paper detail page URLs
        paper_list_forms = parse_context(paper_list_url)
        # Find all form tags with action attribute containing 'show.php'
        forms = paper_list_forms.find_all("form", action=lambda x: x and "show.php" in x)
        # Extract the testpaperid from each form's action attribute
        paper_detail_urls = [domain_name + form['action'].lstrip('..') for form in forms]
        if len(paper_detail_urls) == 0:
            print("No exam paper found.") 

        for paper_detail_url in paper_detail_urls:
            # Parse the content of the page with BeautifulSoup
            soup_detail = parse_context(paper_detail_url)
            # Find the download link for the PDF file
            pdf_link = soup_detail.find('a', href=lambda x: x and x.endswith('.pdf'))
            # Extract the href attribute (URL) of the PDF link
            if pdf_link:
                _pdf_url = pdf_link['href']
                pdf_url = domain_name + "/" + _pdf_url
                print(f'Download URL for the PDF file: {pdf_url}')
                download_pdf(pdf_url, download_dir)
            else:
                print(f'No PDF link found for {paper_detail_url}')