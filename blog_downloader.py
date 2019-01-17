# Simple script to download all blogs from specified blog.sohu.com account
# and save them as a json file

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import re, time, json

# Establish connection
def get_browser(executable_path, mode="normal"):
    caps = DesiredCapabilities().FIREFOX
    caps["pageLoadStrategy"] = mode
    browser = webdriver.Firefox(capabilities=caps, executable_path=executable_path)
    return browser

# Log in
def login(browser, url, account, password):
    print("Logging in...")
    browser.get(url)
    while True:
        try:
            browser.find_element_by_xpath('//*[@id="sideBar_btn"]/a[1]').click()
            browser.find_element_by_name('account').send_keys(account)
            browser.find_element_by_name('password').send_keys(password)
            browser.find_element_by_id('login_toolbar').click()
            time.sleep(3) # wait for login to complete
            break
        except:
            time.sleep(0.5)
    print("Done.")

# Parse the page text section and find the number of total pages
def get_page_count(browser):
    page_count_text = browser.find_element_by_id('pageText').text
    page_count = 0
    numbers = re.findall("[0-9]+", page_count_text)
    if numbers is not None:
        page_count = int(numbers[0])
        print("Total number of pages: %d" % page_count)
    else:
        raise "Illegal page count"
    return page_count

# Fetch all blog links and dates, from blog manager page, because some blogs might have been 
# filtered and hidden, which are only visible through blog manager
def get_blog_link_date(browser, page_count, reverse=False):
    link_date = []

    for page in range(1, page_count + 1):
        print("Navigating to Page %d..." % page)
        browser.get('http://blog.sohu.com/home/entry/list.htm?page=%d' % page) # blog manager
        time.sleep(0.3)

        count = 0
        # blog_link_elements = browser.find_elements_by_xpath('//*[@class="newBlog-list-title"]/a')
        # blog_link_elements = browser.find_elements_by_xpath(
        #     "//a[contains(@href,'http://blog.sohu.com/manage/entry.do?m=edit&id=')]")
        blog_elements = browser.find_elements_by_xpath('//li[@data-blogid]')
        for element in blog_elements:
            # get date
            date = element.find_element_by_xpath('./span[@class="date"]').text
            # get editor url
            link = element.find_element_by_xpath('./span[@class="oper"]/a[@target]').get_attribute('href')
            entry = (link, date)
            link_date.append(entry)
            count += 1
            print(entry)

        print("Blog count on Page %d : %d" % (page, count))

    if reverse:
        link_date.reverse()
    
    return link_date

# Fetch blog content. Blog link has to be the editor link.
def get_blog_content(browser, link):
    print("Fetching content from %s..." % link)
    browser.get(link)
    title = browser.find_element_by_id('entrytitle').get_attribute('value')
    tag = browser.find_element_by_id('keywords').get_attribute('value')

    editor_frame = browser.find_element_by_xpath('//*[@id="ifrEditorContainer"]/div/iframe')
    browser.switch_to.frame(editor_frame) # switch to editor virtual document
    body = browser.find_element_by_xpath('/html/body').get_attribute('innerHTML')
    print("Fetched content: title = %s, tag = %s" % (title, tag))
    
    return title, tag, body

def get_blog_data():
    with open('config.json', 'r') as file:
        config = json.load(file)
    
    account     = config['account']
    password    = config['password']
    driver_path = config['driver_path']
    blog_home   = config['blog_home']

    browser = get_browser(driver_path, mode="eager") # can continue once page becomes interactive
    login(browser, blog_home, account, password)
    page_count = get_page_count(browser)
    link_date = get_blog_link_date(browser, page_count, reverse=True)
    browser.quit()

    browser = get_browser(driver_path) # back to normal mode - wait for page to be fully loaded
    login(browser, blog_home, account, password)

    blog_data = []

    for link, date in link_date:
        while True:
            try:
                title, tag, body = get_blog_content(browser, link)
                break
            except: # might run into exception when failed to load captcha image
                time.sleep(2)
        blog_data.append((link, date, title, tag, body))

    browser.quit()
    return blog_data

if __name__ == '__main__':
    blog_data = get_blog_data()
    with open("blog_data.json", "w") as file:
        json.dump(blog_data, file)

