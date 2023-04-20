from fuzzywuzzy import fuzz
from fuzzywuzzy import process

from paragraph import paragraph_factory, MatchedChapter, ChapterSide
import datetime as dt


with open('ruscon_fuzzy/Юристы/Left/paragraphs4.txt') as f:
    left_text = f.readlines()
    left_paragraphs = paragraph_factory(left_text)
    left_head = left_paragraphs[0]

with open('ruscon_fuzzy/Юристы/Right/paragraphs4.txt') as f:
    right_text = f.readlines()
    right_paragraphs = paragraph_factory(right_text)
    right_head = right_paragraphs[0]


left_chapter = ChapterSide(left_paragraphs, 0, next(reversed(left_paragraphs)))
right_chapter = ChapterSide(right_paragraphs, 0, next(reversed(right_paragraphs)))

head_chapter = MatchedChapter(left_chapter, right_chapter)
thr = .1
while thr < 300:
    # current_chapter = head_chapter
    next_chapter = head_chapter
    while next_chapter:
        current_chapter = next_chapter
        next_chapter = next_chapter.next
        while current_chapter.spawn_possible(thr):
            # TODO: how to split by paragraph chapters with bad thr? ...
            #       ... use all tokens as possible border_start and border_end
            # TODO: use thr according to history of mse not passed thr recently
            parent_chapter, child_chapter = current_chapter.spawn_subchapter(thr)
            if current_chapter is head_chapter:
                head_chapter = parent_chapter
            current_chapter = child_chapter

    with open(f'thr_left_{thr}.txt', 'w') as f_left:
        with open(f'thr_right_{thr}.txt', 'w') as f_right:
            write_chapter = head_chapter
            while write_chapter:
                header_to_write = "se2_id: {}, born_border_match: {}, timestamp: {}\n".format(
                    write_chapter.se2_id, write_chapter.born_border_match, write_chapter.born_datetime)
                f_left.write(header_to_write)
                f_right.write(header_to_write)

                lines_to_write = ''
                for key, val in write_chapter.left_chapter.paragraphs.items():
                    if key >= write_chapter.left_chapter.start_id and key <= write_chapter.left_chapter.end_id:
                        lines_to_write += val.symbols
                f_left.writelines(lines_to_write)

                lines_to_write = ''
                for key, val in write_chapter.right_chapter.paragraphs.items():
                    if key >= write_chapter.right_chapter.start_id and key <= write_chapter.right_chapter.end_id:
                        lines_to_write += val.symbols
                f_right.writelines(lines_to_write)

                write_chapter = write_chapter.next

    thr = thr * (1 + 0.618)

a = 1


"""


left_p = left_head
right_p = right_head
while True:
    left1_end = left_p.tokens[-1]
    left2_start = left_p.next.tokens[0]

    m1_token, m1_rate = process.extractOne(left1_end, right_p.tokens)
    end1_a, end1_z = right_p.get_token_pos_in_text(m1_token)

    m2_token, m2_rate = process.extractOne(left2_start, right_p.tokens)
    start2_a, start2_z = right_p.get_token_pos_in_text(m2_token)

    if m1_rate > 62 and m2_rate > 62:
        if ((start2_a > end1_a) and (start2_a <= end1_z) and (end1_z > start2_a) and (end1_z < start2_z)) \
                or start2_a - end1_z < 5:
            right_p = split_paragraph(right_p, min(start2_a, end1_z), len())
    right_p = right_p.next
    left_p = left_p.next

"""