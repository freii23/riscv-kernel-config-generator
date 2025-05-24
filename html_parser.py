import requests
from bs4 import BeautifulSoup    


url = 'https://cateee.net/lkddb/web-lkddb/ARCH_MMAP_RND_BITS.html'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

header = str(soup.find('h1'))
print(header)

text = str(soup)
start_pos = text.find('<h2>General informations</h2>')
end_pos = text.find('<h2>Hardware</h2>')

print(text[start_pos:end_pos])

with open(f"config_info.html", "w") as config_info:
    config_info.write(header + text[start_pos:end_pos])

