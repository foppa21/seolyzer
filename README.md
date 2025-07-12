# SEOlyzer - SEO Command Line Tool

A powerful CLI tool for SEO analysis of websites, checking various SEO metrics and indicators.

## Requirements

- Python 3.11 or 3.12 (recommended, Python 3.13 is not recommended for lxml)
- Git (optional, for cloning the repo)

### Python package requirements

The following Python packages are required (see also requirements.txt):

- requests==2.31.0
- beautifulsoup4==4.12.2
- PyYAML==6.0.1
- click==8.1.7
- rich==13.7.0
- aiohttp==3.9.1
- python-dotenv==1.0.0
- html5lib==1.1

## Installation

1. Clone the repository (or extract the ZIP):
   ```bash
   git clone https://github.com/foppa21/seolyzer.git
   cd seolyzer
   ```

2. Create a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   python3 -m pip install -r requirements.txt
   ```

## Usage

### Analyze a single URL

```bash
python3 seolyzer.py https://www.example.com --output report.csv
```

### Analyze multiple URLs

1. Create a file called `urls.txt`, one URL per line (with http/https):
   ```
   https://www.example.com
   https://www.example.org
   ...
   ```
2. Then run:
   ```bash
   python3 seolyzer.py urls.txt --output report.csv
   ```

## Output

- The results are saved as a CSV file.
- Each row corresponds to an analyzed URL.
- The most important SEO metrics are output as columns (see example below).

## Example CSV Columns

- URL
- Title tag content
- Description tag content
- H1 header count
- H1 header content
- H2 header count
- H2 header content
- Image count
- Load time
- Size
- Viewport tag
- Canonical
- hreflang
- Noindex

## Notes

- For large URL lists, the analysis may take some time.
- The tool requires internet access to analyze the pages.
- The `urls.txt` file must be in the same directory as the script or specified with an absolute path.

## License

MIT License

## Contributing

Contributions are welcome! Please read our Contributing Guidelines for details.
