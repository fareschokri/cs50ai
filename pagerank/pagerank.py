import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    pr_dict = dict()
    num_pages = len(corpus)
    num_links = len(corpus[page])
    if num_links == 0:
        for pg in corpus:
            pr_dict[pg] = 1 / len(corpus)
        return pr_dict

    for pg in corpus:
        prob = (1 - damping_factor) / num_pages
        if pg in corpus[page]:
            prob += (damping_factor / num_links)
        pr_dict[pg] = prob
    return pr_dict


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    probabilities = dict()
    for page in corpus:
        probabilities[page] = 0
    i = 0
    while i < n:
        if i == 0:
            sample_page = random.choice(list(probabilities.keys()))
        else:
            sample_page = random.choices(list(probabilities.keys()), weights=list(probabilities.values()), k=1)[0]
        new_probabilities = transition_model(corpus, sample_page, damping_factor)
        for page in new_probabilities:
            probabilities[page] += new_probabilities[page]
        i += 1
    for page in probabilities:
        probabilities[page] = probabilities[page] / n
    total = sum(list(probabilities.values()))
    for page in probabilities:
        probabilities[page] = probabilities[page] / total
    return probabilities


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pages_num = len(corpus)
    initial_prob = 1 / pages_num
    probabilities = dict()
    for page in corpus:
        probabilities[page] = initial_prob
    candidates_list = list(corpus)
    while len(candidates_list) > 0:
        for page in candidates_list:
            prob_total = 0
            for extra in corpus:
                if not corpus[extra]:
                    prob_total += probabilities[extra] / len(corpus)
                if page in corpus[extra]:
                    prob_total += probabilities[extra] / len(corpus[extra])

            new_pr = ((1 - damping_factor) / pages_num) + damping_factor * prob_total

            if abs(new_pr - probabilities[page]) < 0.001:
                candidates_list.remove(page)

            probabilities[page] = new_pr
    total = sum(list(probabilities.values()))
    for page in probabilities:
        probabilities[page] = probabilities[page] / total

    return probabilities


if __name__ == "__main__":
    main()
