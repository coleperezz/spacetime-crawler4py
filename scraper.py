import re
from urllib.parse import urlparse, urldefrag,urljoin,urlunparse
from bs4 import BeautifulSoup
from nltk.tokenize import RegexpTokenizer

# Need to Use a Tuple so it is saved across files
longestPage = (float('-inf'), "")
seenURLS = set()
word_count = {}
stop_words = set(line.strip() for line in open('stopwords.txt'))
icsSubdomains = {}


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    global longestPage
    global wordCount
    global stop_words

    if resp.status != 200 or resp.raw_response.content == None:
        return list()

    soup = BeautifulSoup(resp.raw_response.content, 'html5lib')

    #get rid of script and style content from the raw response
    for tag in soup(["script", "style"]):
        tag.extract()

    tokenizer = RegexpTokenizer(r'[a-zA-Z]{3,}')

    tokens = tokenizer.tokenize(soup.get_text().lower())

    # Removes low information pages from scraper
    if len(tokens) < 100: 
        return list()

    pageWords = float('-inf') # Used to find page with most words minus stop words
    for word in tokens:
        #filters out stopwords
        if word not in stop_words:
            pageWords += 1
            if word in word_count:
                word_count[word] += 1
            else:
                word_count[word] = 1

    if pageWords > longestPage[0]:
        longestPage = (pageWords, url)
        with open('report.txt','r') as f:
            data = f.readlines()
        data[1] = (f"The Longest Page is {longestPage[1]}\n")
        data[2] = (f"The longest Page has {longestPage[0]} words\n")

        with open('report.txt','w') as f:
            f.writelines(data)

    links = []
    for link in soup.find_all("a", attrs={'href': re.compile("^http://|^https://")}):
        links.append(link.get('href'))

    return links

def is_valid(url):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    url = urldefrag(url).url
    global seenURLS
    global icsSubdomains
    parsed = urlparse(url)
    try:
        validSubDomain = re.match(
            ".*(\.cs\.uci\.edu\/|\.informatics\.uci\.edu\/|\.stat\.uci\.edu\/|\.ics\.uci\.edu\/).*|.*today\.uci\.edu\/department\/information_computer_sciences\/.*", url)

        if not validSubDomain:
            return False

        if url in seenURLS:
            return False

        # Looks for the subdomains, ensures it is not www.ics.uci.edu
        if re.match(".*(\.ics\.uci\.edu)(?<!www.ics.uci.edu)", parsed.netloc):
            subdomain = parsed.netloc.split(".")[0]
            if subdomain in icsSubdomains:
                icsSubdomains[subdomain] += 1
            else:
                icsSubdomains[subdomain] = 1

        seenURLS.add(url)
        # Writes the number of Unique URLS
        with open('report.txt','r') as file:
            data = file.readlines()
        data[0] = f'The number of Unique URLS is: {len(seenURLS)}\n'
        with open('report.txt','w') as file:
            file.writelines(data)

        print(len(seenURLS))

        return not (re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico|py|java|c"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|odc|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|ppsx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()) or
            re.match(
            r".*\/(css|js|bmp|gif|jpe?g|ico|py|java|c"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|ppsx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)\/.*$", parsed.path.lower()) or
            re.match(r".*\/page\/\d*", parsed.path.lower()))

    except TypeError:
        print ("TypeError for ", parsed)
        raise
