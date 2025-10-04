"""Enhanced web crawler service using MCP Gateway and Exa integration."""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Set
from urllib.parse import urljoin, urlparse
import time
from datetime import datetime
import httpx
from bs4 import BeautifulSoup
import aiohttp

from config import settings
from .mcp_client import MCPClient, MCPClientError

logger = logging.getLogger(__name__)


class WebCrawler:
    """Enhanced web crawler with MCP Gateway integration and robust crawling capabilities."""
    
    def __init__(self):
        self.mcp_client = None
        self.session = None
        self.visited_urls: Set[str] = set()
        self.crawl_queue: List[str] = []
        self.max_depth = settings.max_crawl_depth
        self.delay_between_requests = settings.crawl_delay  # seconds
        self.max_concurrent_requests = settings.max_concurrent_requests
        
        # Initialize MCP client if configured
        if settings.use_mcp_for_crawling and settings.exa_mcp_base_url:
            try:
                self.mcp_client = MCPClient(
                    base_url=settings.exa_mcp_base_url,
                    api_key=None,
                    timeout_s=60.0
                )
                logger.info("MCP Gateway client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize MCP client: {e}")
                self.mcp_client = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'DocuBot-Crawler/1.0 (https://github.com/docubot)'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def crawl_url_with_exa(self, url: str, extract_links: bool = False) -> Dict[str, Any]:
        """
        Crawl a URL using Exa MCP tools for enhanced content extraction.
        
        Args:
            url: URL to crawl
            extract_links: Whether to extract links from the page
            
        Returns:
            Dict containing crawled content and metadata
        """
        if not self.mcp_client:
            raise MCPClientError("MCP client not initialized")
        
        try:
            # Use Exa crawl tool for enhanced content extraction
            crawl_args = {
                "url": url,
                "text": True,
                "links": extract_links,
                "images": False
            }
            
            result = await self.mcp_client.call_tool(
                tool_name=settings.exa_crawl_tool_name or "exa.crawl",
                arguments=crawl_args
            )
            
            # Process the result
            content = ""
            links = []
            
            if isinstance(result, dict):
                # Extract text content
                if "content" in result:
                    content = result["content"]
                elif "text" in result:
                    content = result["text"]
                elif "results" in result and isinstance(result["results"], list):
                    # Handle multiple results
                    content_parts = []
                    for item in result["results"]:
                        if isinstance(item, dict):
                            if "content" in item:
                                content_parts.append(item["content"])
                            elif "text" in item:
                                content_parts.append(item["text"])
                    content = "\n\n".join(content_parts)
                
                # Extract links if requested
                if extract_links and "links" in result:
                    links = result["links"]
                elif extract_links and "results" in result:
                    for item in result["results"]:
                        if isinstance(item, dict) and "links" in item:
                            links.extend(item["links"])
            
            return {
                "success": True,
                "url": url,
                "content": content,
                "links": links,
                "crawled_at": datetime.now().isoformat(),
                "method": "exa_mcp"
            }
            
        except Exception as e:
            logger.error(f"Exa crawl failed for {url}: {e}")
            return {
                "success": False,
                "url": url,
                "error": str(e),
                "method": "exa_mcp"
            }
    
    async def crawl_url_fallback(self, url: str) -> Dict[str, Any]:
        """
        Enhanced fallback crawling method with comprehensive content extraction.
        
        Args:
            url: URL to crawl
            
        Returns:
            Dict containing crawled content and metadata
        """
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    return {
                        "success": False,
                        "url": url,
                        "error": f"HTTP {response.status}",
                        "method": "fallback"
                    }
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract comprehensive metadata
                title = soup.find('title')
                title_text = title.get_text().strip() if title else ""
                
                # Extract meta description
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                description = meta_desc.get('content', '') if meta_desc else ""
                
                # Extract headings for structure
                headings = []
                for level in range(1, 7):
                    for heading in soup.find_all(f'h{level}'):
                        headings.append({
                            'level': level,
                            'text': heading.get_text().strip(),
                            'id': heading.get('id', '')
                        })
                
                # Extract comprehensive content
                content_data = self._extract_comprehensive_content(soup)
                
                # Extract links with more detail
                links = self._extract_links(soup, url)
                
                # Extract images with alt text
                images = self._extract_images(soup, url)
                
                # Extract tables
                tables = self._extract_tables(soup)
                
                # Extract code blocks
                code_blocks = self._extract_code_blocks(soup)
                
                return {
                    "success": True,
                    "url": url,
                    "title": title_text,
                    "description": description,
                    "headings": headings,
                    "content": content_data['text'],
                    "structured_content": content_data['structured'],
                    "links": links,
                    "images": images,
                    "tables": tables,
                    "code_blocks": code_blocks,
                    "content_length": len(content_data['text']),
                    "metadata": {
                        "headings_count": len(headings),
                        "links_count": len(links),
                        "images_count": len(images),
                        "tables_count": len(tables),
                        "code_blocks_count": len(code_blocks)
                    },
                    "crawled_at": datetime.now().isoformat(),
                    "method": "fallback"
                }
                
        except Exception as e:
            logger.error(f"Fallback crawl failed for {url}: {e}")
            return {
                "success": False,
                "url": url,
                "error": str(e),
                "method": "fallback"
            }
    
    def _extract_comprehensive_content(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract comprehensive content with markdown formatting preservation."""
        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
            element.decompose()
        
        # Extract main content areas with markdown formatting
        content_selectors = [
            'main', 'article', '.content', '.main-content', '.documentation', 
            '.docs', '.post', '.entry', '.page-content', '.body-content',
            '#content', '#main', '#primary', '.primary', '.main'
        ]
        
        main_content = ""
        markdown_content = ""
        
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                for element in elements:
                    # Extract plain text
                    content_text = element.get_text(separator='\n', strip=True)
                    if len(content_text) > len(main_content):
                        main_content = content_text
                    
                    # Extract markdown-formatted content
                    markdown_text = self._convert_to_markdown(element)
                    if len(markdown_text) > len(markdown_content):
                        markdown_content = markdown_text
        
        # If no specific content areas found, extract all text
        if not main_content.strip():
            main_content = soup.get_text(separator='\n', strip=True)
            markdown_content = self._convert_to_markdown(soup)
        
        # Extract structured elements with markdown
        structured_content = self._extract_structured_markdown(soup)
        
        return {
            'text': main_content,
            'markdown': markdown_content,
            'structured': structured_content
        }
    
    def _convert_to_markdown(self, element) -> str:
        """Convert HTML element to markdown format."""
        markdown_parts = []
        
        for child in element.find_all(recursive=False):
            if child.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                level = int(child.name[1])
                text = child.get_text(strip=True)
                markdown_parts.append(f"{'#' * level} {text}\n")
            
            elif child.name == 'p':
                text = child.get_text(strip=True)
                if text:
                    markdown_parts.append(f"{text}\n")
            
            elif child.name in ['ul', 'ol']:
                list_markdown = self._convert_list_to_markdown(child)
                markdown_parts.append(list_markdown)
            
            elif child.name == 'blockquote':
                text = child.get_text(strip=True)
                lines = text.split('\n')
                for line in lines:
                    if line.strip():
                        markdown_parts.append(f"> {line.strip()}\n")
            
            elif child.name in ['code', 'pre']:
                code_markdown = self._convert_code_to_markdown(child)
                markdown_parts.append(code_markdown)
            
            elif child.name == 'table':
                table_markdown = self._convert_table_to_markdown(child)
                markdown_parts.append(table_markdown)
            
            elif child.name in ['strong', 'b']:
                text = child.get_text(strip=True)
                markdown_parts.append(f"**{text}**")
            
            elif child.name in ['em', 'i']:
                text = child.get_text(strip=True)
                markdown_parts.append(f"*{text}*")
            
            elif child.name == 'a':
                href = child.get('href', '')
                text = child.get_text(strip=True)
                if href and text:
                    markdown_parts.append(f"[{text}]({href})")
                else:
                    markdown_parts.append(text)
            
            elif child.name == 'img':
                src = child.get('src', '')
                alt = child.get('alt', '')
                title = child.get('title', '')
                if src:
                    if title:
                        markdown_parts.append(f"![{alt}]({src} '{title}')")
                    else:
                        markdown_parts.append(f"![{alt}]({src})")
            
            elif child.name == 'hr':
                markdown_parts.append("---\n")
            
            else:
                # For other elements, extract text content
                text = child.get_text(strip=True)
                if text:
                    markdown_parts.append(text)
        
        return '\n'.join(markdown_parts)
    
    def _convert_list_to_markdown(self, list_element) -> str:
        """Convert HTML list to markdown format."""
        markdown_parts = []
        
        for li in list_element.find_all('li', recursive=False):
            text = li.get_text(strip=True)
            if list_element.name == 'ul':
                markdown_parts.append(f"- {text}")
            else:  # ol
                markdown_parts.append(f"1. {text}")
            
            # Handle nested lists
            nested_lists = li.find_all(['ul', 'ol'], recursive=False)
            for nested_list in nested_lists:
                nested_markdown = self._convert_list_to_markdown(nested_list)
                # Indent nested lists
                indented = '\n'.join(['  ' + line for line in nested_markdown.split('\n')])
                markdown_parts.append(indented)
        
        return '\n'.join(markdown_parts) + '\n'
    
    def _convert_code_to_markdown(self, code_element) -> str:
        """Convert HTML code element to markdown format."""
        if code_element.name == 'pre':
            code_tag = code_element.find('code')
            if code_tag:
                language = self._get_code_language(code_tag)
                code_content = code_tag.get_text()
                return f"```{language}\n{code_content}\n```\n"
            else:
                code_content = code_element.get_text()
                return f"```\n{code_content}\n```\n"
        else:  # inline code
            code_content = code_element.get_text()
            return f"`{code_content}`"
    
    def _get_code_language(self, code_element) -> str:
        """Extract programming language from code element."""
        class_list = code_element.get('class', [])
        for cls in class_list:
            if cls.startswith('language-'):
                return cls.replace('language-', '')
            elif cls.startswith('lang-'):
                return cls.replace('lang-', '')
        
        # Check parent elements for language hints
        parent = code_element.parent
        while parent:
            if parent.name == 'pre':
                parent_classes = parent.get('class', [])
                for cls in parent_classes:
                    if cls.startswith('language-') or cls.startswith('lang-'):
                        return cls.replace('language-', '').replace('lang-', '')
            parent = parent.parent
        
        return ""
    
    def _convert_table_to_markdown(self, table_element) -> str:
        """Convert HTML table to markdown format."""
        markdown_parts = []
        rows = []
        
        # Extract all rows
        for tr in table_element.find_all('tr'):
            cells = []
            for td in tr.find_all(['td', 'th']):
                cell_text = td.get_text(strip=True)
                cells.append(cell_text)
            if cells:
                rows.append(cells)
        
        if not rows:
            return ""
        
        # Create markdown table
        if len(rows) > 0:
            # Header row
            header = rows[0]
            markdown_parts.append('| ' + ' | '.join(header) + ' |')
            
            # Separator row
            separator = '| ' + ' | '.join(['---'] * len(header)) + ' |'
            markdown_parts.append(separator)
            
            # Data rows
            for row in rows[1:]:
                # Pad row with empty cells if needed
                while len(row) < len(header):
                    row.append('')
                markdown_parts.append('| ' + ' | '.join(row) + ' |')
        
        return '\n'.join(markdown_parts) + '\n'
    
    def _extract_structured_markdown(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract structured content with markdown formatting."""
        structured = {
            'headings': [],
            'lists': [],
            'code_blocks': [],
            'tables': [],
            'paragraphs': [],
            'links': [],
            'images': []
        }
        
        # Extract headings with markdown
        for level in range(1, 7):
            for heading in soup.find_all(f'h{level}'):
                text = heading.get_text(strip=True)
                id_attr = heading.get('id', '')
                structured['headings'].append({
                    'level': level,
                    'text': text,
                    'markdown': f"{'#' * level} {text}",
                    'id': id_attr
                })
        
        # Extract lists with markdown
        for ul in soup.find_all(['ul', 'ol']):
            list_items = []
            for li in ul.find_all('li'):
                text = li.get_text(strip=True)
                list_items.append(text)
            
            if list_items:
                list_type = ul.name
                markdown = self._convert_list_to_markdown(ul)
                structured['lists'].append({
                    'type': list_type,
                    'items': list_items,
                    'markdown': markdown
                })
        
        # Extract code blocks with markdown
        for pre in soup.find_all('pre'):
            code = pre.find('code')
            if code:
                language = self._get_code_language(code)
                content = code.get_text()
                markdown = f"```{language}\n{content}\n```"
                structured['code_blocks'].append({
                    'language': language,
                    'content': content,
                    'markdown': markdown
                })
        
        # Extract tables with markdown
        for table in soup.find_all('table'):
            markdown = self._convert_table_to_markdown(table)
            if markdown:
                structured['tables'].append({
                    'markdown': markdown
                })
        
        # Extract paragraphs with markdown
        for p in soup.find_all('p'):
            text = p.get_text(strip=True)
            if len(text) > 20:  # Only meaningful paragraphs
                structured['paragraphs'].append({
                    'text': text,
                    'markdown': text
                })
        
        # Extract links with markdown
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            title = link.get('title', '')
            if href and text:
                if title:
                    markdown = f"[{text}]({href} '{title}')"
                else:
                    markdown = f"[{text}]({href})"
                structured['links'].append({
                    'url': href,
                    'text': text,
                    'title': title,
                    'markdown': markdown
                })
        
        # Extract images with markdown
        for img in soup.find_all('img'):
            src = img.get('src', '')
            alt = img.get('alt', '')
            title = img.get('title', '')
            if src:
                if title:
                    markdown = f"![{alt}]({src} '{title}')"
                else:
                    markdown = f"![{alt}]({src})"
                structured['images'].append({
                    'src': src,
                    'alt': alt,
                    'title': title,
                    'markdown': markdown
                })
        
        return structured
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Extract links with detailed information."""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)
            
            if href and not href.startswith('#') and not href.startswith('mailto:'):
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    from urllib.parse import urljoin
                    href = urljoin(base_url, href)
                
                links.append({
                    'url': href,
                    'text': text,
                    'title': link.get('title', ''),
                    'target': link.get('target', '')
                })
        
        return links
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Extract images with alt text and captions."""
        if not settings.extract_images:
            return []
        
        images = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src:
                # Convert relative URLs to absolute
                if src.startswith('/'):
                    from urllib.parse import urljoin
                    src = urljoin(base_url, src)
                
                images.append({
                    'src': src,
                    'alt': img.get('alt', ''),
                    'title': img.get('title', ''),
                    'caption': self._get_image_caption(img)
                })
        
        return images
    
    def _get_image_caption(self, img_tag) -> str:
        """Get image caption from nearby elements."""
        # Look for figcaption
        figcaption = img_tag.find_next('figcaption')
        if figcaption:
            return figcaption.get_text(strip=True)
        
        # Look for caption in parent figure
        figure = img_tag.find_parent('figure')
        if figure:
            caption = figure.find('figcaption')
            if caption:
                return caption.get_text(strip=True)
        
        return ""
    
    def _extract_tables(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract table content."""
        if not settings.extract_tables:
            return []
        
        tables = []
        for table in soup.find_all('table'):
            rows = []
            for tr in table.find_all('tr'):
                cells = []
                for td in tr.find_all(['td', 'th']):
                    cells.append(td.get_text(strip=True))
                if cells:
                    rows.append(cells)
            
            if rows:
                tables.append({
                    'rows': rows,
                    'headers': rows[0] if rows else [],
                    'data_rows': rows[1:] if len(rows) > 1 else []
                })
        
        return tables
    
    def _extract_code_blocks(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract code blocks and examples."""
        if not settings.extract_code_blocks:
            return []
        
        code_blocks = []
        
        # Extract <pre><code> blocks
        for pre in soup.find_all('pre'):
            code = pre.find('code')
            if code:
                code_blocks.append({
                    'type': 'code_block',
                    'language': code.get('class', [''])[0].replace('language-', '') if code.get('class') else '',
                    'content': code.get_text(),
                    'element': 'pre'
                })
        
        # Extract inline code
        for code in soup.find_all('code'):
            if code.parent.name != 'pre':  # Avoid duplicates
                code_blocks.append({
                    'type': 'inline_code',
                    'content': code.get_text(),
                    'element': 'code'
                })
        
        return code_blocks
    
    async def search_web_with_exa(self, query: str, num_results: int = 10) -> Dict[str, Any]:
        """
        Search the web using Exa's semantic search capabilities.
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            Dict containing search results
        """
        if not self.mcp_client:
            raise MCPClientError("MCP client not initialized")
        
        try:
            search_args = {
                "query": query,
                "numResults": num_results,
                "type": "neural",
                "useAutoprompt": True
            }
            
            result = await self.mcp_client.call_tool(
                tool_name=settings.exa_search_tool_name or "exa.search",
                arguments=search_args
            )
            
            # Process search results
            search_results = []
            if isinstance(result, dict) and "results" in result:
                for item in result["results"]:
                    if isinstance(item, dict):
                        search_results.append({
                            "url": item.get("url", ""),
                            "title": item.get("title", ""),
                            "content": item.get("text", item.get("content", "")),
                            "score": item.get("score", 0.0)
                        })
            
            return {
                "success": True,
                "query": query,
                "results": search_results,
                "total_results": len(search_results),
                "searched_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Exa search failed for query '{query}': {e}")
            return {
                "success": False,
                "query": query,
                "error": str(e)
            }
    
    async def crawl_website_recursive(
        self, 
        start_url: str, 
        max_pages: int = None,
        max_depth: int = None,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Recursively crawl a website starting from a base URL.
        
        Args:
            start_url: Starting URL for crawling
            max_pages: Maximum number of pages to crawl (uses config default if None)
            max_depth: Maximum crawl depth (uses config default if None)
            include_patterns: URL patterns to include
            exclude_patterns: URL patterns to exclude
            
        Returns:
            List of crawled page results
        """
        # Use config defaults if not provided
        max_pages = max_pages or settings.max_pages_per_domain
        max_depth = max_depth or settings.max_crawl_depth
        
        # Extract domain for same-domain crawling
        from urllib.parse import urlparse
        base_domain = urlparse(start_url).netloc
        
        if include_patterns is None:
            include_patterns = []
        if exclude_patterns is None:
            exclude_patterns = [
                "#", "mailto:", "javascript:", "tel:", "sms:", "ftp:",
                ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".ico",
                ".css", ".js", ".json", ".xml", ".zip", ".tar", ".gz",
                ".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm",
                ".mp3", ".wav", ".ogg", ".aac", ".flac"
            ]
        
        self.visited_urls.clear()
        self.crawl_queue = [start_url]
        crawled_pages = []
        current_depth = 0
        
        while self.crawl_queue and len(crawled_pages) < max_pages and current_depth < max_depth:
            current_batch = self.crawl_queue.copy()
            self.crawl_queue.clear()
            
            # Process current batch with concurrency control
            semaphore = asyncio.Semaphore(self.max_concurrent_requests)
            
            async def crawl_with_semaphore(url: str):
                async with semaphore:
                    await asyncio.sleep(self.delay_between_requests)
                    return await self.crawl_single_url(url)
            
            tasks = [crawl_with_semaphore(url) for url in current_batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Crawl task failed: {result}")
                    continue
                
                if result["success"]:
                    crawled_pages.append(result)
                    
                    # Add new links to queue if we haven't reached max depth
                    if current_depth < max_depth - 1:
                        links_added = 0
                        for link_data in result.get("links", []):
                            # Handle both old format (string) and new format (dict)
                            if isinstance(link_data, dict):
                                link_url = link_data.get("url", "")
                            else:
                                link_url = link_data
                            
                            if link_url and link_url not in self.visited_urls and self._should_crawl_link(
                                link_url, start_url, include_patterns, exclude_patterns, base_domain
                            ):
                                self.crawl_queue.append(link_url)
                                links_added += 1
                        
                        logger.info(f"Depth {current_depth}: Added {links_added} links to queue. Queue size: {len(self.crawl_queue)}")
            
            current_depth += 1
        
        return crawled_pages
    
    async def crawl_single_url(self, url: str) -> Dict[str, Any]:
        """
        Crawl a single URL using the best available method.
        
        Args:
            url: URL to crawl
            
        Returns:
            Dict containing crawl result
        """
        if url in self.visited_urls:
            return {
                "success": False,
                "url": url,
                "error": "Already visited",
                "method": "skip"
            }
        
        self.visited_urls.add(url)
        
        # Try Exa MCP first if available
        if self.mcp_client and settings.use_mcp_for_crawling:
            result = await self.crawl_url_with_exa(url, extract_links=True)
            if result["success"]:
                return result
        
        # Fallback to traditional crawling
        return await self.crawl_url_fallback(url)
    
    def _should_crawl_link(
        self, 
        link: str, 
        base_url: str, 
        include_patterns: List[str], 
        exclude_patterns: List[str],
        base_domain: str = None
    ) -> bool:
        """
        Determine if a link should be crawled based on patterns.
        
        Args:
            link: Link to evaluate
            base_url: Base URL for domain checking
            include_patterns: Patterns to include
            exclude_patterns: Patterns to exclude
            base_domain: Pre-extracted base domain for efficiency
            
        Returns:
            True if link should be crawled
        """
        if link in self.visited_urls:
            return False
        
        # Check if link is from same domain (enhanced for same-domain crawling)
        try:
            if base_domain:
                # Use pre-extracted domain for efficiency
                link_domain = urlparse(link).netloc
                if settings.same_domain_only and base_domain != link_domain:
                    return False
            else:
                # Fallback to original logic
                base_domain = urlparse(base_url).netloc
                link_domain = urlparse(link).netloc
                if settings.same_domain_only and base_domain != link_domain:
                    return False
        except:
            return False
        
        # Check exclude patterns
        for pattern in exclude_patterns:
            if pattern in link:
                return False
        
        # Check include patterns (if any)
        if include_patterns:
            for pattern in include_patterns:
                if pattern in link:
                    return True
            return False
        
        return True
    
    async def crawl_documentation_site(self, base_url: str) -> List[Dict[str, Any]]:
        """
        Specialized crawler for documentation sites.
        
        Args:
            base_url: Base URL of the documentation site
            
        Returns:
            List of crawled documentation pages
        """
        doc_patterns = [
            "/docs/", "/documentation/", "/guide/", "/tutorial/", 
            "/api/", "/reference/", "/help/", "/manual/"
        ]
        
        exclude_patterns = [
            "#", "mailto:", "javascript:", ".pdf", ".jpg", ".png", ".gif",
            ".zip", ".tar", ".gz", "/search", "/login", "/register"
        ]
        
        return await self.crawl_website_recursive(
            start_url=base_url,
            max_pages=100,
            max_depth=4,
            include_patterns=doc_patterns,
            exclude_patterns=exclude_patterns
        )

