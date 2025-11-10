import gradio as gr
import json
import csv
import os
import time
from pathlib import Path
from firecrawl import Firecrawl
from datetime import datetime
import re

# Initialize Firecrawl
def init_firecrawl(api_key):
    return Firecrawl(api_key=api_key)

def sanitize_filename(url):
    """Create a safe filename from URL"""
    # Remove protocol and special characters
    name = re.sub(r'https?://', '', url)
    name = re.sub(r'[^\w\-_.]', '_', name)
    return name[:100]  # Limit length

def scrape_urls(api_key, urls_text, csv_file, output_format, output_dir, delay_seconds):
    """Scrape URLs and save results"""
    if not api_key:
        return "Error: Please provide a Firecrawl API key"
    
    # Collect URLs from text input and CSV
    urls = []
    
    if urls_text:
        urls.extend([url.strip() for url in urls_text.split('\n') if url.strip()])
    
    if csv_file:
        with open(csv_file.name, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    urls.extend([url.strip() for url in row if url.strip()])
    
    if not urls:
        return "Error: No URLs provided"
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Initialize Firecrawl
    app = init_firecrawl(api_key)
    
    results = []
    success_count = 0
    fail_count = 0
    
    for i, url in enumerate(urls, 1):
        start_time = time.time()
        
        try:
            # Scrape the URL
            result = app.scrape(url, formats=["markdown", "html"])
            
            # Generate filename
            filename = sanitize_filename(url)
            
            if output_format == "JSON":
                filepath = output_path / f"{filename}.json"
                # Convert Document object to dict for JSON serialization
                result_dict = {
                    'url': url,
                    'markdown': result.markdown if hasattr(result, 'markdown') else '',
                    'html': result.html if hasattr(result, 'html') else '',
                    'metadata': result.metadata if hasattr(result, 'metadata') else {}
                }
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(result_dict, f, indent=2, ensure_ascii=False)
            else:  # Markdown
                filepath = output_path / f"{filename}.md"
                # Access markdown attribute directly from Document object
                content = result.markdown if hasattr(result, 'markdown') else ''
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"# {url}\n\n")
                    f.write(content)
            
            elapsed = time.time() - start_time
            success_count += 1
            results.append(f"✓ [{i}/{len(urls)}] Scraped in {elapsed:.2f}s: {url} → {filepath.name}")
        
        except Exception as e:
            elapsed = time.time() - start_time
            fail_count += 1
            error_msg = str(e)
            # Extract wait time from rate limit error if present
            if "retry after" in error_msg.lower():
                results.append(f"✗ [{i}/{len(urls)}] Rate limited ({elapsed:.2f}s): {url}")
            else:
                results.append(f"✗ [{i}/{len(urls)}] Failed ({elapsed:.2f}s): {url} - {error_msg[:100]}")
        
        # Add delay between requests (except after last URL)
        if i < len(urls) and delay_seconds > 0:
            time.sleep(delay_seconds)
    
    summary = f"\n\n{'='*60}\nCompleted: {success_count} succeeded, {fail_count} failed out of {len(urls)} URLs\nOutput directory: {output_path.absolute()}"
    return "\n".join(results) + summary

# Create Gradio interface
with gr.Blocks(title="Firecrawl Scraper") as demo:
    gr.Markdown("# 🔥 Firecrawl URL Scraper")
    gr.Markdown("Scrape multiple URLs and save as JSON or Markdown files")
    
    with gr.Row():
        api_key_input = gr.Textbox(
            label="Firecrawl API Key",
            placeholder="Enter your Firecrawl API key",
            type="password"
        )
    
    with gr.Row():
        with gr.Column():
            urls_input = gr.Textbox(
                label="URLs (one per line)",
                placeholder="https://example.com\nhttps://another-site.com",
                lines=10
            )
            csv_input = gr.File(
                label="Or upload CSV file with URLs",
                file_types=[".csv"]
            )
        
        with gr.Column():
            format_choice = gr.Radio(
                choices=["JSON", "Markdown"],
                value="Markdown",
                label="Output Format"
            )
            output_dir_input = gr.Textbox(
                label="Output Directory",
                value="scraped_data",
                placeholder="scraped_data"
            )
            delay_input = gr.Slider(
                minimum=0,
                maximum=30,
                value=6,
                step=1,
                label="Delay Between Requests (seconds)",
                info="Recommended: 6s for free tier (10 req/min limit)"
            )
            scrape_btn = gr.Button("Start Scraping", variant="primary")
    
    output_text = gr.Textbox(
        label="Results",
        lines=15,
        max_lines=20
    )
    
    scrape_btn.click(
        fn=scrape_urls,
        inputs=[api_key_input, urls_input, csv_input, format_choice, output_dir_input, delay_input],
        outputs=output_text
    )

if __name__ == "__main__":
    demo.launch()
