# Simple script to download all blogs from specified blog.sohu.com account
# and save them as a single html file with foldable blog entries

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
            time.sleep(2) # wait for login to complete
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
def get_blog_data(browser, page_count):
    blog_data = []

    for page in range(1, page_count + 1):
        print("Navigating to Page %d..." % page)
        browser.get('http://blog.sohu.com/home/entry/list.htm?page=%d' % page) # blog manager
        time.sleep(0.3)

        cur_data = []
        # blog_link_elements = browser.find_elements_by_xpath('//*[@class="newBlog-list-title"]/a')
        # blog_link_elements = browser.find_elements_by_xpath(
        #     "//a[contains(@href,'http://blog.sohu.com/manage/entry.do?m=edit&id=')]")
        blog_elements = browser.find_elements_by_xpath('//li[@data-blogid]')
        for element in blog_elements:
            # get date
            date = element.find_element_by_xpath('./span[@class="date"]').text
            # get editor url
            link = element.find_element_by_xpath('./span[@class="oper"]/a[@target]').get_attribute('href')
            cur_data.append((link, date))
        
        for data in cur_data:
            print(data)

        print("Blog count on Page %d : %d" % (page, len(cur_data)))
        blog_data += cur_data

    return blog_data

# Fetch blog content. Blog link has to be the editor link.
def get_blog_content(browser, link):
    print("Fetching content from %s..." % link)
    browser.get(link)
    title = browser.find_element_by_id('entrytitle').get_attribute('value')
    tag = browser.find_element_by_id('keywords').get_attribute('value')

    editor_frame = browser.find_element_by_xpath('//*[@id="ifrEditorContainer"]/div/iframe')
    browser.switch_to.frame(editor_frame) # switch to editor virtual document
    body = browser.find_element_by_xpath('/html/body')
    print("Fetched content: title = %s, tag = %s" % (title, tag))
    
    return title, tag, body

def main():
    with open('config.json', 'r') as file:
        config = json.load(file)
    
    account     = config['account']
    password    = config['password']
    driver_path = config['driver_path']
    blog_home   = config['blog_home']

    browser = get_browser(driver_path, mode="eager") # can continue once page becomes interactive
    login(browser, blog_home, account, password)
    data = get_blog_data(browser, get_page_count(browser))
    browser.quit()

    browser = get_browser(driver_path) # back to normal mode - wait for page to be fully loaded
    login(browser, blog_home, account, password)

    with open('blog_content.html', 'w') as file:
        file.write('<html>\n')
        file.write('<body>\n')
        for link, date in data:
            while True:
                try:
                    title, tag, body = get_blog_content(browser, link)
                    break
                except: # might run into exception when failed to load captcha image
                    time.sleep(2)

            file.write('<details><summary>%s&nbsp;&nbsp;&nbsp;&nbsp;%s</summary>\n' % (date, title))
            file.write('<p>标签:&nbsp;&nbsp;%s<br></p>\n' % tag)
            file.write(body.get_attribute('innerHTML'))
            file.write('<br>\n')
            file.write('</details>\n')
            print("Content written to file for blog %s %s" % (date, title))

        file.write('</body>\n')
        file.write('</html>\n')
        browser.quit()
        print("Finished.")

if __name__ == '__main__':
    main()

