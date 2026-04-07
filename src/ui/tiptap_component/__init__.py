"""
Streamlit component wrapper for the Tiptap rich-text editor.

Usage:
    from src.ui.tiptap_component import tiptap_editor

    result = tiptap_editor(content="<p>Hello</p>", key="canvas", height=520)
    if result:
        # result = {"type": "action", "action": "save"|"improve"|...,
        #           "selectedText": "...", "fullHtml": "...", "timestamp": ...}
        handle_action(result)
"""
import os
import streamlit.components.v1 as components

_COMPONENT_DIR = os.path.dirname(os.path.abspath(__file__))

_tiptap_editor = components.declare_component(
    "tiptap_editor",
    path=_COMPONENT_DIR,
)


def tiptap_editor(
    content: str = "",
    key: str = None,
    height: int = 520,
    readonly: bool = False,
) -> dict | None:
    """
    Render the Tiptap editor.

    Args:
        content:  HTML string to populate the editor with.
        key:      Streamlit component key (must be stable to avoid re-mounts).
        height:   Editor iframe height in pixels.
        readonly: Render editor in read-only mode.

    Returns:
        A dict describing the user action, or None if nothing has happened yet.
        Schema: {"type": "action", "action": str, "selectedText": str,
                 "fullHtml": str, "timestamp": int}
    """
    return _tiptap_editor(
        content=content,
        height=height,
        readonly=readonly,
        key=key,
        default=None,
    )
