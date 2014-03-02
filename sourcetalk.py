import sublime, sublime_plugin
import os
import webbrowser
import urllib
try:
  import urllib.request
  import urllib.parse
except ImportError:
  pass
try:
  import urllib2
except ImportError:
  pass

class SourcetalkCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    file_content = self.view.substr(sublime.Region(0, self.view.size()))

    try:
      conf_name = os.path.basename(self.view.file_name())
    except AttributeError:
      conf_name = "untitled"

    (row,col) = self.view.rowcol(self.view.sel()[0].begin())

    options = {'conference[file_name]': conf_name,
               'conference[source]': file_content}

    try:
      params_raw = urllib.parse.urlencode(options)
      params = params_raw.encode("utf-8")
    except AttributeError:
      params = urllib.urlencode(options)

    url = "http://app.sourcetalk.net/conferences"
    try:
      req = urllib.request.Request(url, params)
    except AttributeError:
      req = urllib2.Request(url, params)

    response = ""
    try:
      response = urllib.request.urlopen(req)
    except AttributeError:
      response = urllib2.urlopen(req)
    except Exception as e:
      sublime.error_message("failed to create conference")
      print(e)
      return

    webbrowser.open(response.geturl() + "/" + str(row + 1))
