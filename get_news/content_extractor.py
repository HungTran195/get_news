import bs4
import math


class Content_Extractor:
    """Extract content from html"""

    def __init__(self, soup, children=[], is_string=False):
        self.soup = soup
        self.parent = None
        self.children = list(children)
        self.is_string = is_string

        self.get_features()

    @classmethod
    def create(cls, soup):
        return Content_Extractor.create_nodes(soup)

    @classmethod
    def create_nodes(cls, soup):
        if isinstance(soup, bs4.element.Tag) or isinstance(soup, bs4.BeautifulSoup):
            valid_children = list(filter(Content_Extractor.is_valid_soup_node, soup.children))
            children = list(map(Content_Extractor.create_nodes, valid_children))

            parent_of_child = Content_Extractor(soup, children)

            for child in children:
                child.parent = parent_of_child

            return parent_of_child

        elif isinstance(soup, bs4.element.NavigableString):
            return Content_Extractor(soup)

    @classmethod
    def is_valid_soup_node(cls, soup_node):
        if isinstance(soup_node, bs4.element.Comment):
            return False
        if isinstance(soup_node, bs4.element.NavigableString):
            if soup_node.string.strip():
                return True
            else:
                return False
        else:
            return True

    def get_features(self):
        if isinstance(self.soup, bs4.element.NavigableString):
            self.characters = len(self.soup)
            self.tags = 1
            self.link_characters = 0
            self.link_tags = 0
            self.is_string = True
        else:
            self.characters = sum(n.characters for n in self.children)
            self.tags = sum(n.tags for n in self.children)
            self.tags += 1

            if self.soup.name == 'a':
                self.link_characters = self.characters
                self.link_tags = 1
            else:
                self.link_characters = sum(n.link_characters for n in self.children)
                self.link_tags = sum(n.link_tags for n in self.children)

        self.text_density = self.characters / max(1, self.tags)

    def get_child(self):
        yield self
        for child in self.children:
            for c in child.get_child():
                yield c

    def get_path(self, node):
        path = []
        while node:
            path.append(node)
            node = node.parent
        return path

    def mark_content(self):
        body = self

        def composite_text_density(node):
            prop_hyperlink_tag = 1.0 * max(1, node.tags) / max(1, node.link_tags)
            prop_hyperlink_characters = 1.0 * max(1, node.characters) / max(1, node.link_characters)

            a = 1.0 * max(1, node.characters) * max(1, node.link_characters) / max(1, (node.characters - node.link_characters))
            b = 1.0 * max(1, body.link_characters) * max(1, node.characters) / max(1, body.characters)

            natural_log = math.log(a + b + math.exp(1))
            node.composite_text_density = node.text_density * math.log((prop_hyperlink_characters * prop_hyperlink_tag), natural_log)

        def density_sum(node):
            if node.children and len(node.children) > 0:
                node.density_sum = sum(n.composite_text_density for n in node.children)
            else:
                node.density_sum = node.composite_text_density

        for node in self.get_child():
            composite_text_density(node)

        for node in self.get_child():
            density_sum(node)

    def find_max_density_sum(self):
        max_density_sum = float("-inf")
        node_with_max_density_sum = None

        for node in self.get_child():
            if node.density_sum > max_density_sum:
                max_density_sum = node.density_sum
                node_with_max_density_sum = node

        path_to_body = self.get_path(node_with_max_density_sum)
        threshhold = min(path_to_body, key=(lambda x: x.composite_text_density))
        self.threshhold = threshhold.composite_text_density

    def extract(self):
        self.mark_content()
        self.find_max_density_sum()

        best_score = float('-inf')
        best_node = None
        for node in self.get_child():
            #         for node in self.soup.decendants:
            if isinstance(node, bs4.element.NavigableString):
                continue
            if node.density_sum > self.threshhold:
                if best_score < node.density_sum:
                    best_node = node
                    best_score = node.density_sum

        best_node = bs4.BeautifulSoup(str(best_node.soup), 'lxml')
        text = ''
        for child in best_node.descendants:
            if isinstance(child, bs4.element.NavigableString):
                if not child == '\n':
                    text += child
        self.best_node = best_node

        return text
