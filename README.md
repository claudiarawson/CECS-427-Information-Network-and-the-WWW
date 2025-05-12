
# Web Crawler and Graph Analyzer

This project implements a web crawler that explores a website and builds a graph representation of its structure. It also allows you to load and analyze pre-existing graph files. The tool provides functionality to analyze the degree distribution and compute the PageRank of nodes in the graph.

## Features

- **Web Crawling**: Crawl a website from a list of seed URLs and build a directed graph of the visited pages.
- **Graph Analysis**: Load an existing graph in GML format and perform analysis.
- **Degree Distribution**: Generate a log-log plot of the degree distribution of the graph.
- **PageRank Calculation**: Calculate the PageRank of each node in the graph and save the results to a file.

## Prerequisites

Before using this tool, you will need to install the following Python libraries:

- `argparse`: For handling command-line arguments.
- `numpy`: For numerical operations.
- `networkx`: For graph manipulation and analysis.
- `matplotlib`: For plotting graphs.
- `scrapy`: For web crawling.

You can install the dependencies using `pip`:

```bash
pip install numpy networkx matplotlib scrapy
```

## Usage

You can run the script from the command line with various options depending on your use case.

### 1. Web Crawling

To crawl a website starting from a set of seed URLs and save the crawled graph:

```bash
python crawler.py --crawler <seed_file> --crawler_graph <output_graph_file.gml> [--loglogplot] [--pagerank_values <output_pagerank_file.txt>]
```

- `--crawler`: Path to the seed file (a text file containing the maximum number of nodes, the domain to crawl, and the list of seed URLs).
- `--crawler_graph`: Path to save the generated graph in GML format.
- `--loglogplot`: Optionally, generate a log-log plot of the degree distribution of the graph.
- `--pagerank_values`: Optionally, output the PageRank values to a text file.

Example seed file format:
```
10
https://example.com
https://example.com/page1
https://example.com/page2
...
```

### 2. Load and Analyze an Existing Graph

To load an existing graph from a GML file and perform analysis:

```bash
python crawler.py --input <input_graph_file.gml> [--loglogplot] [--pagerank_values <output_pagerank_file.txt>]
```

- `--input`: Path to the GML graph file.
- `--loglogplot`: Optionally, generate a log-log plot of the degree distribution of the graph.
- `--pagerank_values`: Optionally, output the PageRank values to a text file.

### Example of Use:

```bash
python crawler.py --crawler seeds.txt --crawler_graph crawled_graph.gml --loglogplot --pagerank_values pagerank.txt
```

This command will:
- Crawl the website based on the `seeds.txt` file,
- Save the crawled graph to `crawled_graph.gml`,
- Generate a log-log degree distribution plot,
- Save the PageRank values to `pagerank.txt`.

## Output

- **Crawled Web Graph**: A directed graph where each node represents a web page and edges represent links between pages.
- **Log-Log Degree Distribution Plot**: A plot showing the distribution of the degree of nodes in the graph.
- **PageRank Values**: A ranking of nodes in the graph based on their relative importance.

---

## Notes

- If you are crawling a large number of nodes, be mindful of the server’s resources and avoid overloading it. Use the `--loglogplot` option to analyze the graph’s degree distribution once you have collected the data.
- The `scrapy` crawler is configured to follow only HTML links and will ignore other resources like images, JavaScript, and PDF files.