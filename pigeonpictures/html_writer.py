"""Writing the HTML with the pigeons' URLs is important. That's what this
thing does."""
# import pystache  # dropped
from abc import ABC, abstractmethod
import logging
import jinja2
from datetime import datetime, timedelta


def calculate_next_update_time(
    now: datetime = datetime.today(),
    update_interval: timedelta = timedelta(minutes=30),
) -> datetime:
    minutes = now.minute
    if minutes >= 30:
        at_zero_or_half_hour = now + timedelta(minutes=60 - minutes)
    else:
        at_zero_or_half_hour = now + timedelta(minutes=30 - minutes)
    return at_zero_or_half_hour


class HTMLWriter(ABC):
    """I think this is a base class"""

    def __init__(self):
        pass

    @abstractmethod
    def write(self, filename, urls):
        """You wanna call this, but on a concrete class"""
        pass

    @abstractmethod
    def render(self, urls):
        """Just render the file, nothing written"""
        pass


class Jinja2HTMLWriter(HTMLWriter):
    """Hello, I'm gonna use a jinja2 template to write your pigeon pictures HTML"""

    def __init__(self, template_filename, javascript_snippet_filename):
        super().__init__()
        self.template = None
        self.prepare_template(template_filename)
        self.javascript_next_update_snippet = self.make_javascript_next_update_snippet()
        self.javascript_snippet = self.load_javascript_snipet(
            javascript_snippet_filename
        )

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
            file_to_write.write(self.render(urls))

    def render(self, urls):
        return self.template.render(
            image_links=urls, javascript_snippet=self.javascript_snippet,
        )
