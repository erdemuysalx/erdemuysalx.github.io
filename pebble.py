#!/usr/bin/env python3
"""
pebble — static website generator

Converts Markdown source files to a structured HTML website with configurable
templates, a project carousel, blog post listing, and RSS feed.
"""

import os
import re
import sys
import shutil
import yaml
import markdown
import logging
import PyRSS2Gen
from html import escape
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, field_validator


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------

_DATE_PATTERNS = [
    '%d %b %Y', '%d %B %Y',
    '%b %d %Y', '%B %d %Y',
    '%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d',
    '%d-%m-%Y', '%d/%m/%Y', '%d.%m.%Y',
    '%m-%d-%Y', '%m/%d/%Y', '%m.%d.%Y',
]


def _try_parse(s: str, pattern: str) -> Optional[datetime]:
    try:
        return datetime.strptime(s, pattern)
    except ValueError:
        return None


def _is_date_string(s: str) -> bool:
    return any(_try_parse(s, p) is not None for p in _DATE_PATTERNS)


# ---------------------------------------------------------------------------
# Project metadata keys — single source of truth used by parser and stripper
# ---------------------------------------------------------------------------

_PROJECT_META_KEYS: Tuple[str, ...] = ('GitHub', 'Paper', 'Image', 'Sprite', 'Order')

# Lines to scan after the title for dates and project metadata.
_PREAMBLE_SEARCH_DEPTH: int = 12


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class Project(BaseModel):
    title: str
    date: datetime
    path: str
    description: str = ''
    image: Optional[str] = None
    github: Optional[str] = None
    paper: Optional[str] = None
    sprite: Optional[str] = None
    order: Optional[int] = None


class Post(BaseModel):
    title: str
    date: datetime
    path: str
    content: str

    @field_validator('date', mode='before')
    @classmethod
    def parse_date(cls, v: Any) -> datetime:
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            for pattern in _DATE_PATTERNS:
                try:
                    return datetime.strptime(v, pattern)
                except ValueError:
                    continue
            logger.warning(f"Invalid date string: {v!r}, falling back to now()")
            return datetime.now()
        return v


# ---------------------------------------------------------------------------
# Sort helpers
# ---------------------------------------------------------------------------

def _project_sort_key(p: Project) -> Tuple:
    """Primary: explicit order (absent → last). Secondary: newest-first by date."""
    return (p.order if p.order is not None else 10000, -p.date.timestamp())


# ---------------------------------------------------------------------------
# MetadataParser — pure, stateless preamble extraction
# ---------------------------------------------------------------------------

class MetadataParser:
    """Extract structured data from Markdown preamble lines.

    All methods are pure (no I/O, no side effects) and operate on already-read
    content, making them straightforward to test in isolation.
    """

    def extract_title(self, lines: List[str]) -> str:
        for line in lines[:5]:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
        return 'Untitled'

    def extract_date(self, lines: List[str]) -> datetime:
        """Search the first several non-blank, non-heading lines after the title."""
        for line in lines[1:_PREAMBLE_SEARCH_DEPTH]:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            for pattern in _DATE_PATTERNS:
                result = _try_parse(line, pattern)
                if result is not None:
                    return result
        logger.warning("No valid date found, using current date")
        return datetime.now()

    def extract_project_meta(
        self, lines: List[str]
    ) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str], Optional[int]]:
        """Parse GitHub, Paper, Image, Sprite, and Order fields from a project preamble."""
        values: Dict[str, Any] = {k.lower(): None for k in _PROJECT_META_KEYS}
        for line in lines[1:_PREAMBLE_SEARCH_DEPTH]:
            s = line.strip()
            for key in _PROJECT_META_KEYS:
                m = re.match(rf'^{key}:\s*(\S+)', s, re.IGNORECASE)
                if m:
                    attr = key.lower()
                    raw = m.group(1)
                    if attr == 'order':
                        try:
                            values[attr] = int(raw)
                        except ValueError:
                            pass
                    else:
                        values[attr] = raw
                elif re.match(rf'^{key}:\s*$', s, re.IGNORECASE):
                    logger.debug(f"Metadata key '{key}' present but has no value")
        return (
            values['github'], values['paper'], values['image'],
            values['sprite'], values['order'],
        )

    def strip_project_meta_lines(self, md_content: str) -> str:
        """Remove date and all project metadata key lines from the preamble.

        Only strips before the first non-metadata content line so identical
        text later in the body is preserved.
        """
        key_pattern = re.compile(
            r'^(' + '|'.join(_PROJECT_META_KEYS) + r'):', re.IGNORECASE
        )
        lines = md_content.splitlines()
        filtered = []
        preamble_done = False
        for i, line in enumerate(lines):
            if i == 0:
                filtered.append(line)
                continue
            if not preamble_done:
                s = line.strip()
                if key_pattern.match(s) or (s and _is_date_string(s)):
                    continue
                if s:
                    preamble_done = True
            filtered.append(line)
        return '\n'.join(filtered)

    def extract_description(self, html_content: str) -> str:
        """Return plain text of the first prose paragraph in rendered HTML.

        Skips paragraphs that are bare date strings or contain only injected
        metadata markup. Strips a leading "Abstract:" label.
        """
        for m in re.finditer(r'<p(?:[^>]*)>(.*?)</p>', html_content, re.DOTALL):
            text = re.sub(r'<[^>]+>', '', m.group(1)).strip()
            if text and not _is_date_string(text):
                text = re.sub(r'^abstract\s*:\s*', '', text, flags=re.IGNORECASE)
                return text
        return ''


