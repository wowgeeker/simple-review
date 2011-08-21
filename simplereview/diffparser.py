import re


class UnifiedDiffParser(object):

    def parse(self, unified_diff_string):
        self.files = []
        self._store_lines(unified_diff_string)
        self._parse_files()

    def _store_lines(self, unified_diff_string):
        self._lines = []
        number = 0
        for line in unified_diff_string.split("\n"):
            self._lines.append(Line(number, line))
            number += 1

    def _parse_files(self):
        while self._has_more_lines():
            self._parse_file()

    def _parse_file(self):
        self._parse_file_header()
        self._parse_chunks()

    def _parse_file_header(self):
        self._skip_to_old_file()
        old = self._parse_file_name()
        new = self._parse_file_name()
        self._current_file = DiffFile(old, new)
        self.files.append(self._current_file)

    def _skip_to_old_file(self):
        while not self._get_current_line().startswith("---"):
            self._pop_line()

    def _parse_file_name(self):
        line = self._pop_line().content
        return line[4:]

    def _parse_chunks(self):
        while self._has_more_lines() and self._get_current_line().startswith("@@"):
            self._current_chunk = Chunk(self._pop_line())
            self._current_file.chunks.append(self._current_chunk)
            self._parse_diff_part()

    def _parse_diff_part(self):
        while self._has_more_lines():
            if self._get_current_line().startswith(" "):
                self._parse_context_lines()
            elif self._get_current_line().startswith("-"):
                self._parse_removed_lines()
            elif self._get_current_line().startswith("+"):
                self._parse_added_lines()
            else:
                return

    def _parse_context_lines(self):
        self._parse_lines_starting_with(" ", "context")

    def _parse_removed_lines(self):
        self._parse_lines_starting_with("-", "removed")

    def _parse_added_lines(self):
        self._parse_lines_starting_with("+", "added")

    def _parse_lines_starting_with(self, prefix, type_):
        lines = []
        while self._has_more_lines() and self._get_current_line().startswith(prefix):
            lines.append(self._pop_line())
        self._current_chunk.parts.append(ChunkPart(type_, lines))
    
    def _has_more_lines(self):
        return len(self._lines) > 0

    def _get_current_line(self):
        return self._lines[0].content

    def _pop_line(self):
        return self._lines.pop(0)


class DiffFile(object):

    def __init__(self, old, new):
        self.old = old
        self.new = new
        self.chunks = []


class Chunk(object):

    def __init__(self, line):
        self.line = line
        self.parts = []


class ChunkPart(object):

    def __init__(self, type_, lines):
        self.type_ = type_
        self.lines = lines


class Line(object):
    
    def __init__(self, number, content):
        self.number = number
        self.content = content
