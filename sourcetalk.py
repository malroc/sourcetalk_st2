import sublime
import sublime_plugin
import os
import webbrowser
import urllib
import json
try:
  import urllib.request
  import urllib.parse
except ImportError:
  pass
try:
  import urllib2
except ImportError:
  pass


def settings():
  return sublime.load_settings("SourceTalk.sublime-settings")


def st_request(path, params = None):
  token = settings().get("sourcetalk_token")
  base_url = (settings().get("sourcetalk_url") or "http://app.sourcetalk.net")
  url = base_url + "/api/v2/" + path + ".json"
  headers = {"AUTHORIZATION": ("Token token=" + token)}

  if params:
    try:
      params_raw = urllib.parse.urlencode(params)
      params = params_raw.encode("utf-8")
    except AttributeError:
      params = urllib.urlencode(params)

  try:
    req = urllib.request.Request(url, params, headers)
  except AttributeError:
    req = urllib2.Request(url, params, headers)

  response = None
  try:
    response = urllib.request.urlopen(req)
  except AttributeError:
    response = urllib2.urlopen(req)
  except Exception as e:
    sublime.error_message("Error processing the request")
    print(e)

  return response


def token_exists():
  return bool(settings().get("sourcetalk_token"))


def conference_exists():
  return bool(settings().get("sourcetalk_conference"))


class SourcetalkSetUrlCommand(sublime_plugin.ApplicationCommand):
  def run(self, url):
    settings().set("sourcetalk_url", url)
    sublime.save_settings("SourceTalk.sublime-settings")


class SourcetalkSetTokenCommand(sublime_plugin.ApplicationCommand):
  def run(self, token):
    settings().set("sourcetalk_token", token)
    sublime.save_settings("SourceTalk.sublime-settings")


class SourcetalkPromptSetTokenCommand(sublime_plugin.WindowCommand):
  def run(self):
    self.window.show_input_panel("SourceTalk API Token:",
                                 (settings().get("sourcetalk_token") or ""),
                                 self.on_done,
                                 None,
                                 None)
    pass

  def on_done(self, text):
    sublime.run_command("sourcetalk_set_token", {"token": text})


class SourcetalkChooseConferenceCommand(sublime_plugin.ApplicationCommand):
  def run(self, conference):
    settings().set("sourcetalk_conference", conference)
    sublime.save_settings("SourceTalk.sublime-settings")


class SourcetalkPromptChooseConferenceCommand(sublime_plugin.WindowCommand):
  def run(self):
    response = st_request("users")
    users = json.loads(response.read().decode("utf-8"))
    if len(users):
      login = users[0]["login"]
      response = st_request("users/" + login + "/conferences")
      self.conferences = json.loads(response.read().decode("utf-8"))
      self.window.show_quick_panel([conf["name"] for conf in self.conferences],
                                   self.on_done)
    pass

  def is_enabled(self):
    return token_exists()

  def on_done(self, idx):
    conf = self.conferences[idx]
    path = "users/" + conf["owner"]["login"] + "/conferences/" + conf["slug"]
    sublime.run_command("sourcetalk_choose_conference", {"conference": path})


class SourcetalkCreateFileCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    file_content = self.view.substr(sublime.Region(0, self.view.size()))
    conference_path = settings().get("sourcetalk_conference")

    try:
      conf_name = os.path.basename(self.view.file_name())
    except AttributeError:
      conf_name = "untitled"

    (row, col) = self.view.rowcol(self.view.sel()[0].begin())

    options = {'source_file[name]': conf_name,
               'source_file[source]': file_content,
               'source_file[scroll_position]': str(row + 1)}

    response = st_request(conference_path + "/source_files", options)

    if response:
      sublime.status_message("Sent to " + settings().get("sourcetalk_url"))

  def is_enabled(self):
    return token_exists() and conference_exists()
