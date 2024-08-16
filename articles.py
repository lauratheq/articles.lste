#!/usr/bin/python3

import os, re, sys
from datetime import datetime
from math import ceil

def register_hooks(lste) -> None:

    # check if we need to do something
    articles_path = f"{lste.content_path}/articles"
    if not os.path.isdir(articles_path):
        return

    lste.hooks.add('load_content', load_articles, 0)
    lste.hooks.add('load_content', load_loop_pages)
    lste.hooks.add('pre_load_custom_functions', fill_loop_pages)

def load_articles(content, lste):

    # set articles path
    articles_path = f"{lste.content_path}/articles"

    # get the active menu
    active_menu = 'index'
    if 'active_menu' in lste.config_file['articles']:
        active_menu = lste.config_file['articles']['active_menu']

    articles = []    
    files = os.listdir(articles_path)
    for file in files:
        filepath = articles_path + '/' + file
        with open(filepath) as handle:
            file_content = handle.read()

        # extract content
        article = {}
        article['content'] = file_content
        
        # excerpt
        excerpt = lste.helpers.extract_excerpt(article['content'])
        excerpt = lste.hooks.apply('excerpt', excerpt, file, lste)
        article['excerpt'] = excerpt

        # basic content
        article['title'] = lste.helpers.extract_title(article['content'])
        content_pattern = r'^(#+)\s*(.*)$'
        article['content'] = re.sub(content_pattern, '', article['content'], count=1, flags=re.MULTILINE)

        # set filemeta
        article['meta'] = {}
        article['is_article'] = '1'

        # extract date and reformat it
        date_pattern = r'^(\d{4}-\d{2}-\d{2})'
        date_match = re.search(date_pattern, file)
        date = date_match.group(1)

        # get date format
        date_format = 'Y-m-d'
        if 'date_format' in lste.config_file['articles']:
            date_format = lste.config_file['articles']['date_format']
        date_format = date_format.replace('d', '%d').replace('m', '%m').replace('Y', '%Y')

        # and convert
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        date = date_obj.strftime(date_format)
        article['meta']['date'] = date

        # get permalink
        permalink = file.replace('.md', '.html')
        article['meta']['permalink'] = permalink

        article['meta']['active-menu'] = active_menu

        # set template
        article['template'] = 'articles-single.html'

        # append content
        content[file] = article

        # set some loop stuff we need later
        articles.append(file)

    # set plugin_vars
    articles.sort()
    articles.reverse()
    lste.plugin_vars['articles'] = {}
    lste.plugin_vars['articles']['articles'] = articles

    # get the loop location
    loop_location = 'index'
    if 'location' in lste.config_file['articles']:
        loop_location = lste.config_file['articles']['location']
    lste.plugin_vars['articles']['loop_location'] = loop_location

    # get the articles per page setting
    articles_per_page = 10
    if 'articles_per_page' in lste.config_file['articles']:
        articles_per_page = int(lste.config_file['articles']['articles_per_page'])
    lste.plugin_vars['articles']['articles_per_page'] = articles_per_page

    # paginate articles
    lste.plugin_vars['articles']['paginated_articles'] = paginate_articles(articles, articles_per_page)

    return content

def load_loop_pages(content, lste):

    # get the loop location
    loop_location = lste.plugin_vars['articles']['loop_location']
    lste.content[loop_location+'.md']['template'] = 'articles-loop.html'
    lste.content[loop_location+'.md']['skip_markdown'] = '1'

    # get the articles per page setting
    articles_per_page = lste.plugin_vars['articles']['articles_per_page']

    # get the amount of articles
    amount_of_articles = len(lste.plugin_vars['articles']['articles'])

    # calc the amount of pages
    amount_of_pages = ceil(amount_of_articles / articles_per_page)

    # copy the location content for the sub pages
    location_content = content[loop_location+'.md']

    # pagination links
    lste.plugin_vars['articles']['pagination_links'] = []
    lste.plugin_vars['articles']['pagination_links'].append(loop_location+'.html')

    # loop the pages
    for page_counter in range(amount_of_pages):
        # skip page zero
        if page_counter == 0:
            continue

        # build the page
        loop_page = dict(location_content)
        new_articles_string = "{{articles_" + f"{page_counter}" + "}}"
        new_excerpts_string = "{{excerpts_" + f"{page_counter}" + "}}"
        loop_page['content'] = loop_page['content'].replace('{{articles}}', new_articles_string)
        loop_page['content'] = loop_page['content'].replace('{{excerpts}}', new_excerpts_string)
        loop_page['template'] = 'articles-loop.html'
        loop_page['skip_markdown'] = '1'

        # filename
        filename = f"{loop_location}_{page_counter}.md"
        content[filename] = loop_page

        # pagination links
        lste.plugin_vars['articles']['pagination_links'].append(filename.replace('.md', '.html'))

    return content

