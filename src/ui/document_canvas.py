"""
Document canvas UI — renders the right-hand panel in workspace mode.
Handles template picker, toolbar, and the Tiptap editor component.
All business logic (AI calls, storage, export) stays in app.py.
"""
import streamlit as st
from src.agent.document_agent import TEMPLATES
from src.ui.tiptap_component import tiptap_editor

# Template definitions with icons and categories for the picker UI
_TEMPLATE_GROUPS = [
    ("📄 Docs", [
        ("prd-1pager",       "PRD (1-pager)",     "One-page product requirements"),
        ("prd-full",         "PRD (Full)",         "Detailed product requirements doc"),
        ("strategy-doc",     "Strategy Doc",       "Strategic context and bets"),
    ]),
    ("📊 Prioritization", [
        ("rice",             "RICE",               "Reach · Impact · Confidence · Effort"),
        ("ice",              "ICE",                "Impact · Confidence · Ease"),
        ("moscow",           "MoSCoW",             "Must / Should / Could / Won't"),
        ("kano",             "Kano Model",         "Delighters vs. must-haves"),
        ("wsjf",             "WSJF",               "Weighted Shortest Job First"),
    ]),
    ("🗺️ Roadmap", [
        ("now-next-later",   "Now / Next / Later", "Horizon-based roadmap"),
        ("outcome-roadmap",  "Outcome-Based",      "Goals → initiatives"),
    ]),
    ("🔍 Discovery", [
        ("jtbd",             "Jobs-to-be-Done",    "Situation · Motivation · Outcome"),
        ("opp-solution-tree","Opportunity Tree",   "Outcomes → opportunities → solutions"),
    ]),
]


def render_template_picker() -> str | None:
    """
    Render a grid of template cards.
    Returns the selected template_id, or None if nothing was clicked.
    """
    st.markdown(
        """
        <div style="padding:0 0 0.5rem;">
          <p style="font-size:0.78rem;font-weight:600;color:#9ca3af;
             text-transform:uppercase;letter-spacing:0.07em;margin:0 0 1rem;">
            Choose a template
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for group_label, items in _TEMPLATE_GROUPS:
        st.markdown(
            f'<p style="font-size:0.75rem;font-weight:600;color:#6b7280;'
            f'text-transform:uppercase;letter-spacing:0.06em;margin:0.75rem 0 0.4rem;">'
            f'{group_label}</p>',
            unsafe_allow_html=True,
        )
        cols = st.columns(len(items) if len(items) <= 3 else 3)
        for i, (tid, label, desc) in enumerate(items):
            with cols[i % 3]:
                if st.button(
                    f"**{label}**\n\n{desc}",
                    key=f"tpl_{tid}",
                    use_container_width=True,
                ):
                    return tid
    return None


def render_canvas_toolbar(document_id: str | None, title: str) -> str | None:
    """
    Render the document title + action toolbar above the editor.
    Returns an action string if a toolbar button was clicked, else None.
    Actions: 'save' | 'export_md' | 'export_excel' | 'versions' | 'close'
    """
    col_title, col_save, col_md, col_xl, col_ver, col_close = st.columns(
        [4, 1.1, 1.1, 1.1, 1.1, 0.6], gap="small"
    )

    with col_title:
        new_title = st.text_input(
            "doc_title",
            value=title,
            label_visibility="collapsed",
            placeholder="Untitled document",
            key="doc_title_input",
        )
        if new_title != title:
            st.session_state.document_title = new_title

    action = None
    with col_save:
        if st.button("💾 Save", use_container_width=True, key="toolbar_save"):
            action = "save"
    with col_md:
        if st.button("⬇️ .md", use_container_width=True, key="toolbar_md"):
            action = "export_md"
    with col_xl:
        if st.button("📊 .xlsx", use_container_width=True, key="toolbar_xl"):
            action = "export_excel"
    with col_ver:
        if document_id and st.button("🕐 Versions", use_container_width=True, key="toolbar_ver"):
            action = "versions"
    with col_close:
        if st.button("✕", use_container_width=True, key="toolbar_close"):
            action = "close"

    return action


def render_canvas(
    content_html: str,
    document_id: str | None,
    title: str,
    height: int = 520,
) -> dict | None:
    """
    Render the full document canvas: toolbar + Tiptap editor.

    Returns a dict from the Tiptap component (user action) or
    a toolbar action dict, or None if nothing happened.
    """
    # Toolbar
    toolbar_action = render_canvas_toolbar(document_id, title)
    if toolbar_action:
        return {"type": "action", "action": toolbar_action,
                "selectedText": "", "fullHtml": content_html}

    # Editor
    result = tiptap_editor(content=content_html, key="tiptap_canvas", height=height)
    return result
