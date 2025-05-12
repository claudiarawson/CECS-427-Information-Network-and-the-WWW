import argparse
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import urljoin, urlparse


def parse_arguments():
    # Parse the command-line arguments for crawler, input files, and plotting options.
    parser = argparse.ArgumentParser(description="Web crawler and PageRank calculator.")
    parser.add_argument("--crawler", type=str, help="Path to the seed file for crawling.")
    parser.add_argument("--input", type=str, help="Path to the input graph file (GML format).")
    parser.add_argument("--loglogplot", action="store_true", help="Generate a log-log degree distribution plot.")
    parser.add_argument("--crawler_graph", type=str, help="Output file for the crawled graph in GML format.")
    parser.add_argument("--pagerank_values", type=str, help="Output file for storing PageRank values.")
    return parser.parse_args()


def load_seed_file(filepath):
    # Load the seed file containing the crawling configurations (max nodes, domain, seed URLs).
    try:
        with open(filepath, 'r') as file:
            lines = [line.strip() for line in file if line.strip()]
            max_nodes = int(lines[0])
            domain = lines[1]
            seeds = lines[2:]
            return max_nodes, domain, seeds
    except Exception as e:
        print(f"Error reading seed file: {e}")
        return None, None, None


def plot_degree_distribution(graph):
    # Plot the log-log degree distribution of the graph.
    degrees = [deg for _, deg in graph.degree()]
    unique_degrees, counts = np.unique(degrees, return_counts=True)
    plt.figure()
    plt.loglog(unique_degrees, counts, marker='o', linestyle='None')
    plt.title("Log-Log Degree Distribution")
    plt.xlabel("Degree")
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.show()


class WebSpider(scrapy.Spider):
    # A Scrapy spider to crawl the web and construct a directed graph of visited URLs.
    name = "web_spider"
    custom_settings = {
        'DOWNLOAD_DELAY': 1.0,  # Delay between requests
        'DEPTH_LIMIT': 3,       # Maximum depth for crawling
        'LOG_LEVEL': 'INFO',    # Logging level
    }

    def __init__(self, domain, start_urls, max_nodes, **kwargs):
        # Initialize the spider with the domain, seed URLs, and max nodes to crawl.
        super().__init__(**kwargs)
        self.allowed_domain = domain.replace("www.", "")
        self.start_urls = start_urls
        self.max_nodes = max_nodes
        self.visited = set()
        self.frontier = set(start_urls)
        self.graph = nx.DiGraph()  # Directed graph to store URLs and edges

    def start_requests(self):
        # Start requests from the seed URLs.
        for url in self.frontier:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        # Parse the response and add the URL to the graph if it's valid.
        if not self._is_html(response):
            return

        url = self._normalize(response.url)
        if url in self.visited or len(self.visited) >= self.max_nodes:
            return

        print(f"[{len(self.visited)}/{self.max_nodes}] Visiting: {url}")
        self.visited.add(url)
        self.frontier.discard(url)
        self.graph.add_node(url)

        for link in response.css('a::attr(href)').getall():
            absolute_link = self._normalize(urljoin(url, link))
            if not self._valid_link(absolute_link):
                continue

            if (absolute_link not in self.visited and absolute_link not in self.frontier
                    and len(self.visited) + len(self.frontier) < self.max_nodes):
                self.frontier.add(absolute_link)
                yield scrapy.Request(absolute_link, callback=self.parse, dont_filter=True)

            if self._is_html_link(absolute_link):
                self.graph.add_edge(url, absolute_link)

    def _normalize(self, url):
        # Normalize a URL to remove the trailing slash and standardize its format.
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip('/')

    def _valid_link(self, url):
        # Check if the URL is valid for crawling based on the allowed domain and extensions.
        parsed = urlparse(url)
        domain = parsed.netloc.replace("www.", "")
        path = parsed.path.lower()
        disallowed_ext = ('.pdf', '.jpg', '.jpeg', '.png', '.gif', '.css', '.js', '.svg', '.ico', '.mp4', '.webp')
        return (domain == self.allowed_domain
                and parsed.scheme in {"http", "https"}
                and not any(path.endswith(ext) for ext in disallowed_ext))

    def _is_html(self, response):
        # Check if the response content is HTML.
        content_type = response.headers.get('Content-Type', b'').decode('utf-8').lower()
        return 'text/html' in content_type

    def _is_html_link(self, url):
        # Check if the URL is an HTML link (e.g., ends with .html or .htm).
        path = urlparse(url).path.lower()
        return path.endswith(('.html', '.htm', '')) or path.endswith('/')


def crawl_website(domain, seeds, max_nodes):
    # Crawl the website using the provided domain and seed URLs, and return the constructed graph.
    process = CrawlerProcess(settings={"USER_AGENT": "Mozilla/5.0"})
    graph_data = {}

    class CollectorSpider(WebSpider):
        def closed(self, reason):
            graph_data["graph"] = self.graph

    process.crawl(CollectorSpider, domain=domain, start_urls=seeds, max_nodes=max_nodes)
    process.start()
    return graph_data.get("graph", nx.DiGraph())


def main():
    # Main function to handle argument parsing, crawling, graph loading, and plotting.
    args = parse_arguments()
    graph = None

    if args.crawler:
        max_nodes, domain, seeds = load_seed_file(args.crawler)
        if domain is None:
            print("Invalid seed file. Exiting.")
            return
        clean_domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
        print(f"Starting crawl on domain: {clean_domain} with {len(seeds)} seeds (max {max_nodes} nodes)")

        graph = crawl_website(clean_domain, seeds, max_nodes)

        if args.crawler_graph:
            nx.write_gml(graph, args.crawler_graph)
            print(f"Graph saved to {args.crawler_graph}")

        plt.figure(figsize=(15, 15))
        pos = nx.spring_layout(graph, k=0.15, iterations=20)
        nx.draw_networkx_nodes(graph, pos, node_size=20, node_color='dodgerblue')
        nx.draw_networkx_edges(graph, pos, alpha=0.1)
        plt.title("Crawled Web Graph")
        plt.axis('off')
        plt.show()

    if args.input:
        try:
            graph = nx.read_gml(args.input)
            print(f"Graph loaded from {args.input}")
            plt.figure(figsize=(18, 18))
            pos = nx.spring_layout(graph, k=0.1, iterations=20)
            nx.draw_networkx_nodes(graph, pos, node_size=50, node_color='skyblue')
            nx.draw_networkx_edges(graph, pos, alpha=0.3)
            plt.title("Loaded Web Graph")
            plt.axis('off')
            plt.show()
        except FileNotFoundError:
            print(f"Error: Input file {args.input} not found.")

    if graph is None:
        print("No graph data available. Exiting.")
        return

    if args.loglogplot:
        plot_degree_distribution(graph)

    if args.pagerank_values:
        pagerank = nx.pagerank(graph)
        with open(args.pagerank_values, 'w') as f:
            for node, rank in sorted(pagerank.items(), key=lambda x: x[1], reverse=True):
                f.write(f"{node} {rank}\n")
        print(f"PageRank values saved to {args.pagerank_values}")


if __name__ == "__main__":
    main()
