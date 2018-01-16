from captcha_unlock import *
import json
import requests

def assure_path_exists(path):
	if not os.path.exists(path):
		os.makedirs(path)

# s = requests.Session()
# # Load all anime posts
# r = requests.get('http://snahp.it/wp-json/wp/v2/posts?categories=3187&per_page=30')
# jobj = json.loads(r.text)
# filtered = []

# for i in jobj:
# 	title = i['title']['rendered']
# 	html = i['content']['rendered']
# 	data = {
# 		'page_title': title
# 	}
# 	soup = BeautifulSoup(html, 'lxml')
# 	data['enumerations'] = []
# 	for i in soup.find_all('a'):
# 		if 'links.snahp.it' in i.get('href'):
# 			t = {
# 				'title': i.text,
# 				'link': i.get('href')
# 			}
# 			data['enumerations'].append(t)

# 	filtered.append(data)

# f = open('anime.json', 'w')
# json.dump(filtered, f)
# f.close()

f = open('anime.json')
k = open('animezippy.json', 'w')
jobj = json.load(f)
result = []
main_root = os.getcwd()
c = CaptchaUnlock([])
for i in jobj:
	current_root = os.path.join(main_root, i['page_title'])
	assure_path_exists(current_root)
	for j in i['enumerations']:
		print(j['link'])
		c.set_snahpit_links([j['link']])
		links = c.getCracking()
		if len(links) != 0:
			now_root = os.path.join(current_root, j['title'])
			assure_path_exists(now_root)
			p = open(os.path.join(now_root, 'zippy.txt'), 'w')

			for i in links:
				p.write('{}\n'.format(i))
			p.close()
		c.clear()

f.close()
k.close()

