#!/usr/bin/env python3
"""
Static Website Generator

A simple static website generator that converts Markdown files to HTML
with configurable templates and directory structure.
"""

import os
import sys
import shutil
import yaml
import markdown
import logging
import PyRSS2Gen
from html import escape
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Post:
    title: str
    date: datetime
    path: str
    content: str

    def __post_init__(self):
        if isinstance(self.date, str):
            try:
                self.date = datetime.strptime(self.date, '%Y-%m-%d')
            except ValueError:
                logger.warning(f"Invalid date format for post '{self.title}': {self.date}")
                self.date = datetime.now()


class WebsiteGenerator:

    def __init__(self, config_path: str = 'config.yml'):
        self.config = self._load_config(config_path)
        self._validate_config()
        self._setup_directories()
        self._markdown = markdown.Markdown(extensions=['extra', 'codehilite'])
        self._nav_links: str = ''
        self._header_template: str = self._read_file(self.config['templates']['header'])
        self._footer_template: str = self._read_file(self.config['templates']['footer'])

    # -------------------------------------------------------------------------
    # Configuration
    # -------------------------------------------------------------------------

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                logger.info(f"Configuration loaded from {config_path}")
                return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            logger.error(f"Error parsing configuration: {e}")
            sys.exit(1)

    def _validate_config(self) -> None:
        required_keys = ['website_url', 'website_name', 'author', 'directories', 'files', 'misc', 'templates']
        for key in required_keys:
            if key not in self.config:
                logger.error(f"Missing required configuration key: {key}")
                sys.exit(1)

        required_file_keys = [
            ('files', 'root_index'),
            ('templates', 'header'),
            ('templates', 'footer'),
        ]
        for section, key in required_file_keys:
            path = self.config.get(section, {}).get(key)
            if not path:
                logger.error(f"Missing required configuration key: {section}.{key}")
                sys.exit(1)
            if not os.path.exists(path):
                logger.error(f"Required file not found: {path}")
                sys.exit(1)

        # Optional files: warn but continue
        blog_index = self.config['files'].get('blog_index')
        if blog_index and not os.path.exists(blog_index):
            logger.warning(f"blog_index not found, blog list page will be skipped: {blog_index}")

    def _setup_directories(self) -> None:
        output = self.config['directories']['output']
        Path(output).mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------------------
    # I/O helpers
    # -------------------------------------------------------------------------

    def _read_file(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except (FileNotFoundError, IOError, UnicodeDecodeError) as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise

    def _write_file(self, file_path: str, content: str) -> None:
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.debug(f"Written: {file_path}")
        except (IOError, OSError) as e:
            logger.error(f"Error writing file {file_path}: {e}")
            raise

    # -------------------------------------------------------------------------
    # Markdown / templating
    # -------------------------------------------------------------------------

    def _markdown_convert(self, content: str) -> str:
        self._markdown.reset()
        return self._markdown.convert(content)

    def _base_template_vars(self) -> Dict[str, str]:
        rss_filename = self.config['misc'].get('rss_filename', 'rss.xml')
        return {
            'WEBSITE_NAME': self.config['website_name'],
            'WEBSITE_URL': self.config['website_url'],
            'AUTHOR': self.config['author'],
            'RSS_URL': f"/{rss_filename}",
            'SOURCE_URL': self.config.get('source_url', ''),
            'NAV_HOME': self.config['misc'].get('nav_home', 'Home'),
            'NAV_LINKS': self._nav_links,
            'CONTACT_URL': self.config['misc'].get('contact_url', '/contact'),
        }

    def _build_nav(self, pages_dir: str, blog_dir: str) -> None:
        """Pre-scan pages directory and build navigation HTML stored on self._nav_links.

        Nav order: all pages (including blog index if it has posts) sorted alphabetically.
        """
        blog_index = self.config['files'].get('blog_index')
        blog_has_posts = bool(blog_dir and os.path.isdir(blog_dir) and any(
            f.endswith('.md') for f in os.listdir(blog_dir)
        ))

        items = []
        if pages_dir and os.path.isdir(pages_dir):
            for filename in sorted(os.listdir(pages_dir)):
                if not filename.endswith('.md'):
                    continue
                file_path = os.path.join(pages_dir, filename)
                # Blog index is a list-page template — link to the blog dir instead,
                # but only if there are actual posts.
                if blog_index and os.path.abspath(file_path) == os.path.abspath(blog_index):
                    if blog_has_posts:
                        try:
                            lines = self._read_file(file_path).splitlines()
                            title = self._extract_title(lines)
                            items.append(f'<li><a href="/{blog_dir}">{escape(title)}</a></li>')
                        except Exception as e:
                            logger.warning(f"Could not read nav title from {file_path}: {e}")
                    continue
                try:
                    lines = self._read_file(file_path).splitlines()
                    title = self._extract_title(lines)
                    slug = os.path.splitext(filename)[0]
                    items.append(f'<li><a href="/{slug}">{escape(title)}</a></li>')
                except Exception as e:
                    logger.warning(f"Could not read nav title from {file_path}: {e}")

        self._nav_links = '\n\t\t\t\t'.join(items)

    def _apply_template(self, content: str, variables: Dict[str, str]) -> str:
        for key, value in variables.items():
            content = content.replace(f'{{{{{key}}}}}', value)
        return content

    def _render_page(self, body_html: str, title: str) -> str:
        """Wrap body HTML with processed header and footer."""
        template_vars = {**self._base_template_vars(), 'TITLE': title}
        return (
            self._apply_template(self._header_template, template_vars)
            + body_html
            + self._apply_template(self._footer_template, template_vars)
        )

    # -------------------------------------------------------------------------
    # Metadata extraction
    # -------------------------------------------------------------------------

    def _extract_title(self, lines: List[str]) -> str:
        for line in lines[:5]:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
        return 'Untitled'

    def _extract_date(self, lines: List[str]) -> datetime:
        date_patterns = [
            '%d %b %Y', '%d %B %Y',
            '%b %d %Y', '%B %d %Y',
            '%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d',
            '%d-%m-%Y', '%d/%m/%Y', '%d.%m.%Y',
            '%m-%d-%Y', '%m/%d/%Y', '%m.%d.%Y',
        ]
        for line in lines[1:3]:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            for pattern in date_patterns:
                try:
                    return datetime.strptime(line, pattern)
                except ValueError:
                    continue
        logger.warning("No valid date found in post, using current date")
        return datetime.now()

    # -------------------------------------------------------------------------
    # Build steps
    # -------------------------------------------------------------------------

    def convert_markdown_to_html(self, input_directory: str, output_directory: str) -> List[Post]:
        """Convert all markdown files in a directory tree to HTML pages."""
        if not os.path.exists(input_directory):
            logger.warning(f"Input directory does not exist: {input_directory}")
            return []

        designated = {
            os.path.abspath(p)
            for p in [self.config['files'].get('blog_index')]
            if p
        }

        posts = []
        for root, _, files in os.walk(input_directory):
            for file in sorted(files):
                if not file.endswith('.md'):
                    continue

                file_path = os.path.join(root, file)
                if os.path.abspath(file_path) in designated:
                    continue

                try:
                    md_content = self._read_file(file_path)
                    lines = md_content.splitlines()
                    title = self._extract_title(lines)
                    date = self._extract_date(lines)
                    html_content = self._markdown_convert(md_content)

                    relative_path = os.path.splitext(os.path.relpath(file_path, input_directory))[0]
                    output_file = os.path.join(output_directory, relative_path, 'index.html')

                    self._write_file(output_file, self._render_page(html_content, title))

                    posts.append(Post(
                        title=title,
                        date=date,
                        path=relative_path + '/',
                        content=html_content,
                    ))
                    logger.info(f"Processed: {file_path} -> {output_file}")

                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")

        return posts

    def generate_index_page(self, posts: List[Post]) -> None:
        """Generate the main index page.

        Place <!-- RECENT_POSTS --> anywhere in index.md to control where the
        recent-posts list is injected. If the marker is absent the list is
        appended after the page content.
        """
        root_content = self._read_file(self.config['files']['root_index'])
        lines = root_content.splitlines()
        title = self._extract_title(lines)
        body_html = self._markdown_convert(root_content)

        blog_dir = self.config['directories'].get('blog')
        if posts and blog_dir:

            posts_count = self.config['misc'].get('recent_posts_count', 5)
            recent = sorted(posts, key=lambda p: p.date, reverse=True)[:posts_count]

            recent_html = '<ul class="blog">\n'
            for post in recent:
                date_str = post.date.strftime("%d %b %Y")
                recent_html += f'<li><span>{date_str}</span><a href="/{blog_dir}/{post.path}">{escape(post.title)}</a></li>\n'
            recent_html += '</ul>\n'
            recent_html += f'<p><a href="/{blog_dir}">View all blog posts &rarr;</a></p>\n'

            marker = '<!-- RECENT_POSTS -->'
            if marker in body_html:
                body_html = body_html.replace(marker, recent_html)
            else:
                body_html += recent_html

        output_path = os.path.join(self.config['directories']['output'], 'index.html')
        self._write_file(output_path, self._render_page(body_html, title))
        logger.info(f"Generated index page: {output_path}")

    def generate_list_page(self, posts: List[Post], content_type: str,
                            index_file_key: str, output_subdir: str) -> None:
        """Generate a list page for any content type (blog, projects, etc.)"""
        index_file = self.config['files'].get(index_file_key)
        if not index_file or not os.path.exists(index_file):
            logger.warning(f"Index file for '{content_type}' not found, skipping list page")
            return

        index_md = self._read_file(index_file)
        title = self._extract_title(index_md.splitlines())
        body_html = self._markdown_convert(index_md)

        if posts:
            sorted_posts = sorted(posts, key=lambda p: p.date, reverse=True)
            body_html += f'<ul class="{content_type}">\n'
            for post in sorted_posts:
                date_str = post.date.strftime("%d %b %Y")
                body_html += f'<li><span>{date_str}</span><a href="/{output_subdir}/{post.path}">{escape(post.title)}</a></li>\n'
            body_html += '</ul>\n'

        output_path = os.path.join(self.config['directories']['output'], output_subdir, 'index.html')
        self._write_file(output_path, self._render_page(body_html, title))
        logger.info(f"Generated {content_type} list page: {output_path}")

    def generate_rss(self, posts: List[Post]) -> None:
        """Generate RSS feed from posts."""
        if not posts:
            logger.warning("No posts found, skipping RSS generation")
            return

        posts_dir = self.config['directories']['blog']
        items = []
        for post in posts:
            date = post.date.replace(hour=12, minute=0, second=0, microsecond=0)
            items.append(PyRSS2Gen.RSSItem(
                title=post.title,
                link=f"{self.config['website_url']}/{posts_dir}/{post.path}",
                description=post.content,
                pubDate=date,
            ))

        items.sort(key=lambda x: x.pubDate, reverse=True)
        rss_limit = self.config['misc'].get('rss_post_limit', 20)
        items = items[:rss_limit]

        rss = PyRSS2Gen.RSS2(
            title=f"{self.config['website_name']} RSS Feed",
            link=self.config['website_url'],
            description=f"The official RSS Feed for {self.config['website_url']}",
            lastBuildDate=datetime.now(),
            items=items,
        )

        rss_filename = self.config['misc'].get('rss_filename', 'rss.xml')
        rss_file = os.path.join(self.config['directories']['output'], rss_filename)
        with open(rss_file, 'wb') as f:
            rss.write_xml(f, encoding='utf-8')
        logger.info(f"Generated RSS feed: {rss_file} ({len(items)} items)")

    def build(self) -> None:
        """Build the entire website."""
        try:
            logger.info("Starting website build...")

            output = self.config['directories']['output']
            blog_dir = self.config['directories'].get('blog')
            pages_dir = self.config['directories'].get('pages')

            # Build nav before any rendering so all pages can include it
            self._build_nav(pages_dir, blog_dir)

            # Convert static pages
            if pages_dir:
                self.convert_markdown_to_html(pages_dir, output)

            # Convert blog posts
            blog_posts: List[Post] = []
            if blog_dir and os.path.isdir(blog_dir):
                blog_posts = self.convert_markdown_to_html(
                    blog_dir,
                    os.path.join(output, blog_dir),
                )

            # Generate index and blog list
            self.generate_index_page(blog_posts)
            if blog_dir and self.config['files'].get('blog_index'):
                self.generate_list_page(blog_posts, 'blog', 'blog_index', blog_dir)

            # Generate RSS feed
            if self.config['misc'].get('generate_rss', True) and blog_posts:
                self.generate_rss(blog_posts)

            # Copy static assets
            public_dir = self.config['directories'].get('public', 'public')
            if os.path.isdir(public_dir):
                shutil.copytree(public_dir, os.path.join(output, public_dir), dirs_exist_ok=True)
                logger.info(f"Copied static assets: {public_dir} -> {output}/{public_dir}")

            logger.info(f"Website build completed successfully! Output: {output}")

        except Exception as e:
            logger.error(f"Website build failed: {e}")
            sys.exit(1)


def main():
    try:
        WebsiteGenerator().build()
    except KeyboardInterrupt:
        logger.info("Build interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
