#!/usr/bin/env python3
"""
SEOlyzer - Ein CLI-Tool zur SEO-Analyse von Webseiten
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
    # Einfache URL-Prüfung
    return re.match(r'^https?://', string.strip()) is not None

@click.command()
@click.argument('input_path')
@click.option('--output', '-o', help='Ausgabedatei für den Bericht (CSV)', required=True)
@click.option('--format', '-f', type=click.Choice(['csv']), default='csv', help='Nur CSV wird unterstützt')
@click.option('--depth', '-d', default=1, help='Tiefe der Seitenanalyse')
@click.option('--pagespeed', is_flag=True, default=False, help='Führe zusätzlich eine Google PageSpeed Insights Analyse durch (API-Key erforderlich)')
@click.option('--verbose', '-v', is_flag=True, help='Detaillierte Ausgabe')
def main(input_path, output, format, depth, pagespeed, verbose):
    """
    SEOlyzer - SEO-Analyse-Tool für Webseiten
    
    INPUT_PATH: Entweder eine einzelne URL oder ein Pfad zu einer Datei mit URLs (eine pro Zeile)
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
        console.print(f"[red]Fehler: '{input_path}' ist weder eine existierende Datei noch eine gültige URL![/red]")
        return

    if not urls:
        console.print(f"[red]Keine gültigen URLs gefunden![/red]")
        return

    console.print(f"[yellow]Analysiere folgende URLs:[/yellow]")
    for u in urls:
        console.print(f" - {u}")

    analyzer = SEOAnalyzer()
    results_list = []
    for url in urls:
        console.print(f"[bold green]SEOlyzer[/bold green] - SEO-Analyse für {url}")
        result = await analyzer.analyze_url(url, depth)
        result["url"] = url
        result["timestamp"] = datetime.now().isoformat()
        # PageSpeed Insights nur wenn Option gesetzt
        if pagespeed:
            result["pagespeed"] = await analyze_pagespeed(url)
        results_list.append(result)
        if verbose:
            display_results(result)
    await analyzer.close()

    write_csv(output, results_list, pagespeed)
    console.print(f"\n[green]CSV-Bericht wurde in {output} gespeichert[/green]")

def write_csv(output, results_list, pagespeed):
    fieldnames = [
        'URL',
        'Title Tag inhalt',
        'Description Tag inhalt',
        'H1 Header anzahl',
        'Inhalt H1 Header',
        'H2 Header anzahl',
        'Inhalt H2 Header',
        'Anzahl Bilder',
        'Ladezeit',
        'Größe',
        'Viewport-Tag',
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
                'Title Tag inhalt': meta.get('title', ''),
                'Description Tag inhalt': meta.get('description', ''),
                'H1 Header anzahl': headers.get('h1_count', 0),
                'Inhalt H1 Header': ', '.join(headers.get('h1_content', [])),
                'H2 Header anzahl': headers.get('h2_count', 0),
                'Inhalt H2 Header': ', '.join(headers.get('h2_content', [])),
                'Anzahl Bilder': images.get('count', 0),
                'Ladezeit': perf.get('load_time_seconds', ''),
                'Größe': perf.get('size_bytes', ''),
                'Viewport-Tag': mobile.get('viewport', ''),
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
    """Zeigt die Analyseergebnisse in einer übersichtlichen Tabelle an"""
    table = Table(title="SEO-Analyse Ergebnisse")
    table.add_column("Kategorie", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="yellow")

    # Meta-Tags
    meta = results.get("meta_tags", {})
    table.add_row("Meta-Tags", "✅" if meta else "❌", f"Title: {meta.get('title')}, Desc: {meta.get('description')}")
    # Header
    headers = results.get("headers", {})
    table.add_row("H1-Header", str(headers.get('h1_count', 0)), f"{headers.get('h1_content', [])}")
    table.add_row("H2-Header", str(headers.get('h2_count', 0)), f"{headers.get('h2_content', [])}")
    table.add_row("H3-Header", str(headers.get('h3_count', 0)), f"{headers.get('h3_content', [])}")
    # Bilder
    images = results.get("images", {})
    table.add_row("Bilder", f"{images.get('count', 0)}", f"Beispiele: {[img['src'] for img in images.get('images', [])[:3]]}")
    # Links
    links = results.get("links", {})
    table.add_row("Links (intern)", f"{links.get('internal_count', 0)}", f"Beispiele: {[l for l in links.get('internal', [])[:3]]}")
    table.add_row("Links (extern)", f"{links.get('external_count', 0)}", f"Beispiele: {[l for l in links.get('external', [])[:3]]}")
    # Performance
    perf = results.get("performance", {})
    table.add_row("Performance", "✅" if perf.get('status_code') == 200 else "❌", f"Ladezeit: {perf.get('load_time_seconds')}s, Größe: {perf.get('size_bytes')} Bytes")
    # Mobile
    mobile = results.get("mobile_friendly", {})
    table.add_row("Mobile Viewport", "✅" if mobile.get('viewport') else "❌", f"Viewport-Tag: {mobile.get('viewport')}")
    table.add_row("Mobile Meta", "✅" if mobile.get('mobile_meta') else "❌", f"Mobile-Meta: {mobile.get('mobile_meta')}")
    # Technisches SEO
    tech = results.get("technical_seo", {})
    table.add_row("Canonical", "✅" if tech.get('canonical') else "❌", f"{tech.get('canonical')}")
    table.add_row("Noindex", "✅" if tech.get('noindex') else "❌", f"noindex: {tech.get('noindex')}")
    table.add_row("Hreflang", "✅" if tech.get('hreflang') else "❌", f"{tech.get('hreflang')}")

    console.print(table)

async def analyze_pagespeed(url):
    api_key = os.environ.get('GOOGLE_PAGESPEED_API_KEY')
    if not api_key:
        return {'error': 'Kein API-Key gesetzt'}
    endpoint = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed'
    params = {
        'url': url,
        'key': api_key,
        'strategy': 'desktop',  # oder 'mobile'
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