from os.path import join
import json
import re
import string
from collections import OrderedDict

from markdown import Markdown


class Term(dict):
    id = None

    def __init__(self, *args, key="", **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.id = key

    def set_item(self, item, data, lang="de", append=False):
        if lang not in self:
            self[lang] = {}
        if append and item in self[lang]:
            self[lang][item] += f" {data}"
        else:
            self[lang][item] = data

    def merge(self, term):
        for k, v in term.items():
            if k not in self:
                self[k] = v


class Glossary(dict):
    DEF_RE = re.compile(r"^[ ]{0,3}\[[ ]*id=([^\]]*)[ ]*\]")
    localized_glossaries = {}

    def __init__(self, json_file=None):
        super(Glossary, self).__init__()
        if json_file:
            self.parse_json(json_file)

    def get_localized_glossary(self, lang):
        glossary = OrderedDict((c, {}) for c in string.ascii_uppercase)
        for t in self.values():
            if lang in t:
                term = t[lang]["term"]
                glossary[term[0].upper()][term] = t[lang]["definition"]
        return glossary

    def parse_markdown(self, filename, lang="de"):
        md = Markdown()
        with open(filename, "r", encoding="utf-8") as fh:
            lines = fh.readlines()
            etree = md.parser.parseDocument(lines)
        terms = []
        current_term = None
        for item in etree.iter():

            if item.tag == "h2":
                current_term = Term()
                terms.append(current_term)
                current_term.set_item("term", item.text.strip(), lang=lang)

            elif item.tag == "p" and current_term:
                m = self.DEF_RE.search(item.text)
                if m:
                    current_term.id = m.groups()[0].strip()
                else:
                    current_term.set_item(
                        "definition", item.text, append=True, lang=lang
                    )

        for t in terms:
            if t.id in self:
                self[t.id].merge(t)
            else:
                self[t.id] = t
        self.localized_glossaries[lang] = self.get_localized_glossary(lang)

    def parse_json(self, filename):
        with open(filename) as fh:
            raw_data = json.load(fh)
        languages = set()
        for k, v in raw_data.items():
            self[k] = Term(key=k, **v)
            languages.update(v.keys())
        for lang in languages:
            self.localized_glossaries[lang] = self.get_localized_glossary(lang)

    @staticmethod
    def from_markdown(basedir="."):
        g = Glossary()
        for lang, fname in {'de': 'Glossar.md', 'en': 'Glossary.md'}.items():
            g.parse_markdown(join(basedir, fname), lang=lang)
        return g


if __name__ == "__main__":
    g = Glossary.from_markdown()
    with open("glossary.json", "w") as fh:
        json.dump({k: g[k] for k in sorted(g)}, fh, indent=2)