# ---------------------------------------------------------------------------
# WebsiteBuilder — rendering, I/O, and build orchestration
# ---------------------------------------------------------------------------

class WebsiteBuilder:
    """Builds the full HTML website: reads source files, renders HTML, writes output."""

    def __init__(self, config_path: str = 'config.yml') -> None:
        self._config = self._load_config(config_path)
        self._validate_config()
        Path(self._config['directories']['output']).mkdir(parents=True, exist_ok=True)

        self._parser = MetadataParser()
        self._header = self._read_file(self._config['templates']['header'])
        self._footer = self._read_file(self._config['templates']['footer'])
        self._nav_items: List[Tuple[str, str]] = []

    # ------------------------------------------------------------------
    # Config
    # ------------------------------------------------------------------

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
        for key in ['website_url', 'website_name', 'author', 'directories', 'files', 'misc', 'templates']:
            if key not in self._config:
                logger.error(f"Missing required configuration key: {key}")
                sys.exit(1)

        for section, key in [('files', 'root_index'), ('templates', 'header'), ('templates', 'footer')]:
            path = self._config.get(section, {}).get(key)
            if not path:
                logger.error(f"Missing required configuration key: {section}.{key}")
                sys.exit(1)
            if not os.path.exists(path):
                logger.error(f"Required file not found: {path}")
                sys.exit(1)

        blog_index = self._config['files'].get('blog_index')
        if blog_index and not os.path.exists(blog_index):
            logger.warning(f"blog_index not found, blog list page will be skipped: {blog_index}")

    # ------------------------------------------------------------------
    # I/O helpers
    # ------------------------------------------------------------------

    def _read_file(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except (FileNotFoundError, IOError, UnicodeDecodeError):
            raise

    def _write_file(self, file_path: str, content: str) -> None:
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.debug(f"Written: {file_path}")
        except (IOError, OSError):
            raise

    # ------------------------------------------------------------------
    # Markdown conversion and HTML post-processing
    # ------------------------------------------------------------------

    def _markdown_convert(self, content: str) -> str:
        # Fresh instance per call — codehilite holds internal state that
        # markdown.reset() does not fully clear.
        return markdown.Markdown(extensions=['extra', 'codehilite']).convert(content)

    def _inject_post_meta(self, html: str, md_content: str, date: datetime) -> str:
        """Strip any raw date paragraph and inject a reading-time line after the first heading."""
        def _drop_date_para(m: re.Match) -> str:
            inner = re.sub(r'<[^>]+>', '', m.group(1)).strip()
            return '' if _is_date_string(inner) else m.group(0)
        html = re.sub(r'<p(?:[^>]*)>(.*?)</p>', _drop_date_para, html, flags=re.DOTALL)

        minutes = max(1, round(len(md_content.split()) / 200))
        tag = (
            f'<p class="reading-time">'
            f'<span>{date.strftime("%d %b %Y")}</span>'
            f'<span>&nbsp;&middot;&nbsp;</span>'
            f'<span>{minutes} min read</span>'
            f'</p>'
        )
        for heading in ('</h1>', '</h2>', '</h3>'):
            idx = html.find(heading)
            if idx != -1:
                end = idx + len(heading)
                return html[:end] + tag + html[end:]
        return tag + html

    def _inject_project_meta(self, html: str, github: Optional[str], paper: Optional[str]) -> str:
        """Inject GitHub and Paper link badges after the first heading on a project page."""
        if not github and not paper:
            return html
        links = ''
        if github:
            links += f'<a class="project-btn" href="{escape(github)}">GitHub &nearr;</a>'
        if paper:
            links += f'<a class="project-btn" href="{escape(paper)}">Paper &nearr;</a>'
        tag = f'<p class="project-page-links">{links}</p>'
        for heading in ('</h1>', '</h2>', '</h3>'):
            idx = html.find(heading)
            if idx != -1:
                end = idx + len(heading)
                return html[:end] + tag + html[end:]
        return tag + html

    def _style_reference_numbers(self, html: str) -> str:
        """Wrap leading [n] markers in paragraphs with a styled span."""
        return re.sub(r'<p>(\[\d+\])', r'<p><span class="ref-num">\1</span>', html)

    # ------------------------------------------------------------------
    # Navigation and page templating
    # ------------------------------------------------------------------

    def _build_nav(self, pages_dir: str, blog_dir: str) -> None:
        """Pre-scan pages directory and populate self._nav_items."""
        blog_index = self._config['files'].get('blog_index')
        blog_has_posts = bool(blog_dir and os.path.isdir(blog_dir) and any(
            f.endswith('.md') for f in os.listdir(blog_dir)
        ))

        self._nav_items = []
        if not (pages_dir and os.path.isdir(pages_dir)):
            return

        for filename in sorted(os.listdir(pages_dir)):
            if not filename.endswith('.md'):
                continue
            file_path = os.path.join(pages_dir, filename)
            if blog_index and os.path.abspath(file_path) == os.path.abspath(blog_index):
                if blog_has_posts:
                    try:
                        title = self._parser.extract_title(self._read_file(file_path).splitlines())
                        self._nav_items.append((f'/{blog_dir}', title))
                    except Exception as e:
                        logger.warning(f"Could not read nav title from {file_path}: {e}")
                continue
            try:
                title = self._parser.extract_title(self._read_file(file_path).splitlines())
                slug = os.path.splitext(filename)[0]
                self._nav_items.append((f'/{slug}', title))
            except Exception as e:
                logger.warning(f"Could not read nav title from {file_path}: {e}")

        # Contact link is always pinned to the end of the nav.
        contact_url = self._config['misc'].get('contact_url', '/contact')
        self._nav_items.sort(key=lambda item: item[0] == contact_url)

    def _render_page(self, body_html: str, title: str, current_path: str = '/') -> str:
        """Wrap body HTML with the header and footer templates."""
        home_active = ' class="active"' if current_path == '/' else ''
        nav_links = []
        for href, nav_title in self._nav_items:
            active = ' class="active"' if (
                href == current_path.rstrip('/') or
                (href != '/' and current_path.startswith(href + '/'))
            ) else ''
            nav_links.append(f'<li><a href="{href}"{active}>{escape(nav_title)}</a></li>')

        rss_filename = self._config['misc'].get('rss_filename', 'rss.xml')
        tmpl_vars = {
            'WEBSITE_NAME':    self._config['website_name'],
            'WEBSITE_URL':     self._config['website_url'],
            'AUTHOR':          self._config['author'],
            'RSS_URL':         f"/{rss_filename}",
            'SOURCE_URL':      self._config.get('source_url', ''),
            'NAV_HOME':        self._config['misc'].get('nav_home', 'Home'),
            'NAV_HOME_ACTIVE': home_active,
            'NAV_LINKS':       '\n\t\t\t\t'.join(nav_links),
            'CONTACT_URL':     self._config['misc'].get('contact_url', '/contact'),
            'TITLE':           escape(title),
            'BUILD_VERSION':   str(int(datetime.now().timestamp())),
        }

        def _apply(template: str) -> str:
            for k, v in tmpl_vars.items():
                template = template.replace(f'{{{{{k}}}}}', v)
            return template

        return _apply(self._header) + body_html + _apply(self._footer)

    # ------------------------------------------------------------------
    # Card / carousel / list HTML
    # ------------------------------------------------------------------

    def _render_project_card(self, project: Project, projects_dir: str) -> str:
        image_html = (
            f'<img class="project-card-image" src="{escape(project.image)}" alt="{escape(project.title)}">'
            if project.image
            else '<div class="project-card-placeholder">[ no preview ]</div>'
        )
        btn_html = ''
        if project.github:
            btn_html += f'<a class="project-btn" href="{escape(project.github)}">GitHub &nearr;</a>'
        if project.paper:
            btn_html += f'<a class="project-btn" href="{escape(project.paper)}">Paper &nearr;</a>'
        sprite_attr = f' data-card-sprite="{project.sprite}"' if project.sprite else ''
        return (
            f'<article class="project-card"{sprite_attr}>'
            f'<a href="/{projects_dir}/{project.path}" class="project-card-image-link">{image_html}</a>'
            f'<div class="project-card-body">'
            f'<h3><a href="/{projects_dir}/{project.path}">{escape(project.title)}</a></h3>'
            f'<p class="project-card-description">{escape(project.description)}</p>'
            f'<div class="project-card-footer">{btn_html}</div>'
            f'</div>'
            f'</article>'
        )

    def _render_carousel(self, projects: List[Project], projects_dir: str, cards_per_page: int = 2) -> str:
        pages = [projects[i:i + cards_per_page] for i in range(0, len(projects), cards_per_page)]
        dots = ''.join(
            f'<button class="carousel-dot{" active" if i == 0 else ""}" '
            f'aria-label="Go to page {i + 1}"></button>'
            for i in range(len(pages))
        )
        inner = ''.join(
            '<div class="carousel-page">\n'
            + ''.join(self._render_project_card(p, projects_dir) for p in page)
            + '</div>\n'
            for page in pages
        )
        return (
            f'<div class="carousel-wrapper"><div class="project-carousel">\n'
            f'{inner}'
            f'</div>\n<div class="carousel-dots">{dots}</div>\n</div>\n'
        )

    def _render_recent_posts(self, posts: List[Post], blog_dir: str, count: int) -> str:
        recent = sorted(posts, key=lambda p: p.date, reverse=True)[:count]
        items = ''.join(
            f'<li><span>{p.date.strftime("%d %b %Y")}</span>'
            f'<a href="/{blog_dir}/{p.path}">{escape(p.title)}</a></li>\n'
            for p in recent
        )
        return (
            f'<ul class="blog">\n{items}</ul>\n'
            f'<p><a href="/{blog_dir}">View all blog posts &rarr;</a></p>\n'
        )

    # ------------------------------------------------------------------
    # Content conversion
    # ------------------------------------------------------------------

    def _convert_markdown_to_html(
        self, input_dir: str, output_dir: str, is_blog: bool = False
    ) -> List[Post]:
        """Convert all Markdown files in a directory tree to HTML pages."""
        if not os.path.exists(input_dir):
            logger.warning(f"Input directory does not exist: {input_dir}")
            return []

        designated = {
            os.path.abspath(p)
            for p in [
                self._config['files'].get('blog_index'),
                self._config['files'].get('projects_index'),
            ]
            if p
        }

        posts = []
        for root, _, files in os.walk(input_dir):
            for file in sorted(files):
                if not file.endswith('.md'):
                    continue
                file_path = os.path.join(root, file)
                if os.path.abspath(file_path) in designated:
                    continue
                try:
                    md_content = self._read_file(file_path)
                    lines = md_content.splitlines()
                    title = self._parser.extract_title(lines)
                    date = self._parser.extract_date(lines)
                    html = self._markdown_convert(md_content)
                    if is_blog:
                        html = self._inject_post_meta(html, md_content, date)
                        html = self._style_reference_numbers(html)

                    relative_path = os.path.splitext(os.path.relpath(file_path, input_dir))[0]
                    output_file = os.path.join(output_dir, relative_path, 'index.html')
                    page_path = '/' + relative_path + '/'
                    self._write_file(output_file, self._render_page(html, title, page_path))
                    posts.append(Post(title=title, date=date, path=relative_path + '/', content=html))
                    logger.info(f"Processed: {file_path} -> {output_file}")
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")

        return posts

    def _convert_projects_to_html(self, input_dir: str, output_dir: str) -> List[Project]:
        """Convert all project Markdown files to individual HTML pages.

        Projects are intentionally flat (no subdirectories), unlike blog posts
        which support nested paths via os.walk().
        """
        if not os.path.exists(input_dir):
            logger.warning(f"Projects directory does not exist: {input_dir}")
            return []

        projects = []
        for file in sorted(os.listdir(input_dir)):
            if not file.endswith('.md'):
                continue
            file_path = os.path.join(input_dir, file)
            try:
                md_content = self._read_file(file_path)
                lines = md_content.splitlines()
                title = self._parser.extract_title(lines)
                date = self._parser.extract_date(lines)
                github, paper, image, sprite, order = self._parser.extract_project_meta(lines)

                clean_md = self._parser.strip_project_meta_lines(md_content)
                html = self._markdown_convert(clean_md)
                description = self._parser.extract_description(html)
                html = self._inject_project_meta(html, github, paper)

                relative_path = os.path.splitext(file)[0]
                output_file = os.path.join(output_dir, relative_path, 'index.html')
                # Use the URL slug from config, not the filesystem input_dir,
                # so the path stays correct if the directory name ever differs.
                projects_url_slug = self._config['directories'].get('projects', 'projects')
                page_path = f'/{projects_url_slug}/{relative_path}/'
                self._write_file(output_file, self._render_page(html, title, page_path))

                projects.append(Project(
                    title=title, date=date, path=relative_path + '/',
                    description=description, image=image,
                    github=github, paper=paper, sprite=sprite, order=order,
                ))
                logger.info(f"Processed project: {file_path} -> {output_file}")
            except Exception as e:
                logger.error(f"Error processing project {file_path}: {e}")

        return projects

    # ------------------------------------------------------------------
    # Page generators
    # ------------------------------------------------------------------

    def _generate_index_page(self, posts: List[Post], projects: List[Project]) -> None:
        """Generate the main index page.

        Markers in index.md:
          <!-- RECENT_POSTS -->    — replaced with recent blog posts list
          <!-- SELECTED_PROJECTS --> — replaced with recent project cards (carousel)
        If a marker is absent, its block is appended after all content.
        """
        root_content = self._read_file(self._config['files']['root_index'])
        title = self._parser.extract_title(root_content.splitlines())
        body_html = self._markdown_convert(root_content)

        blog_dir = self._config['directories'].get('blog')
        if posts and blog_dir:
            count = self._config['misc'].get('recent_posts_count', 5)
            recent_posts_html = self._render_recent_posts(posts, blog_dir, count)
            marker = '<!-- RECENT_POSTS -->'
            body_html = (
                body_html.replace(marker, recent_posts_html)
                if marker in body_html
                else body_html + recent_posts_html
            )

        projects_dir = self._config['directories'].get('projects', 'projects')
        if projects:
            count = self._config['misc'].get('selected_projects_count', 3)
            cards_per_page = self._config['misc'].get('carousel_cards_per_page', 2)
            recent = sorted(projects, key=_project_sort_key)[:count]
            carousel_html = self._render_carousel(recent, projects_dir, cards_per_page)
            carousel_html += f'<p><a href="/{projects_dir}">View all projects &rarr;</a></p>\n'
            marker = '<!-- SELECTED_PROJECTS -->'
            body_html = (
                body_html.replace(marker, carousel_html)
                if marker in body_html
                else body_html + carousel_html
            )

        output_path = os.path.join(self._config['directories']['output'], 'index.html')
        self._write_file(output_path, self._render_page(body_html, title, '/'))
        logger.info(f"Generated index page: {output_path}")

    def _generate_list_page(
        self, posts: List[Post], content_type: str, index_file_key: str, output_subdir: str
    ) -> None:
        """Generate a sorted list page for any content type (blog, etc.)"""
        index_file = self._config['files'].get(index_file_key)
        if not index_file or not os.path.exists(index_file):
            logger.warning(f"Index file for '{content_type}' not found, skipping list page")
            return

        index_md = self._read_file(index_file)
        title = self._parser.extract_title(index_md.splitlines())
        body_html = self._markdown_convert(index_md)

        if posts:
            body_html += f'<ul class="{content_type}">\n'
            for post in sorted(posts, key=lambda p: p.date, reverse=True):
                body_html += (
                    f'<li><span>{post.date.strftime("%d %b %Y")}</span>'
                    f'<a href="/{output_subdir}/{post.path}">{escape(post.title)}</a></li>\n'
                )
            body_html += '</ul>\n'

        output_path = os.path.join(self._config['directories']['output'], output_subdir, 'index.html')
        self._write_file(output_path, self._render_page(body_html, title, f'/{output_subdir}/'))
        logger.info(f"Generated {content_type} list page: {output_path}")

    def _generate_card_page(self, projects: List[Project]) -> None:
        """Generate the /projects listing page as a card grid."""
        projects_dir = self._config['directories'].get('projects', 'projects')
        index_file = self._config['files'].get('projects_index')
        if not index_file or not os.path.exists(index_file):
            logger.warning("projects_index not found, skipping card page")
            return

        index_md = self._read_file(index_file)
        title = self._parser.extract_title(index_md.splitlines())
        body_html = self._markdown_convert(index_md)

        if projects:
            body_html += '<div class="project-grid">\n'
            for project in sorted(projects, key=_project_sort_key):
                body_html += self._render_project_card(project, projects_dir)
            body_html += '</div>\n'

        output_path = os.path.join(self._config['directories']['output'], projects_dir, 'index.html')
        self._write_file(output_path, self._render_page(body_html, title, f'/{projects_dir}/'))
        logger.info(f"Generated projects card page: {output_path}")

    def _generate_rss(self, posts: List[Post]) -> None:
        """Generate RSS feed from blog posts."""
        if not posts:
            logger.warning("No posts found, skipping RSS generation")
            return

        posts_dir = self._config['directories'].get('blog', 'blog')
        items = []
        for post in posts:
            date = post.date.replace(hour=12, minute=0, second=0, microsecond=0)
            # Strip HTML tags for a clean plain-text excerpt in RSS readers.
            plain = re.sub(r'<[^>]+>', '', post.content).strip()
            excerpt = plain[:500] + ('…' if len(plain) > 500 else '')
            items.append(PyRSS2Gen.RSSItem(
                title=post.title,
                link=f"{self._config['website_url']}/{posts_dir}/{post.path}",
                description=excerpt,
                pubDate=date,
            ))

        items.sort(key=lambda x: x.pubDate, reverse=True)
        items = items[:self._config['misc'].get('rss_post_limit', 20)]

        rss = PyRSS2Gen.RSS2(
            title=f"{self._config['website_name']} RSS Feed",
            link=self._config['website_url'],
            description=f"The official RSS Feed for {self._config['website_url']}",
            lastBuildDate=datetime.now(),
            items=items,
        )

        rss_filename = self._config['misc'].get('rss_filename', 'rss.xml')
        rss_file = os.path.join(self._config['directories']['output'], rss_filename)
        with open(rss_file, 'wb') as f:
            rss.write_xml(f, encoding='utf-8')
        logger.info(f"Generated RSS feed: {rss_file} ({len(items)} items)")

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def build(self) -> None:
        """Build the entire website."""
        try:
            logger.info("Starting website build...")

            output = self._config['directories']['output']
            blog_dir = self._config['directories'].get('blog')
            pages_dir = self._config['directories'].get('pages')

            # Build nav before any rendering so all pages can include it.
            self._build_nav(pages_dir, blog_dir)

            if pages_dir:
                self._convert_markdown_to_html(pages_dir, output)

            blog_posts: List[Post] = []
            if blog_dir and os.path.isdir(blog_dir):
                blog_posts = self._convert_markdown_to_html(
                    blog_dir, os.path.join(output, blog_dir), is_blog=True,
                )

            projects_dir = self._config['directories'].get('projects')
            projects: List[Project] = []
            if projects_dir and os.path.isdir(projects_dir):
                projects = self._convert_projects_to_html(
                    projects_dir, os.path.join(output, projects_dir),
                )

            self._generate_index_page(blog_posts, projects)
            if blog_dir and self._config['files'].get('blog_index'):
                self._generate_list_page(blog_posts, 'blog', 'blog_index', blog_dir)
            if projects:
                self._generate_card_page(projects)
            if self._config['misc'].get('generate_rss', True) and blog_posts:
                self._generate_rss(blog_posts)

            public_dir = self._config['directories'].get('public', 'public')
            if os.path.isdir(public_dir):
                shutil.copytree(public_dir, os.path.join(output, public_dir), dirs_exist_ok=True)
                logger.info(f"Copied static assets: {public_dir} -> {output}/{public_dir}")

            logger.info(f"Website build completed successfully! Output: {output}")

        except Exception as e:
            logger.error(f"Website build failed: {e}")
            sys.exit(1)


def main():
    try:
        WebsiteBuilder().build()
    except KeyboardInterrupt:
        logger.info("Build interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
