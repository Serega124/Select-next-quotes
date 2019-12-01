import sublime
import sublime_plugin
#import time


# TODO: multiple selections
class SelectNextQuotesCommand(sublime_plugin.TextCommand):
  def run(self, edit, char='"', move_forward=True, jumps=1):
    #start = time.time()
    # ---------------------------------------
    if jumps < 1:
      return
    region = None
    for i in range(1, jumps + 1):
      if region == None:
        cursor_point = self.view.sel()[0].end()
      else:
        cursor_point = region.end()
      if move_forward:
        region = self.find_forward(char, cursor_point)
      else:
        region = self.find_prev(char, cursor_point)
    if region == None:
      return
    self.view.sel().clear()
    self.view.sel().add(region)
    # ---------------------------------------
    #end = time.time()
    #print("perf:")
    #print(end - start)

  def find_forward(self, char, cursor_point):
    region = self.find_region_forward(char, cursor_point)
    if self.is_start(region):
      #print("debug: reached end of text buffer")
      return
    return region

  def find_prev(self, char, cursor_point, flags=0):
    region = self.find_region_prev(char, cursor_point)
    if self.is_start(region):
      #print("debug: reached start of text buffer")
      return
    return region

  def find_region_forward(self, char, cursor_point):
    return self.view.find("(?<={0})([^{0}]*)(?={0})".format(char), cursor_point)

  def is_start(self, region):
    return (region.a == -1 and region.b == -1)

  def search_in_range(self, what, start, end, flags=0):
    match = self.view.find(what, start, flags)
    if match and ((match.begin() >= start) and (match.end() <= end)):
      return True

  def reverse_search(self, what, cursor_point, flags=0):
    ''' binary search '''
    last_match = None
    lo = 0
    hi = cursor_point
    while True:
      middle = int((lo + hi) / 2)
      # Don't search forever the same line.
      last_match = sublime.Region(lo, hi)
      if last_match and last_match.size() <= len(what):
        return last_match.begin()
      if self.search_in_range(what, middle, hi, flags):
        lo = middle
      elif self.search_in_range(what, lo, middle, flags):
        hi = middle
      else:
        return -1

  def find_region_prev(self, char, cursor_point):
    pos = self.reverse_search(char, cursor_point)
    if pos != -1:
      pos = self.reverse_search(char, pos)
      if pos != -1:
        return self.view.find("(?<={0})([^{0}]*)(?={0})".format(char), pos)
    return sublime.Region(-1, -1)
