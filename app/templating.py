from string import Template
import os
import config



def render_from_string(template_string, mapping):
    template = Template(template_string)
    result = template.safe_substitute(mapping)
    return [result.encode("utf-8")]


def template_render(templatename, mapping=None):
    tpath = os.path.join(config.TEMPLATE_DIR, templatename)
    if not os.path.exists(tpath):
        print("Can't find template at:", tpath)
        return [b"Error processing template"]

    # read the template from the given file
    h = open(tpath, 'r')
    template = h.read()
    h.close()

    # return render_from_string(template, mapping)
    return [template.encode("utf-8")]
