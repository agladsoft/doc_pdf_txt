import itertools as itt
import datetime as dt

from dataclasses import dataclass
import dataclasses
import heapq
import re
import numpy as np


import fuzzywuzzy.fuzz
from fuzzywuzzy import process


class Paragraph(object):
    def __init__(self, symbols, position, nbrs, match_paragraph=None):
        self.symbols = symbols
        self.symbols_count = len(self.symbols)
        self.global_position = position[0]
        self.token_borders = self._get_cleaned_token_borders()
        self.tokens = self._get_tokens(3)
        self.tokens_count = len(self.tokens)
        self.prev = nbrs[0]
        self.next = nbrs[1]
        self.match_paragraph = match_paragraph

    def _clean_symbols(self, symbols):
        #TODO: Why unification lead to bad compare results?
        new_symbols = re.sub(r"\s{2,}", " ", symbols)
        new_symbols += " "
        new_symbols = re.sub(r"\s+$", "\n", new_symbols)
        return new_symbols

    def _get_cleaned_token_borders(self):
        token_borders = list(self._get_token_borders())
        # token_borders2 = list(self._clean_token_borders(token_borders))
        return token_borders

    def _get_token_borders(self):
        splitter = " "
        j = 0
        yield 0
        while j != -1:
            j = self.symbols.find(splitter, j + 4)
            if j == -1:
                yield len(self.symbols)
            else:
                yield j

    def _clean_token_borders(self, token_borders):
        for a, b in itt.pairwise(token_borders):
            if b - a > 2 or a == 0:
                yield a
        yield b

    def _get_tokens(self, words_count):
        tokens = []
        for i in range(len(self.token_borders)-words_count):
            start = self.token_borders[i]
            end = self.token_borders[i+words_count]
            token = self.symbols[start:end]
            tokens.append(token)
        if not tokens:
            tokens.append(self.symbols)
        return tokens

    def get_token_pos_in_text(self, token):
        start = self.symbols._find_right_tokens(token)
        end = start + len(token)
        return start, end


def paragraph_factory(text):
    """Creates dict[Paragraph] with absolute start position of every paragraph as dict key"""
    prev_p = None
    global_position = 0
    paragraphs = dict()
    text += "\n"  # add empty paragraph because we work with start positions of paragraphs
    for line in text:
        current_p = Paragraph(line, position=(global_position, len(text)), nbrs=(prev_p, None))
        paragraphs[global_position] = current_p
        global_position += len(line)
        if prev_p:
            prev_p.next = current_p
        prev_p = current_p
    return paragraphs


@dataclass
class ChapterSide:
    """One side of chapter"""
    paragraphs: dict[int:Paragraph]
    start_id: int
    end_id: int


@dataclass
class FoundRightToken:
    text: str
    rate: int
    paragraph_id: int
    relative_pos: float


class BorderTokenMatch(object):
    def __init__(self, left_token: str, right_tokens: dict):
        self.left_token = left_token
        self.right_tokens = right_tokens
        self.right_tokens_min_id = min(self.right_tokens.keys())
        self.right_tokens_max_id = max(self.right_tokens.keys())
        self.found_right_tokens = list(self._find_right_tokens())

    def _find_right_tokens(self):
        found_right_tokens_and_rates = process.extract(query=self.left_token,
                                                       choices=self.right_tokens.values(),
                                                       scorer=fuzzywuzzy.fuzz.ratio,
                                                       limit=3)
        for found_right_token, found_right_token_rate in found_right_tokens_and_rates:
            paragraph_id = next((k for k, v in self.right_tokens.items() if v == found_right_token), (None, None))
            yield FoundRightToken(text=found_right_token,
                                  rate=found_right_token_rate,
                                  paragraph_id=paragraph_id,
                                  relative_pos=paragraph_id/self.right_tokens_max_id)


