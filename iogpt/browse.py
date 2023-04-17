from selenium import webdriver

# Open a browser
def browse_dynamic_page(url):
    driver = webdriver.Chrome()
    driver.get(url)
    driver.implicitly_wait(10)
    elements = driver.find_elements_by_xpath("//*[contains(text(), '')]")
    text_content = []
    for element in elements:
        text = element.text.strip()
        if text:
            text_content.append(text)
    print(text_content)
    driver.quit()
    return '\n'.join(text_content)
