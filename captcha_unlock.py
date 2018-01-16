import requests
from bs4 import BeautifulSoup
import os
from PIL import Image
import re



class CaptchaUnlock():
	def __init__(self, links=[], passwords=['megalinks'], session=requests.Session()):
		'''
		::::CaptchaUnlock initializer::::

		params:: links: (optional) This is a list of snahp.it links from which you want to extract actual links
		params:: passwords: (optional) A list of passwords to try for any snahp.it links that require password verification
		params:: session: (optional) For custom requests.Session() management.

		'''
		self._session = session
		self._snahpit_links = links
		self._passwords = passwords
		self._hidden_links = []

		

	# Some utility functions

	def clear(self):
		"""
		Clear the _hidden_links cache from previous iterations and the _snahpit_links cache.
		"""
		self._hidden_links = []
		self._snahpit_links = []

	def set_snahpit_links(self, links):
		"""
		Add a list of links.snahp.it to iterate over
		"""
		self._snahpit_links = links


	def add_passwords(self, passwords):
		"""
		Add a list of passwords to automatically check against any password protected link

		params:: passwords: A list of passwords
		"""
		self._passwords += passwords

	def clear_passwords(self):
		"""
		Clear the passwords that are checked automatically.
		If there are no passwords, you have manually enter one whenever a passsword protected link occurs
		"""
		self._passwords = []


	def _isLinkPage(self, soup):
		"""
		Utility Function: Checks whether page is Hidden Links page
		"""

		if "Hidden" in soup.find(name='p').text:
			return True
		else:
			return False


	def _isPasswordPage(self, soup):
		"""
		Utility Function: Checks whether page is password page
		"""

		if soup.find(name='input', attrs={'type': 'password'}) != None:
			return True
		else:
			return False

	def _isCaptchaPage(self, soup):
		"""
		Utility Function: Checks whether page is captcha page
		"""

		if len(soup.select("input[id='security_code']"))==0:
			return False
		else:
			return True

	def _handleLinkPage(self, soup):
		"""
		Utility Function: Extracts links from hidden links page
		"""
		
		_hidden = soup.select("center > p > a")
		links = []
		for i in _hidden:
			if re.search(r'^http:\/\/', i.get("href")) != None:
				links.append(i.get("href").replace('\r', '').replace('\n', ''))

		return links

	def _handlePasswordPage(self, link):
		"""
		Utility Function: Cracks password and produces a links page
		"""

		params = {'Pass1': '', 'Submit0': 'Submit'}
		flag = False

		# Try automatic provided passwords
		for i in self._passwords:
			params['Pass1'] = i
			response = self._session.post(link, data=params)
			soup = BeautifulSoup(response.content)
			if self._isLinkPage(soup):
				flag = True
				break

		if flag:
			return self._handleLinkPage(soup)
		else:
			while True:
				# Try passwords taken from user
				print('\nThe following link doesn\'t work with provided passwords:\n{}\n'.format(link))
				password = input('Please provide a new password (leave blank to skip this link): ')
				if password == '':
					print('\nSkipping link {}\n'.format(link))
					return []
				params['Pass1'] = password
				response = self._session.post(link, data=params)
				soup = BeautifulSoup(response.content)
				if self._isLinkPage(soup):
					self._passwords.append(password)
					return self._handleLinkPage(soup)

	def _handleCaptchaPage(self, link, soup):
		"""
		Utility Function: Cracks captcha and produces a links page
		"""

		while self._isCaptchaPage(soup):
			params = {'security_code': '', 'submit1': 'Submit'}
			print('\nDownloading captcha image.')
			image_url = "http://links.snahp.it/"+soup.select('form > p > img')[0].get('src')
			f = open('captcha.jpg', 'wb')
			c = self._session.get(image_url)
			if c.status_code == 200:
				f.write(c.content)
			f.close()
			print('Captcha Image has been downloaded to {}\captcha.jpg\n'.format(os.getcwd()))
			p = Image.open('captcha.jpg')
			p.show()
			captcha = input('Please input the captcha: ')
			params['security_code'] = captcha
			response = self._session.post(link, data=params)
			soup = BeautifulSoup(response.content, 'lxml')
			if self._isLinkPage(soup):
				return self._handleLinkPage(soup)
			else:
				print('Captcha verification failed. Trying again ...')


	def crack_captcha(self, link):
		"""
		Finds the hidden links by bypassing captcha.

		params: link -- The snahp.it link
		"""

		response = self._session.get(link)
		# TODO: Add exception handling to this section

		soup = BeautifulSoup(response.content, "lxml")
		if self._isLinkPage(soup):
			self._hidden_links += self._handleLinkPage(soup)
		elif self._isPasswordPage(soup):
			result = self._handlePasswordPage(link)
			if len(result) != 0:
				self._hidden_links += result
			else:
				pass
		else:
			self._hidden_links += self._handleCaptchaPage(link, soup)




	def getCracking(self):
		if len(self._snahpit_links) != 0:
			for i in self._snahpit_links:
				self.crack_captcha(i)
				print('\nExtracted links from: {}'.format(i))

			return self._hidden_links
		else:
			print("\nNo links provided. Use the set_snahpit_links() method to set the links to bypass.")