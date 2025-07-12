"""
Main module for SEO analysis
"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
import yaml
import os
from urllib.parse import urlparse
import time

class SEOAnalyzer:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.session = None
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Loads the configuration from the YAML file"""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file {config_path} not found")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    async def analyze_url(self, url: str, depth: int = 1) -> Dict[str, Any]:
        """
        Performs SEO analysis for a URL
        
        Args:
            url: The URL to analyze
            depth: The depth of the analysis
            
        Returns:
            Dict with the analysis results
        """
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={"User-Agent": self.config["http"]["user_agent"]}
            )
        
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    return {"error": f"HTTP {response.status}: {response.reason}"}
                
                html = await response.text()
                return await self._analyze_page(html, url)
                
        except Exception as e:
            return {"error": str(e)}
    
    async def _analyze_page(self, html: str, url: str) -> Dict[str, Any]:
        """Analyzes a single page"""
        soup = BeautifulSoup(html, 'html.parser')
        
        return {
            "meta_tags": self._analyze_meta_tags(soup),
            "headers": self._analyze_headers(soup),
            "images": self._analyze_images(soup),
            "links": self._analyze_links(soup),
            "performance": await self._analyze_performance(url),
            "mobile_friendly": await self._check_mobile_friendly(url),
            "technical_seo": self._analyze_technical_seo(soup)
        }
    
    def _analyze_meta_tags(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyzes meta tags (title, description)"""
        result = {}
        # Title
        title_tag = soup.find('title')
        result['title'] = title_tag.text.strip() if title_tag else None
        # Description
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        result['description'] = desc_tag['content'].strip() if desc_tag and desc_tag.has_attr('content') else None
        return result
    
    def _analyze_headers(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyzes header tags (H1-H6) and returns count and content for H1, H2, H3"""
        headers = {}
        for i in range(1, 7):
            tag = f'h{i}'
            headers[tag] = [h.get_text(strip=True) for h in soup.find_all(tag)]
        # Specifically for H1, H2, H3: count and content
        summary = {
            'h1_count': len(headers['h1']),
            'h2_count': len(headers['h2']),
            'h3_count': len(headers['h3']),
            'h1_content': headers['h1'],
            'h2_content': headers['h2'],
            'h3_content': headers['h3'],
            'all': headers
        }
        return summary
    
    def _analyze_images(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyzes images and alt texts"""
        images = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            alt = img.get('alt', None)
            images.append({'src': src, 'alt': alt})
        return {'count': len(images), 'images': images}
    
    def _analyze_links(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyzes internal and external links"""
        links = {'internal': [], 'external': []}
        for a in soup.find_all('a', href=True):
            href = a['href']
            parsed = urlparse(href)
            if parsed.netloc == '' or parsed.netloc == self._get_domain(soup):
                links['internal'].append(href)
            else:
                links['external'].append(href)
        return {'internal_count': len(links['internal']), 'external_count': len(links['external']), 'internal': links['internal'], 'external': links['external']}
    
    def _get_domain(self, soup: BeautifulSoup) -> str:
        # Helper function to extract the domain from the soup object (e.g. from canonical link or base tag)
        canonical = soup.find('link', rel='canonical')
        if canonical and canonical.has_attr('href'):
            return urlparse(canonical['href']).netloc
        base = soup.find('base')
        if base and base.has_attr('href'):
            return urlparse(base['href']).netloc
        return ''
    
    async def _analyze_performance(self, url: str) -> Dict[str, Any]:
        """Analyzes performance metrics (load time, page size)"""
        result = {}
        start = time.perf_counter()
        try:
            async with self.session.get(url) as response:
                content = await response.read()
                result['status_code'] = response.status
                result['size_bytes'] = len(content)
        except Exception as e:
            result['error'] = str(e)
            result['status_code'] = None
            result['size_bytes'] = None
        end = time.perf_counter()
        result['load_time_seconds'] = round(end - start, 3)
        return result
    
    async def _check_mobile_friendly(self, url: str) -> Dict[str, Any]:
        """Checks mobile-first criteria (viewport, mobile meta tags)"""
        result = {'viewport': False, 'mobile_meta': False}
        try:
            async with self.session.get(url) as response:
                html = await response.text()
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            # Viewport tag
            viewport = soup.find('meta', attrs={'name': 'viewport'})
            result['viewport'] = viewport is not None
            # Mobile-optimized meta tags
            mobile_meta = soup.find('meta', attrs={'name': 'HandheldFriendly'}) or \
                          soup.find('meta', attrs={'name': 'MobileOptimized'})
            result['mobile_meta'] = mobile_meta is not None
        except Exception as e:
            result['error'] = str(e)
        return result
    
    def _analyze_technical_seo(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Performs technical SEO checks (robots, canonical, noindex, hreflang)"""
        result = {}
        # Canonical
        canonical = soup.find('link', rel='canonical')
        result['canonical'] = canonical['href'] if canonical and canonical.has_attr('href') else None
        # Noindex
        noindex = soup.find('meta', attrs={'name': 'robots'})
        result['noindex'] = 'noindex' in noindex['content'].lower() if noindex and noindex.has_attr('content') else False
        # Hreflang
        hreflangs = [link['hreflang'] for link in soup.find_all('link', rel='alternate') if link.has_attr('hreflang')]
        result['hreflang'] = hreflangs
        return result
    
    async def close(self):
        """Closes the HTTP session"""
        if self.session:
            await self.session.close() 