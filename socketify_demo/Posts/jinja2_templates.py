from jinja2 import Environment, FileSystemLoader

class Jinja2Template:
  def __init__(self, searchpath, encoding="utf-8", followlinks=False):
    self.env = Environment(
        loader=FileSystemLoader(searchpath, encoding, followlinks)
    )
  
  # You can also add caching and logging strategy here if you want ;)
  def render(self, templatename, **kwargs):
    try:
      template = self.env.get_template(templatename)
      return template.render(**kwargs)
    except Exception as err:
      return str(err)

