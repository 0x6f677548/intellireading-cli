import math
import re
import logging


class RegExBoldMetaguider:
    _body_regex = re.compile(r"<body[^>]*>(.*)</body>", re.DOTALL)
    _text_block_regex = re.compile(r"(?<!<b)>[^\S]*[^\s<][^<]*[^\S\n]*<")
    _word_pattern_regex = re.compile(r"\b\w+\b", re.UNICODE)
    _entity_ref_regex = re.compile(r"(&[#a-zA-Z][a-zA-Z0-9]*;)")
    _logger = logging.getLogger(__name__)

    def __init__(self, fallback_encoding: str = "utf-8") -> None:
        self._fallback_encoding = fallback_encoding

    def _bold_word(self, word: str) -> str:
        # this is the function that is called for each word

        # if the word is an empty string, whitespace or new line, return it
        if not word.strip():
            return word

        _length = len(word)
        midpoint = 1 if _length in (1, 3) else math.ceil(len(word) / 2)
        return f"<b>{word[:midpoint]}</b>{word[midpoint:]}"  # Bold the first half of the word

    def _bold_node_text_part(self, part: str) -> str:
        # is this part an entity reference?
        if self._entity_ref_regex.match(part):
            return part
        return self._word_pattern_regex.sub(lambda m: self._bold_word(m.group()), part)

    def _bold_text_node(self, node: str) -> str:
        # this is the function that is called for each text node
        node_text = node[1:-1]

        # split the node_text into parts based on the entity references
        node_text_parts = self._entity_ref_regex.split(node_text)

        new_node_text = "".join(map(self._bold_node_text_part, node_text_parts))

        if node_text != new_node_text:
            return ">" + new_node_text + "<"
        return node

    def _bold_document(self, html: str) -> str:
        # get the body. If there is no body, return the original html
        match = self._body_regex.search(html)
        if match:
            body = match.group(1)
        else:
            return html

        # find all text nodes in the body and trigger the bolding of the words
        body = self._text_block_regex.sub(lambda m: self._bold_text_node(m.group()), body)

        html = html.replace(match.group(1), body)
        return html

    def _get_encoding_using_lxml(self, xhtml_document: bytes) -> str | None:
        from lxml import etree

        _parser = etree.XMLParser(resolve_entities=False)
        _doc = etree.fromstring(xhtml_document, parser=_parser).getroottree()  # noqa: S320
        _docinfo = _doc.docinfo
        return _docinfo.encoding

    def _get_encoding_using_bom(self, xhtml_document: bytes) -> str | None:
        if xhtml_document.startswith(b"\xef\xbb\xbf"):
            return "utf-8"
        elif xhtml_document.startswith(b"\xff\xfe"):
            return "utf-16-le"
        elif xhtml_document.startswith(b"\xfe\xff"):
            return "utf-16-be"
        elif xhtml_document.startswith(b"\x00\x00\xfe\xff"):
            return "utf-32-be"
        elif xhtml_document.startswith(b"\xff\xfe\x00\x00"):
            return "utf-32-le"
        else:
            return None

    def _get_encoding_using_xml_header(self, xhtml_document: bytes) -> str | None:
        # if the document does not start with an XML header, return None. This is not a xml document
        if not xhtml_document.startswith(b"<?xml "):
            return None

        xml_header_end = xhtml_document.find(b"?>") + 1
        if xml_header_end == 0:
            msg = "Invalid XHTML document. Could not find closing XML element."
            raise ValueError(msg)

        header = xhtml_document[:xml_header_end].decode("utf-8")
        match = re.search(r'encoding=(["\'])([a-zA-Z][a-zA-Z0-9-]{0,38}[a-zA-Z0-9])\1', header)
        if match:
            return match.group(2)
        else:
            # although the XML header is present, it does not contain an encoding
            # this is not a valid XHTML document, but we can still try to detect the encoding on a later stage
            # and we will not raise an exception
            return None

    def _get_encoding(self, xhtml_document: bytes) -> str:
        _encoding = self._get_encoding_using_xml_header(xhtml_document)

        if not _encoding:
            self._logger.debug(
                "Could not detect the encoding of the XHTML document using the XML header. "
                "Trying to detect the encoding using the BOM."
            )
            _encoding = self._get_encoding_using_bom(xhtml_document)

        if not _encoding:
            self._logger.debug(
                "Could not detect the encoding of the XHTML document. Trying to detect the encoding using lxml."
            )
            _encoding = self._get_encoding_using_lxml(xhtml_document)

        return _encoding or self._fallback_encoding

    def metaguide_xhtml_document(self, xhtml_document: bytes) -> bytes:
        # if none of the methods to detect the encoding work, use utf-8
        _encoding = self._get_encoding(xhtml_document) or "utf-8"

        _html = xhtml_document.decode(_encoding)
        _bolded_html = self._bold_document(_html)
        return _bolded_html.encode(_encoding)
