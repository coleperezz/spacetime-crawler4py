import re
from urllib.parse import urlparse, urldefrag
from bs4 import BeautifulSoup
from nltk.tokenize import RegexpTokenizer

lenLongest = 0
nameMaxLenURL = " "
seenURLS = set()
word_count = {}
stop_words = set(line.strip() for line in open('stopwords.txt'))


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
    global lenLongest
    global nameMaxLenURL
    global wordCount
    global stop_words

    if resp.status != 200 or resp.raw_response.content == None:
        return list()
    if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico|py|java|c"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|ppsx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", resp.raw_response.url):
            return list()

    soup = BeautifulSoup(resp.raw_response.content, 'html5lib')

    #get rid of script and style content from the raw response
    for tag in soup(["script", "style"]):
        tag.extract()

    tokenizer = RegexpTokenizer(r'\w{3,}')

    tokens = tokenizer.tokenize(soup.get_text().lower())
    for word in tokens:
        #filters out stopwords
        if word not in stop_words:
            if word in word_count:
                word_count[word] += 1
            else:
                word_count[word] = 1

    if len(tokens) > lenLongest:
        lenLongest = len(tokens)
        nameMaxLenURL = url

    links = []
    for link in soup.find_all("a", attrs={'href': re.compile("^http://|^https://")}):
        links.append(link.get('href'))
    #
    #print(links)
    return links

def is_valid(url):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    url = urldefrag(url).url
    global seenURLS
    parsed = urlparse(url)
    try:
        validSubDomain = re.match(
            ".*(\.cs\.uci\.edu\/|\.informatics\.uci\.edu\/|\.stat\.uci\.edu\/|\.ics\.uci\.edu\/).*|.*today\.uci\.edu\/department\/information_computer_sciences\/.*", url)

        if not validSubDomain:
            return False

        if url in seenURLS:
            return False

        seenURLS.add(url)
        print(len(seenURLS))

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico|py|java|c"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|ppsx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
