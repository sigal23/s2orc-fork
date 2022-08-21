from dataclasses_json import DataClassJsonMixin, dataclass_json
from typing import List, Dict, Union, Iterator
from dataclasses import dataclass, field


@dataclass_json
@dataclass(frozen=True)
class CharSpan:
    first: int
    last: int

    def str(self, text):
        return text[self.first : self.last + 1]


@dataclass_json
@dataclass(frozen=True)
class CharLabeledSpan(CharSpan):
    label: str


@dataclass_json
@dataclass(frozen=True)
class GoldEntity(CharLabeledSpan):
    pass

@dataclass(frozen=True)
class SectionTitle(DataClassJsonMixin):
    name: str

    # represents the nesting level.
    # e.g. if a document has the numbered sections:   1, 1.1, 1.2, 2, 2.1, 2.1.1, 2.2.2, 2.2, 3
    # then the corresponding nesting levels are:      1, 2,   2,   1, 2,   3,     3,     2,   1
    nesting: int = field(default_factory=int)


@dataclass(frozen=True)
class Paragraph(DataClassJsonMixin):
    text: str
    entities: List[GoldEntity] = field(default_factory=list)

    def with_cb_entities(self, entities: List[GoldEntity]) -> "Paragraph":
        return Paragraph(self.text, list(set(self.entities + entities)))

    def split_long_paragraph(
        self, min_length: int = 0, separators: List[str] = [".\n", '."\n', "\n\n"]
    ) -> Iterator["Paragraph"]:
        if len(self.entities) > 0:
            raise Exception("Cannot split paragraphs with supplied entities.")
        if len(self.text) < min_length:
            yield self
            return
        text = self.text
        for sep in separators:
            text = text.replace(sep, sep + "~~~SEP~~~")
        texts = [t.strip() for t in text.split("~~~SEP~~~")]
        for text in texts:
            yield Paragraph(text=text, entities=[])

