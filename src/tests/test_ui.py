from selenium import webdriver

def test_ui():
    d = webdriver.Chrome()
    d.get("http://localhost:5000")
    d.quit()