def fill_loop_pages(content, file, lste):

    # get the location
    location = lste.plugin_vars['articles']['loop_location']
    location_file = f"{location}.md"

    # check if the file is an archive
    if location not in file:
        return content
    
    # get the current number of the page
    number_match = re.search(rf'{location}_(\d+)\.md$', file)
    if number_match:
        number = int(number_match.group(1))
    elif file == f'{location}.md':
        number = 0
    
    # check if we need the excerpt or the single template
    contains_excerpts = "{{excerpts}}" in lste.content[location_file]['content']
    template = 'articles-single.html'
    if contains_excerpts:
        template = 'articles-excerpt.html'

    # get the dedicated articles
    concat_articles = ''
    articles = lste.plugin_vars['articles']['paginated_articles'][number]
    for article in articles:

        # load the template
        single_content = lste.templates[template]
        single_content = single_content.replace("{{title}}", lste.content[article]['title'])
        single_content = single_content.replace("{{content}}", lste.content_rendered[article])
        single_content = single_content.replace("{{excerpt}}", lste.content[article]['excerpt'])
        single_content = lste.hooks.apply('single_content', single_content, article, lste)

        concat_articles += single_content

    # place content
    if number == 0:
        content = content.replace('{{articles}}', concat_articles)
        content = content.replace('{{excerpts}}', concat_articles)
    else:
        articles_string ="{{articles_" + f"{number}" + "}}"
        excerpts_string ="{{excerpts_" + f"{number}" + "}}"
        content = content.replace(articles_string, concat_articles)
        content = content.replace(excerpts_string, concat_articles)

    # built up pagination
    # Initialize next_page and previous_page as None
    current_page = file.replace('.md', '.html')

    next_page = None
    previous_page = None

    # Determine next and previous pages
    if current_page in lste.plugin_vars['articles']['pagination_links']:
        # Get the index of the current page
        current_index = lste.plugin_vars['articles']['pagination_links'].index(current_page)
        
        # Determine the next page if it exists
        if current_index < len(lste.plugin_vars['articles']['pagination_links']) - 1:
            next_page = lste.plugin_vars['articles']['pagination_links'][current_index + 1]
        
        # Determine the previous page if it exists
        if current_index > 0:
            previous_page = lste.plugin_vars['articles']['pagination_links'][current_index - 1]

    # Print the appropriate links
    previous_page_link = ''
    next_page_link = ''
    if previous_page:
        previous_page_link = f"<span class='previos-page'><a href='{previous_page}'>&laquo; Previous Page</a></span>";
    if next_page:
        next_page_link = f"<span class='next-page'><a href='{next_page}'>Next Page &raquo;</a></span>";
    pagination = f"<div class='pagination'>{previous_page_link}{next_page_link}</div>"
    content = content.replace('{{pagination}}', pagination)

    return content

def paginate_articles(articles, articles_per_page):
    """
    Paginate a list into chunks of a specified size.

    Args:
        articles (list): The list to paginate.
        articles_per_page (int): The number of articles per page.

    Returns:
        list of lists: A list where each sublist is a page of articles.
    """
    return [articles[i:i + articles_per_page] for i in range(0, len(articles), articles_per_page)]