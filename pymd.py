import os
import re
import yaml
import shutil
import markdown
from datetime import datetime


# Load configuration
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

site_url = config['site_url']
site_name = config['site_name']
author_name = config['author_name']

pages_dir = config['directories']['pages']
posts_dir = config['directories']['posts']
projects_dir = config['directories']['projects']
public_dir = config['directories']['public']
output_dir = config['directories']['output']
pages_output_dir = config['directories']['pages_output']
posts_output_dir = config['directories']['posts_output']
projects_output_dir = config['directories']['projects_output']

header_file = config['files']['header']
footer_file = config['files']['footer']
root_index_file = config['files']['root_index']
posts_index_file = config['files']['posts_index']
projects_index_file = config['files']['projects_index']

post_count = config['misc']['latest_posts_count']

# Make sure output directories exist
[os.makedirs(dir, exist_ok=True) for dir in (posts_output_dir, pages_output_dir)]

def replace_title_placeholder(header_content, title):
    """
    Replace the title meta tag in the header.html.
    """
    return header_content.replace('<title>{{TITLE}}</title>', f'<title>{title}</title>')

def extract_title_from_md(lines):
    """
    Get the title from each markdown file.
    """
    first_line = lines[0] if lines else None
    if first_line and first_line.startswith('# '):
        return first_line[2:].strip()
    else:
        return 'Blog Post'

def convert_md_to_html(input_directory, output_directory, header_content, footer_content):
    """
    Convert markdown file to HTML file.
    """
    items = []

    for root, _, files in os.walk(input_directory):
        for file in files:
            if file.endswith(".md"):
                path = os.path.join(root, file)
                
                # Read markdown content
                with open(path, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                
                lines = md_content.splitlines()

                # Extract title and date
                title = extract_title_from_md(lines)
                try:
                    date = datetime.strptime(lines[2].strip(), '%Y-%m-%d').date() if len(lines) > 2 else datetime.today().date()
                except Exception:
                    date = datetime.today().date()

                # Convert markdown file to HTML
                html_content = markdown.markdown(md_content)

                # Determine relative path and output directory
                relative_path = os.path.relpath(path, input_directory).replace('.md', '')
                item_dir = os.path.join(output_directory, relative_path)
                output_file = os.path.join(item_dir, 'index.html')
                os.makedirs(item_dir, exist_ok=True)

                # Replace title placeholder in header
                header_content = replace_title_placeholder(header_content, title)
                
                # Write HTML output file
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(header_content + html_content + footer_content)

                # Collect item details
                items.append({
                    'title': title,
                    'date': date,
                    'link': relative_path + '/',
                    'content': html_content
                })

    return items

def generate_index(posts, header_content, footer_content, root_index_file, post_count, output_dir, posts_dir):
    """
    Generate the index page.
    """
    # Read the root index file
    with open(root_index_file, 'r', encoding='utf-8') as f:
        root_index_content = f.read()

    # Extract the title and convert markdown to HTML
    root_title = extract_title_from_md(root_index_content.splitlines())
    root_html = markdown.markdown(root_index_content)

    # Replace title placeholder in header
    header = replace_title_placeholder(header_content, root_title)

    # Start building the index content
    index_content = header + root_html + '<ul class="posts">\n'

    # Add the posts list to the index
    for post in posts[:post_count]:
        index_content += f"<li><span>{post['date']}</span><a href='/{posts_dir}/{post['link']}'>{post['title']}</a></li>\n"

    index_content += f"</ul>\n<p><a href='/{posts_dir}'>View all posts &rarr;</a></p>\n" + footer_content

    # Write the content to the root index file
    output_path = os.path.join(output_dir, 'index.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(index_content)

def generate_full_posts_list(posts, header_content, footer_content, posts_index_file, output_dir, posts_dir):
    """
    Generate the posts page.
    """
    # Read the posts index file
    with open(posts_index_file, 'r', encoding='utf-8') as f:
        posts_index_content = f.read()
 
    # Extract the title and convert markdown to HTML
    posts_title = extract_title_from_md(posts_index_content.splitlines())
    posts_html = markdown.markdown(posts_index_content)

    # Replace title placeholder in header
    header = replace_title_placeholder(header_content, posts_title)

    # Start building the list content
    list_content = header + posts_html + '<ul class="posts">\n'

    # Add the posts to the list
    for post in posts:
        list_content += f"<li><span>{post['date']}</span><a href='/{posts_dir}/{post['link']}'>{post['title']}</a></li>\n"

    list_content += "</ul>\n" + footer_content

    # Write the content to the posts index file
    output_path = os.path.join(output_dir, 'posts/index.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(list_content)

# Read the header content
with open(header_file, 'r', encoding='utf-8') as f:
    header_content = f.read()

# Read the footer content
with open(footer_file, 'r') as f:
    footer_content = f.read()

# Process posts, projects and pages
posts = convert_md_to_html(posts_dir, posts_output_dir, header_content, footer_content)
posts.sort(key=lambda post: post['date'], reverse=True)

projects = convert_md_to_html(projects_dir, projects_output_dir, header_content, footer_content)
projects.sort(key=lambda project: project['date'], reverse=True)

pages = convert_md_to_html(pages_dir, pages_output_dir, header_content, footer_content)

# Generate index and full posts list
generate_index(posts, header_content, footer_content, root_index_file, post_count, output_dir, posts_dir)
generate_full_posts_list(posts, header_content, footer_content, posts_index_file, output_dir, posts_dir)

# Print success message
print(f"Website build successfully in '{output_dir}' folder.")