class BorderMatch(object):
    def __init__(self, left_bstart_token, left_bend_token, left_border_pid,
                 right_bstart_tokens, right_bend_tokens, right_chapter):
        self.left_bstart_token = left_bstart_token
        self.left_bend_token = left_bend_token
        self.left_border_pid = left_border_pid
        self.right_bstart_tokens = right_bstart_tokens
        self.right_bend_tokens = right_bend_tokens
        self.right_chapter = right_chapter
        self.bstart_token_match = BorderTokenMatch(left_bstart_token, right_bstart_tokens)
        self.bend_token_match = BorderTokenMatch(left_bend_token, right_bend_tokens)

        self.best_bstart_right_token, \
        self.best_bend_right_token, \
        self.tokens_rate, \
        self.best_char_distance = self._get_best_found_bend_bstart_tokens_and_best_char_distance()
        a = 1
        assert self.best_bend_right_token, "best_bend_right_token is none, no good match found"

        # self.tokens_rate = self._get_tokens_rate()

        self.border_rate = self.tokens_rate / 10 + self.best_char_distance
        a = 1

    def __lt__(self, other):
        return self.border_rate < other.border_rate

    def _get_tokens_rate(self):
        if self.best_bstart_right_token:
            tokens_rate = min(self.best_bstart_right_token.rate,
                              self.best_bend_right_token.rate)
        else:
            tokens_rate = 0.1
        return tokens_rate

    @staticmethod
    def _get_mse_of_found_right_tokens(bs: FoundRightToken, be: FoundRightToken):
        y_true = [100, 100]  # Y_true = Y (original values)
        # Calculated values
        y_pred = [bs.rate, be.rate]  # Y_pred = Y'
        # Mean Squared Error
        mse = np.square(np.subtract(y_true, y_pred)).mean()
        return mse

    def _get_best_found_bend_bstart_tokens_and_best_char_distance(self):
        best_bs = None
        best_be = None
        best_mse = 99999999
        best_char_distance = 99999999
        for bs, be in itt.product(self.bstart_token_match.found_right_tokens,
                                  self.bend_token_match.found_right_tokens):
            char_distance = be.paragraph_id - \
                            bs.paragraph_id - \
                            self.right_chapter.paragraphs[bs.paragraph_id].symbols_count
            mse = self._get_mse_of_found_right_tokens(bs, be)

            if (char_distance >= 0) and (char_distance <= best_char_distance) and (mse < best_mse):
                best_bs, best_be, best_mse, best_char_distance,  = bs, be, mse, char_distance
        a = 1
        return best_bs, best_be, best_mse, best_char_distance


class MatchedChapter(object):
    """Chapter that match left and right side, check and spawn subchapter if possible"""
    def __init__(self, left_chapter: ChapterSide, right_chapter: ChapterSide, nbrs: tuple = (None, None),
                 born_border_match: float = None):
        self.left_chapter = left_chapter
        self.right_chapter = right_chapter
        self.se2_id = (left_chapter.start_id, left_chapter.end_id), (right_chapter.start_id, right_chapter.end_id)
        self.right_bstart_tokens = dict()
        self.right_bend_tokens = dict()
        self._get_right_tokens()
        self.border_matches_heap = self._fill_border_matches_heap()
        self.born_border_match = born_border_match
        self.born_datetime = dt.datetime.now()

        self.prev = nbrs[0]
        self.next = nbrs[1]

    def _get_right_tokens(self, ):
        """
        Fill right_bstart_tokens with tokens that may be in the start of the border.
        And right_bend_tokens with tokens that may be in the end of the border.
        """
        right_p = self.right_chapter.paragraphs[self.right_chapter.start_id]
        while right_p and right_p.global_position <= self.right_chapter.end_id:
            if right_p.global_position != self.right_chapter.end_id:
                self.right_bstart_tokens[right_p.global_position] = right_p.tokens[-1]
            if right_p.global_position != self.right_chapter.start_id:
                self.right_bend_tokens[right_p.global_position] = right_p.tokens[0]
            right_p = right_p.next

    def _fill_border_matches_heap(self):
        border_matches_heap = []
        left_p = self.left_chapter.paragraphs[self.left_chapter.start_id]
        while left_p.global_position < self.left_chapter.end_id:
            try:
                border_match = BorderMatch(left_bstart_token=left_p.tokens[-1],
                                           left_bend_token=left_p.next.tokens[0],
                                           left_border_pid=left_p.next.global_position,
                                           right_bstart_tokens=self.right_bstart_tokens,
                                           right_bend_tokens=self.right_bend_tokens,
                                           right_chapter=self.right_chapter
                                           )
                heapq.heappush(border_matches_heap, border_match)
            except Exception as e:
                print(f"Error: {e}")
            left_p = left_p.next
        return border_matches_heap

    def spawn_possible(self, thr):
        if not self.border_matches_heap:
            return False
        best_border_match = self.border_matches_heap[0]
        return best_border_match.border_rate <= thr

    def spawn_subchapter(self, border_rate_threshold):
        best_border_match = self.border_matches_heap[0]
        if best_border_match.border_rate <= border_rate_threshold:
            parent_left_chapter = dataclasses.replace(self.left_chapter)
            parent_left_chapter.end_id = parent_left_chapter.paragraphs[best_border_match.left_border_pid].prev.global_position

            parent_right_chapter = dataclasses.replace(self.right_chapter)
            parent_right_chapter.end_id = parent_right_chapter.paragraphs[best_border_match.best_bend_right_token.paragraph_id].prev.global_position

            child_left_chapter = dataclasses.replace(self.left_chapter)
            child_left_chapter.start_id = best_border_match.left_border_pid

            child_right_chapter = dataclasses.replace(self.right_chapter)
            child_right_chapter.start_id = best_border_match.best_bend_right_token.paragraph_id

            parent = MatchedChapter(parent_left_chapter, parent_right_chapter,
                                    nbrs=(self.prev, None), born_border_match=self.born_border_match)
            child = MatchedChapter(child_left_chapter, child_right_chapter,
                                   nbrs=(parent, self.next), born_border_match=best_border_match.border_rate)
            parent.next = child
            if self.prev:
                self.prev.next = parent
            return parent, child
        assert "spawn is not possible"
