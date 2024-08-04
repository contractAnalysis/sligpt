from tabulate import tabulate

from sligpt.config import color_prefix

bold="\033[1m"


def make_markdown_table(array, align: str =None,header:list=[], title:str=''):
    """
    Args:
        array: The array to make into a table. Mush be a rectangular array
               (constant width and height).
        align: The alignment of the cells : 'left', 'center' or 'right'.
        https://gist.github.com/OsKaR31415/955b166f4a286ed427f667cb21d57bfd
    """
    # make sure every elements are strings
    array = [[str(elt) for elt in line] for line in array]
    # get the width of each column
    widths = [max(len(line[i]) for line in array) for i in range(len(array[0]))]

    # make every width at least 3 colmuns, because the separator needs it
    widths = [max(w, 3) for w in widths]

    # get the widths from the header
    header_widths=[len(ele) for ele in header]

    # update widths based on header_widths
    widths=[max(e1,e2) for e1,e2 in zip(widths,header_widths)]

    if align=='center':
        # center text according to the widths
        array = [[elt.center(w) for elt, w in zip(line, widths)] for line in array]
    elif align=='right':
        # center text according to the widths
        array = [[elt.rjust(w) for elt, w in zip(line, widths)] for line in array]
    else:
        # center text according to the widths
        array = [[elt.ljust(w) for elt, w in zip(line, widths)] for line in array]

    header=[elt.center(w) for elt,w in zip(header,widths)]


    separator_header = '| ' + ' | '.join(['*' * w for w in widths]) + ' |'
    header = '| ' + ' | '.join(header) + ' |'
    header_separator = '| ' + ' | '.join(['-' * w for w in widths]) + ' |'
    separator = '| ' + ' | '.join(['-' * w for w in widths]) + ' |'

    # body of the table
    body = [''] * len(array)  # empty string list that we fill after
    for idx, line in enumerate(array):
        # for each line, change the body at the correct index
        body[idx] = '| ' + ' | '.join(line) + ' |'

    body = '\n'.join(body)
    return "\n##"+title+"\n"+separator_header+"\n"+header + '\n' + header_separator + '\n' + body+ '\n' + separator

def present_as_markdown_table(data,align:tuple=(),header:list=[],title:str="",format:str=""):
    """
    "plain": Plain text table without any separators or borders.
    "simple": Simple grid-based table with a header row and horizontal separator lines.
    "grid": Grid-based table with both vertical and horizontal separator lines.
    "pipe": Markdown-style table with vertical separators using pipes (|).
    "orgtbl": Emacs Org mode table format.
    "tsv": Tab-separated values format.
    "html": HTML table format.
    "mediawiki": MediaWiki table format.
    "latex": LaTeX table format.
    "latex_raw": Raw LaTeX table format (useful for including in LaTeX documents).
    :param data:
    :param aligh:
    :param header:
    :param title:
    :return:
    """

    if format=="":
        fmt_type="grid"
    else:
        fmt_type=format
    if len(align)==0:
        column_align=tuple(['left']*len(header))
    else:
        column_align=align

    print(f'{title}')
    # Generate the table with custom column widths
    table = tabulate(data, headers=header, tablefmt=fmt_type, colalign=column_align, numalign="left", maxcolwidths=30)

    print(table)
