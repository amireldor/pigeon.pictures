"""Writing the HTML with the pigeons' URLs is important. That's what this
thing does."""
import pystache
import settings


class HTMLWriter:
    """Will write a nice HTML file given nice URLs"""
    def __init__(self):
        pass

    def write(self, filename, urls):
        """Write the HTML with the URLs provided"""
        pass


class MustacheHTMLWriter:
    """Will write a nice HTML file given nice URLs"""
    def __init__(self):
        self.renderer = pystache.Renderer()
        self.parsed_template = None
        self.prepare_renderer()

    def prepare_renderer(self):
        """Load and prepare the mustache template and have some fun!"""
        with open(settings.MUSTACHE_TEMPLATE) as template_file:
            self.parsed_template = pystache.parse(template_file.read())

    def write(self, filename, urls):
        """Write the HTML with the URLs provided"""
        context = {"images": [{"url": url} for url in urls]}
        rendered = self.renderer.render(self.parsed_template, context)
        print("UNFNFUNF", rendered)