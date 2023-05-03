from paragraph import paragraph_factory, chapters_by_token_factory, MatchedChapter, ChapterSide, logger

# logger = logging.getLogger(__name__)
all_m_chapters = dict()


def write_chapters_to_files(head_chapter, filename_prefix):
    text_left = ''
    text_right = ''
    with open(f'{filename_prefix}_left_{thr}.txt', 'w') as f_left:
        with open(f'{filename_prefix}_right_{thr}.txt', 'w') as f_right:
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
                text_left += lines_to_write
                text_left += '\n'

                lines_to_write = ''
                for key, val in write_chapter.right_chapter.paragraphs.items():
                    if key >= write_chapter.right_chapter.start_id and key <= write_chapter.right_chapter.end_id:
                        lines_to_write += val.symbols
                f_right.writelines(lines_to_write)
                text_right += lines_to_write
                text_right += '\n'

                write_chapter = write_chapter.next
    return text_left, text_right


def write_all_m_chapters(prefix):
    with open(f'{prefix}_{thr}.txt', 'w') as f:
        f.write("\n".join([str(kv) for kv in all_m_chapters.items()]))


def spawn_chapters(head_chapter: MatchedChapter):
    next_chapter = head_chapter
    while next_chapter:
        current_chapter = next_chapter
        next_chapter = next_chapter.next
        while current_chapter.spawn_possible(thr):
            logger.info(f'current_chapter is {current_chapter}')
            parent_chapter, child_chapter = current_chapter.spawn_child(thr)
            current_chapter.is_obsolete = True
            all_m_chapters[parent_chapter.se2_id] = parent_chapter
            all_m_chapters[child_chapter.se2_id] = child_chapter

            if current_chapter is head_chapter:
                head_chapter = parent_chapter
            current_chapter = child_chapter
    return head_chapter


def flatten_right_paragraphs_text(head_chapter):
    right_text = ''
    next_chapter = head_chapter
    right_text_by_lines = []

    while next_chapter:
        right_paragraphs = next_chapter.right_chapter.paragraphs
        for pid in right_paragraphs.keys():
            current_paragraph_text = right_paragraphs[pid].symbols
            right_text += current_paragraph_text.replace('\n', ' ')
            if next_chapter and pid == next_chapter.right_chapter.end_id:
                # right_text.replace('\n', '')
                right_text += '\n' if right_text else ''
                right_text_by_lines.append(right_text)
                right_text = ''
                next_chapter = next_chapter.next
    # right_text_by_lines.append('\n')
    return right_text_by_lines


MAX_THR = 200

with open('ruscon_fuzzy/Юристы/Left/paragraphs.txt') as f:
    left_text = f.readlines()
left_paragraphs = paragraph_factory(left_text)
# left_head = left_paragraphs[0]

with open('ruscon_fuzzy/Юристы/Right/Right.txt') as f:
    right_text = f.readlines()
right_paragraphs = paragraph_factory(right_text)
# right_head = right_paragraphs[0]


left_chapter = ChapterSide(left_paragraphs, 0, next(reversed(left_paragraphs)))
right_chapter = ChapterSide(right_paragraphs, 0, next(reversed(right_paragraphs)))

logger.info('MatchedChapter - 1st iteration')
head_chapter = MatchedChapter(left_chapter, right_chapter)
all_m_chapters[head_chapter.se2_id] = head_chapter
thr = .1
while thr < MAX_THR:
    logger.info(f'Next thr cycle started.! thr is {thr}')
    head_chapter = spawn_chapters(head_chapter)
    write_chapters_to_files(head_chapter, 'thr')
    write_all_m_chapters('all_m_chapters')

    thr = thr * (1 + 0.618)


logger.info('flatten_right_paragraphs_text...')
right_text = flatten_right_paragraphs_text(head_chapter)
with open('ruscon_fuzzy/Юристы/Right/flatten_right_paragraphs_text.txt', 'w') as f:
    f.writelines(right_text)
# Build data structeres from the scratch
right_paragraphs = paragraph_factory(right_text)
right_chapter = ChapterSide(right_paragraphs, 0, next(reversed(right_paragraphs)))
head_chapter = MatchedChapter(left_chapter, right_chapter)

all_m_chapters = dict()
all_m_chapters[head_chapter.se2_id] = head_chapter

#       2. run MatchedChapter spawn_subchapter cycle once again
logger.info('MatchedChapter - 2nd iteration')
thr = .1
while thr < MAX_THR:
    head_chapter = spawn_chapters(head_chapter)
    write_chapters_to_files(head_chapter, 'thr2')
    write_all_m_chapters('all_m_chapters2')
    thr = thr * (1 + 0.618)

logger.info('chapters_by_token_factory...')
head_chapter_bt = chapters_by_token_factory(head_chapter)
all_m_chapters = dict()
all_m_chapters[head_chapter_bt.se2_id] = head_chapter_bt

logger.info('MatchedChapterByToken iteration')
thr = .1
while thr < MAX_THR * pow(0.618, 1):
    head_chapter_bt = spawn_chapters(head_chapter_bt)
    left_final, right_final = write_chapters_to_files(head_chapter_bt, 'bt_thr')
    write_all_m_chapters('all_m_chapters_bt')

    thr = thr * (1 + 0.618)
    print(thr)

print(left_final)
print(right_final)