"""Writing the HTML with the pigeons' URLs is important. That's what this
thing does."""
# import pystache  # dropped
from abc import ABC, abstractmethod
import logging
import jinja2


class HTMLWriter(ABC):
    """I think this is a base class"""
    def __init__(self):
        pass

    @abstractmethod
    def write(self, filename, urls):
        """You wanna call this, but on a concrete class"""
        pass


"""Mustache was dropped because I need to access the first item in the images
array and Mustache is kinda sad about it, although probably possible with some
sick syntax. It seems however that this is a bit against the philosophy of
Mustache being "logic-less" and all that crap."""
# class MustacheHTMLWriter:
#     """Will write a nice HTML file given nice URLs"""
#     def __init__(self):
#         self.renderer = pystache.Renderer()
#         self.parsed_template = None
#         self.prepare_renderer()

#     def prepare_renderer(self):
#         """Load and prepare the mustache template and have some fun!"""
#         with open(settings.MUSTACHE_TEMPLATE) as template_file:
#             self.parsed_template = pystache.parse(template_file.read())

#     def write(self, filename, urls):
#         """Write the HTML with the URLs provided"""
#         context = {"images": [{"url": url} for url in urls]}
#         rendered = self.renderer.render(self.parsed_template, context)
#         print("UNFNFUNF", rendered)


class Jinja2HTMLWriter(HTMLWriter):
    """Hello, I'm gonna use a jinja2 template to write your pigeon pictures HTML"""
    def __init__(self, template_filename, javascript_snippet_filename):
        super().__init__()
        self.template = None
        self.prepare_template(template_filename)
        self.javascript_snippet = self.load_javascript_snipet(javascript_snippet_filename)

    def prepare_template(self, template_filename):
        """Load template from disk and create a thing that can render it"""
        logging.info('Loading template from "%s"', template_filename)
        with open(template_filename) as template_file:
            template_content = template_file.read()
            self.template = jinja2.Template(template_content)

    @staticmethod
    def load_javascript_snipet(filename):
        """There is some silly JavaScript code that has a countdown to next pigeoning"""
        try:
            with open(filename) as js_file:
                return js_file.read()
        except IOError as exception:
            logging.warning("JavaScript snippet not found! %s", exception)
            return ""

    def write(self, filename, urls):
        logging.info('Writing %d URLs to HTML file "%s"', len(urls), filename)
        with open(filename, "w") as file_to_write:
            file_to_write.write(self.render_template(urls))

    def render_template(self, urls):
        return self.template.render(
            image_links=urls,
            javascript_snippet=self.javascript_snippet,
        )
