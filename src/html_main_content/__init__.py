"""Extract the main content of an HTML page as clean text blocks."""

from __future__ import annotations

import logging
import re
from collections.abc import Mapping
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Union

__all__ = ["ExtractError", "Extracted", "extract"]

__version__ = "0.1.0"

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

VOID_ELEMENTS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}

REMOVE_TAGS = {
    "script",
    "style",
    "noscript",
    "template",
    "iframe",
    "svg",
    "canvas",
    "form",
    "button",
    "select",
    "input",
    "nav",
    "aside",
    "header",
    "footer",
}

BOILERPLATE_TOKENS = {
    "nav",
    "menu",
    "footer",
    "sidebar",
    "comment",
    "comments",
    "share",
    "social",
    "advert",
    "ad",
    "ads",
    "promo",
    "cookie",
    "banner",
    "related",
    "breadcrumb",
    "newsletter",
    "popup",
}

BLOCK_TAGS = {
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "p",
    "li",
    "pre",
    "blockquote",
    "th",
    "td",
}


class ExtractError(Exception):
    """Raised when extraction cannot produce content."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class Extracted:
    """Result of main-content extraction."""

    title: str
    text: str
    blocks: tuple[str, ...]
    removed: Mapping[str, int]


Node = Union["_Text", "_Element"]


@dataclass
class _Text:
    data: str


@dataclass
class _Element:
    tag: str
    attrs: dict[str, str]
    children: list[Node]


class _HTMLParser(HTMLParser):
    """Build a light element tree with depth limit."""

    def __init__(self, max_depth: int):
        super().__init__(convert_charrefs=True)
        self.max_depth = max_depth
        self.root = _Element(tag="", attrs={}, children=[])
        self.stack: list[_Element] = []

    def _current_parent(self) -> _Element:
        return self.stack[-1] if self.stack else self.root

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if len(self.stack) >= self.max_depth:
            raise ExtractError("too_deep")
        attr_dict: dict[str, str] = {}
        for key, value in attrs:
            attr_dict[key.lower()] = value if value is not None else ""
        elem = _Element(tag=tag, attrs=attr_dict, children=[])
        self._current_parent().children.append(elem)
        if tag not in VOID_ELEMENTS:
            self.stack.append(elem)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag.lower() not in VOID_ELEMENTS:
            self.stack.pop()

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in VOID_ELEMENTS:
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data: str) -> None:
        self._current_parent().children.append(_Text(data))


def _is_hidden(elem: _Element) -> bool:
    if "hidden" in elem.attrs:
        return True
    aria = elem.attrs.get("aria-hidden", "").strip().lower()
    if aria == "true":
        return True
    style = elem.attrs.get("style", "")
    if style:
        collapsed = re.sub(r"\s+", "", style).lower()
        if "display:none" in collapsed or "visibility:hidden" in collapsed:
            return True
    return False


def _is_boilerplate(elem: _Element) -> bool:
    role = elem.attrs.get("role", "").strip().lower()
    if role in {"navigation", "banner", "contentinfo", "complementary"}:
        return True
    for attr_name in ("class", "id"):
        attr_val = elem.attrs.get(attr_name, "")
        if not attr_val:
            continue
        tokens = re.split(r"[\s_-]", attr_val)
        for token in tokens:
            if token.lower() in BOILERPLATE_TOKENS:
                return True
    return False


def _prune(node: Node, in_article_or_main: bool, removed: dict[str, int]) -> Node | None:
    if isinstance(node, _Text):
        return node
    tag = node.tag
    if tag in REMOVE_TAGS and not (tag in {"header", "footer"} and in_article_or_main):
        removed["tags"] += 1
        return None
    if _is_hidden(node):
        removed["hidden"] += 1
        return None
    if _is_boilerplate(node):
        removed["boilerplate"] += 1
        return None
    child_in = in_article_or_main or tag in {"article", "main"}
    new_children: list[Node] = []
    for child in node.children:
        pruned = _prune(child, child_in, removed)
        if pruned is not None:
            new_children.append(pruned)
    return _Element(tag=tag, attrs=node.attrs, children=new_children)


def _collect_elements(node: Node, tags: set[str], result: list[_Element]) -> None:
    if isinstance(node, _Text):
        return
    if node.tag in tags:
        result.append(node)
    for child in node.children:
        _collect_elements(child, tags, result)


def _element_text_length(elem: _Element) -> int:
    total = 0
    for child in elem.children:
        if isinstance(child, _Text):
            total += len(child.data)
        elif child.tag == "br":
            total += 1
        else:
            total += _element_text_length(child)
    return total


def _density_info(elem: _Element) -> tuple[int, int]:
    text_chars = 0
    link_chars = 0

    def walk(node: Node, in_link: bool) -> None:
        nonlocal text_chars, link_chars
        if isinstance(node, _Text):
            text_chars += len(node.data)
            if in_link:
                link_chars += len(node.data)
        elif node.tag == "br":
            text_chars += 1
            if in_link:
                link_chars += 1
        else:
            child_in_link = in_link or node.tag == "a"
            for child in node.children:
                walk(child, child_in_link)

    walk(elem, False)
    return text_chars, link_chars


def _score(elem: _Element) -> float:
    direct_sum = 0
    for child in elem.children:
        if isinstance(child, _Element) and child.tag in {"p", "pre", "blockquote"}:
            length = _element_text_length(child)
            if length >= 25:
                direct_sum += length
    text_chars, link_chars = _density_info(elem)
    if text_chars == 0:
        return 0.0
    return direct_sum * (1.0 - link_chars / text_chars)


def _normalize_inline_text(data: str) -> str:
    collapsed = re.sub(r"\s+", " ", data).strip()
    return collapsed


def _pre_text(elem: _Element) -> str:
    result = ""
    for child in elem.children:
        if isinstance(child, _Text):
            result += child.data
        elif child.tag == "br":
            result += "\n"
        elif child.tag in BLOCK_TAGS:
            continue
        else:
            result += _pre_text(child)
    return result


def _block_text(elem: _Element, for_pre: bool = False) -> str:
    if for_pre:
        return _pre_text(elem)
    pieces: list[str | None] = []

    def walk(node: Node) -> None:
        if isinstance(node, _Text):
            normalized = _normalize_inline_text(node.data)
            if normalized:
                pieces.append(normalized)
        elif node.tag == "br":
            pieces.append(None)
        elif node.tag in BLOCK_TAGS:
            return
        else:
            for child in node.children:
                walk(child)

    for child in elem.children:
        walk(child)
    result = ""
    for piece in pieces:
        if piece is None:
            if result and result[-1] == " ":
                result = result.rstrip()
            result += "\n"
        else:
            if result and result[-1] not in (" ", "\n"):
                result += " "
            result += piece
    return result.strip()


def _extract_blocks(candidate: _Element) -> list[str]:
    blocks: list[str] = []

    def walk(node: _Element, add_direct_text: bool) -> None:
        for child in node.children:
            if isinstance(child, _Text):
                if add_direct_text:
                    text = _normalize_inline_text(child.data)
                    if text:
                        blocks.append(text)
            elif child.tag in BLOCK_TAGS:
                text = _block_text(child, for_pre=(child.tag == "pre"))
                if text:
                    blocks.append(text)
                walk(child, False)
            else:
                walk(child, False)

    walk(candidate, True)
    return blocks


def _extract_title(root: _Element) -> str:
    titles: list[_Element] = []
    _collect_elements(root, {"title"}, titles)
    if not titles:
        return ""
    title_elem = titles[0]
    text_parts: list[str] = []

    def walk(node: Node) -> None:
        if isinstance(node, _Text):
            text_parts.append(node.data)
        elif node.tag == "br":
            text_parts.append(" ")
        else:
            for child in node.children:
                walk(child)

    walk(title_elem)
    return re.sub(r"\s+", " ", "".join(text_parts)).strip()


def extract(
    html: str,
    *,
    max_bytes: int = 5_000_000,
    max_depth: int = 512,
) -> Extracted:
    """Extract the main content of ``html``.

    Args:
        html: The HTML document or fragment.
        max_bytes: Maximum size in UTF-8 bytes of ``html``.
        max_depth: Maximum element nesting depth.

    Returns:
        Extracted content with title, text, blocks and removal counts.

    Raises:
        ExtractError: If the input is too large, too deep, or has no content.
    """
    if len(html.encode("utf-8")) > max_bytes:
        raise ExtractError("input_too_large")
    parser = _HTMLParser(max_depth)
    try:
        parser.feed(html)
        parser.close()
    except ExtractError:
        raise
    root = parser.root
    removed: dict[str, int] = {"tags": 0, "hidden": 0, "boilerplate": 0}
    cleaned_root = _prune(root, False, removed)
    if not isinstance(cleaned_root, _Element):
        cleaned_root = _Element(tag="", attrs={}, children=[])

    articles: list[_Element] = []
    _collect_elements(cleaned_root, {"article"}, articles)
    candidate: _Element | None = None
    if len(articles) == 1:
        candidate = articles[0]
    else:
        mains: list[_Element] = []
        _collect_elements(cleaned_root, {"main"}, mains)
        if len(mains) == 1:
            candidate = mains[0]
        else:
            candidates: list[_Element] = []
            _collect_elements(cleaned_root, {"div", "section", "td", "body"}, candidates)
            if not candidates:
                if articles or mains:
                    candidates = articles or mains
                elif any(isinstance(child, _Element) for child in cleaned_root.children):
                    candidates = [cleaned_root]
                else:
                    raise ExtractError("no_content")
            candidate = max(candidates, key=_score)

    if candidate is None:
        raise ExtractError("no_content")
    blocks = _extract_blocks(candidate)
    if not blocks:
        raise ExtractError("no_content")
    title = _extract_title(cleaned_root)
    return Extracted(
        title=title,
        text="\n\n".join(blocks),
        blocks=tuple(blocks),
        removed=removed,
    )
