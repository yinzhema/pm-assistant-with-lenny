"""
agent.md section schema — used by both TranslationAgent and IdeaToAgent synthesis.

Confidence levels for PRD → agent.md translation:
  green  = directly derivable from PRD source
  yellow = inferred with low confidence — flagged for PM review
  red    = missing entirely — requires PM input
"""
from dataclasses import dataclass


@dataclass
class AgentMdSection:
    key: str          # stable snake_case identifier
    label: str        # heading in the rendered agent.md
    description: str  # what this section should contain
    required: bool    # whether it must be present for a complete agent.md


AGENT_MD_SECTIONS = [
    AgentMdSection(
        key="purpose",
        label="Purpose",
        description="One-sentence job description for the agent.",
        required=True,
    ),
    AgentMdSection(
        key="users",
        label="Users",
        description="Who uses this agent and what they need from it.",
        required=True,
    ),
    AgentMdSection(
        key="capabilities",
        label="Capabilities",
        description="Bulleted list of specific actions the agent can perform.",
        required=True,
    ),
    AgentMdSection(
        key="tools_integrations",
        label="Tools & Integrations",
        description="Tools and APIs available to the agent, with access level (read/write/admin).",
        required=True,
    ),
    AgentMdSection(
        key="decision_authority",
        label="Decision Authority",
        description="Three subsections: Autonomous (no human needed), Escalate to Human, Never Do.",
        required=True,
    ),
    AgentMdSection(
        key="constraints",
        label="Constraints",
        description="Hard prohibitions — data, actions, and topics that are off-limits.",
        required=True,
    ),
    AgentMdSection(
        key="success_metrics",
        label="Success Metrics",
        description="Measurable indicators of agent quality and performance.",
        required=True,
    ),
    AgentMdSection(
        key="communication_style",
        label="Communication Style",
        description="Tone, verbosity, and format preferences for agent responses.",
        required=False,
    ),
    AgentMdSection(
        key="edge_cases",
        label="Edge Cases & Fallbacks",
        description="Table of difficult scenarios and prescribed agent responses.",
        required=False,
    ),
]

# Section keys in canonical order
SECTION_KEYS = [s.key for s in AGENT_MD_SECTIONS]
REQUIRED_SECTION_KEYS = {s.key for s in AGENT_MD_SECTIONS if s.required}

# Gap categories used in PRD → agent.md translation
GAP_CATEGORIES = [
    "implicit_judgment",      # "Use best judgment" — agent cannot do this
    "missing_escalation",     # What triggers human review is not defined
    "ambiguous_scope",        # Action/request types not specified
    "missing_constraints",    # No "never do" rules defined
    "metric_ambiguity",       # Success metrics not quantified
    "tool_permissions",       # Integrations lack read/write/admin specification
]

# Canonical agent.md output template (HTML with {{section_key}} placeholders)
AGENT_MD_HTML_TEMPLATE = """\
<h1>Agent: {{agent_name}}</h1>

<h2>Purpose</h2>
<p>{{purpose}}</p>

<h2>Users</h2>
<p>{{users}}</p>

<h2>Capabilities</h2>
{{capabilities}}

<h2>Tools &amp; Integrations</h2>
{{tools_integrations}}

<h2>Decision Authority</h2>
<h3>Autonomous (no human needed)</h3>
{{decision_authority_autonomous}}
<h3>Escalate to Human</h3>
{{decision_authority_escalate}}
<h3>Never Do</h3>
{{decision_authority_never}}

<h2>Constraints</h2>
{{constraints}}

<h2>Success Metrics</h2>
{{success_metrics}}

<h2>Communication Style</h2>
<p>{{communication_style}}</p>

<h2>Edge Cases &amp; Fallbacks</h2>
{{edge_cases}}
"""
