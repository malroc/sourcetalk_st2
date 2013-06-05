import sublime, sublime_plugin
import urllib, urllib2
import os
import webbrowser

class SourcetalkCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		file_content = self.view.substr(sublime.Region(0, self.view.size()))

		conf_name = os.path.basename(self.view.file_name())

		(row,col) = self.view.rowcol(self.view.sel()[0].begin())

		params = urllib.urlencode({'conference[file_name]': conf_name, 'conference[source]': file_content})

		req = urllib2.Request("http://sourcetalk.net/conferences", params)

		response = ""
		try:
			response = urllib2.urlopen(req)
		except Exception as e:
			sublime.error_message("failed to create conference")
			print e
			return

		webbrowser.open(response.geturl() + "/" + str(row + 1))
