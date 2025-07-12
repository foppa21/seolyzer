#!/usr/bin/env python3
"""
SEOlyzer - A CLI tool for SEO analysis of websites
"""

import click
import json
import csv
from rich.console import Console
from rich.table import Table
from datetime import datetime
import asyncio
from seolyzer.core.analyzer import SEOAnalyzer
import os
import re
import aiohttp

console = Console()

def is_url(string):
    # Simple URL check
    return re.match(r'^https?://', string.strip()) is not None

@click.command()
@click.argument('input_path')
@click.option('--output', '-o', help='Output file for the report (CSV)', required=True)
@click.option('--format', '-f', type=click.Choice(['csv']), default='csv', help='Only CSV is supported')
@click.option('--depth', '-d', default=1, help='Depth of page analysis')
@click.option('--pagespeed', is_flag=True, default=False, help='Additionally run Google PageSpeed Insights analysis (API key required)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def main(input_path, output, format, depth, pagespeed, verbose):
    """
    SEOlyzer - SEO analysis tool for websites
    
    INPUT_PATH: Either a single URL or a path to a file with URLs (one per line)
    """
    asyncio.run(run_analysis(input_path, output, format, depth, pagespeed, verbose))

async def run_analysis(input_path, output, format, depth, pagespeed, verbose):
    urls = []
    if os.path.isfile(input_path):
        with open(input_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and is_url(line):
                    urls.append(line)
    elif is_url(input_path):
        urls = [input_path.strip()]
    else:
        console.print(f"[red]Error: '{input_path}' is neither an existing file nor a valid URL![/red]")
        return

    if not urls:
        console.print(f"[red]No valid URLs found![/red]")
        return

    console.print(f"[yellow]Analyzing the following URLs:[/yellow]")
    for u in urls:
        console.print(f" - {u}")

    analyzer = SEOAnalyzer()
    results_list = []
    for url in urls:
        console.print(f"[bold green]SEOlyzer[/bold green] - SEO analysis for {url}")
        result = await analyzer.analyze_url(url, depth)
        result["url"] = url
        result["timestamp"] = datetime.now().isoformat()
        # PageSpeed Insights only if option is set
        if pagespeed:
            result["pagespeed"] = await analyze_pagespeed(url)
        results_list.append(result)
        if verbose:
            display_results(result)
    await analyzer.close()

    write_csv(output, results_list, pagespeed)
    console.print(f"\n[green]CSV report saved to {output}[/green]")

def write_csv(output, results_list, pagespeed):
    fieldnames = [
        'URL',
        'Title tag content',
        'Description tag content',
        'H1 header count',
        'H1 header content',
        'H2 header count',
        'H2 header content',
        'Image count',
        'Load time',
        'Size',
        'Viewport tag',
        'Canonical',
        'hreflang',
        'Noindex',
    ]
    if pagespeed:
        fieldnames += ['PageSpeed Score', 'LCP', 'CLS', 'FID']
    with open(output, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for results in results_list:
            url = results.get('url', '')
            meta = results.get('meta_tags', {})
            headers = results.get('headers', {})
            images = results.get('images', {})
            perf = results.get('performance', {})
            mobile = results.get('mobile_friendly', {})
            tech = results.get('technical_seo', {})
            pagespeed_result = results.get('pagespeed', {})
            row = {
                'URL': url,
                'Title tag content': meta.get('title', ''),
                'Description tag content': meta.get('description', ''),
                'H1 header count': headers.get('h1_count', 0),
                'H1 header content': ', '.join(headers.get('h1_content', [])),
                'H2 header count': headers.get('h2_count', 0),
                'H2 header content': ', '.join(headers.get('h2_content', [])),
                'Image count': images.get('count', 0),
                'Load time': perf.get('load_time_seconds', ''),
                'Size': perf.get('size_bytes', ''),
                'Viewport tag': mobile.get('viewport', ''),
                'Canonical': tech.get('canonical', ''),
                'hreflang': ','.join(tech.get('hreflang', [])),
                'Noindex': tech.get('noindex', ''),
            }
            if pagespeed:
                row['PageSpeed Score'] = pagespeed_result.get('score', '')
                row['LCP'] = pagespeed_result.get('lcp', '')
                row['CLS'] = pagespeed_result.get('cls', '')
                row['FID'] = pagespeed_result.get('fid', '')
            writer.writerow(row)

def display_results(results):
    """Displays the analysis results in a clear table"""
    table = Table(title="SEO Analysis Results")
    table.add_column("Category", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="yellow")

    # Meta tags
    meta = results.get("meta_tags", {})
    table.add_row("Meta tags", "✅" if meta else "❌", f"Title: {meta.get('title')}, Desc: {meta.get('description')}")
    # Headers
    headers = results.get("headers", {})
    table.add_row("H1 header", str(headers.get('h1_count', 0)), f"{headers.get('h1_content', [])}")
    table.add_row("H2 header", str(headers.get('h2_count', 0)), f"{headers.get('h2_content', [])}")
    table.add_row("H3 header", str(headers.get('h3_count', 0)), f"{headers.get('h3_content', [])}")
    # Images
    images = results.get("images", {})
    table.add_row("Images", f"{images.get('count', 0)}", f"Examples: {[img['src'] for img in images.get('images', [])[:3]]}")
    # Links
    links = results.get("links", {})
    table.add_row("Links (internal)", f"{links.get('internal_count', 0)}", f"Examples: {[l for l in links.get('internal', [])[:3]]}")
    table.add_row("Links (external)", f"{links.get('external_count', 0)}", f"Examples: {[l for l in links.get('external', [])[:3]]}")
    # Performance
    perf = results.get("performance", {})
    table.add_row("Performance", "✅" if perf.get('status_code') == 200 else "❌", f"Load time: {perf.get('load_time_seconds')}s, Size: {perf.get('size_bytes')} bytes")
    # Mobile
    mobile = results.get("mobile_friendly", {})
    table.add_row("Mobile viewport", "✅" if mobile.get('viewport') else "❌", f"Viewport tag: {mobile.get('viewport')}")
    table.add_row("Mobile meta", "✅" if mobile.get('mobile_meta') else "❌", f"Mobile meta: {mobile.get('mobile_meta')}")
    # Technical SEO
    tech = results.get("technical_seo", {})
    table.add_row("Canonical", "✅" if tech.get('canonical') else "❌", f"{tech.get('canonical')}")
    table.add_row("Noindex", "✅" if tech.get('noindex') else "❌", f"noindex: {tech.get('noindex')}")
    table.add_row("Hreflang", "✅" if tech.get('hreflang') else "❌", f"{tech.get('hreflang')}")

    console.print(table)

async def analyze_pagespeed(url):
    api_key = os.environ.get('GOOGLE_PAGESPEED_API_KEY')
    if not api_key:
        return {'error': 'No API key set'}
    endpoint = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed'
    params = {
        'url': url,
        'key': api_key,
        'strategy': 'desktop',  # or 'mobile'
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(endpoint, params=params) as resp:
                data = await resp.json()
                lighthouse = data.get('lighthouseResult', {})
                categories = lighthouse.get('categories', {})
                audits = lighthouse.get('audits', {})
                return {
                    'score': categories.get('performance', {}).get('score', ''),
                    'lcp': audits.get('largest-contentful-paint', {}).get('displayValue', ''),
                    'cls': audits.get('cumulative-layout-shift', {}).get('displayValue', ''),
                    'fid': audits.get('interactive', {}).get('displayValue', ''),
                }
        except Exception as e:
            return {'error': str(e)}

if __name__ == '__main__':
    main() 