"""
Pre-authored, deterministic question trees for the Interactive Artifact Builder.
Questions are static data — no LLM generates them.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Question:
    id: str                        # stable snake_case key
    text: str                      # displayed to the user
    section_key: str               # which artifact section this populates
    section_label: str             # human-readable section name
    placeholder: str               # greyed preview text when unanswered
    why_it_matters: str            # tooltip / coaching note
    kb_query: Optional[str] = None # if set, surfaces a KB snippet inline
    allow_skip: bool = True


@dataclass
class QuestionTree:
    artifact_type: str             # key used in API / DB
    title: str                     # display name
    description: str               # shown on type-picker
    questions: list = field(default_factory=list)

    def as_dict_list(self):
        return [
            {
                "id": q.id,
                "text": q.text,
                "section_key": q.section_key,
                "section_label": q.section_label,
                "placeholder": q.placeholder,
                "why_it_matters": q.why_it_matters,
                "kb_query": q.kb_query,
                "allow_skip": q.allow_skip,
            }
            for q in self.questions
        ]


# ---------------------------------------------------------------------------
# Play to Win (Roger Martin framework) — 8 questions
# ---------------------------------------------------------------------------
PLAY_TO_WIN = QuestionTree(
    artifact_type="play-to-win",
    title="Play to Win",
    description="Build a product strategy using Roger Martin's Playing to Win framework.",
    questions=[
        Question(
            id="ptw_winning_aspiration",
            text="What does winning look like for this product in 3 years?",
            section_key="winning_aspiration",
            section_label="Winning Aspiration",
            placeholder="Describe what success looks like — the ambition that frames all other choices.",
            why_it_matters="The winning aspiration sets the tone for every choice that follows. It should be aspirational but grounded — not a financial goal, but a statement of where you want to be in the market.",
            kb_query="winning aspiration product strategy Roger Martin playing to win",
        ),
        Question(
            id="ptw_market_definition",
            text="What market are you competing in? (customer segment, geography, channel)",
            section_key="market_definition",
            section_label="Market Definition",
            placeholder="Define the specific arena where you will compete — segment, geography, distribution channel.",
            why_it_matters="'Where to play' is arguably the most important strategic choice. Competing everywhere means winning nowhere. Be specific about the market boundary.",
            kb_query="market definition where to play product strategy segmentation",
        ),
        Question(
            id="ptw_where_to_play",
            text="Within that market, where will you focus? Which segments, use cases, or customer types will you prioritize?",
            section_key="where_to_play",
            section_label="Where to Play",
            placeholder="Name the specific segments, personas, or use cases you will actively pursue — and implicitly deprioritize.",
            why_it_matters="Focus creates leverage. Naming where you won't play is as important as naming where you will. This choice enables the 'how to win' to be specific.",
            kb_query="where to play focus segment prioritization strategy",
        ),
        Question(
            id="ptw_how_to_win",
            text="How will you win there? What unique capabilities, advantages, or positioning let you beat alternatives?",
            section_key="how_to_win",
            section_label="How to Win",
            placeholder="Describe your sustainable advantage — what you can do that competitors cannot easily replicate.",
            why_it_matters="'How to win' must be specific and defensible. Generic answers like 'best product' or 'great UX' aren't strategies. Name the actual mechanism of advantage.",
            kb_query="competitive advantage differentiation how to win moat product strategy",
        ),
        Question(
            id="ptw_must_have_capabilities",
            text="What capabilities must be in place to execute this strategy? What do you need to build, buy, or partner for?",
            section_key="must_have_capabilities",
            section_label="Must-Have Capabilities",
            placeholder="List the internal capabilities — technical, operational, team — required to deliver on Where to Play and How to Win.",
            why_it_matters="Strategy is only as good as its execution. If you can't realistically build the capabilities needed, the strategy is fiction. This section forces a honest capability inventory.",
            kb_query="product capabilities build buy partner execution strategy",
        ),
        Question(
            id="ptw_management_systems",
            text="What metrics and management systems will you use to know the strategy is working?",
            section_key="management_systems",
            section_label="Management Systems",
            placeholder="Name the KPIs, review cadences, and feedback loops that will tell you whether you're winning.",
            why_it_matters="A strategy without measurement is a wish. Management systems create the feedback loop to adapt the strategy as reality unfolds.",
            kb_query="product metrics KPIs OKRs strategy measurement feedback loop",
        ),
        Question(
            id="ptw_moats",
            text="What moats or defensive advantages will protect your position once you've won?",
            section_key="moats",
            section_label="Moats & Defensibility",
            placeholder="Describe what will make it hard for competitors to replicate your position — network effects, data, switching costs, brand, etc.",
            why_it_matters="Winning is only valuable if you can hold the position. Moats turn a win into a durable advantage. Name the specific mechanisms, not generic claims.",
            kb_query="competitive moats defensibility network effects switching costs product strategy",
        ),
        Question(
            id="ptw_biggest_risks",
            text="What are the top 3 assumptions or risks that could invalidate this strategy?",
            section_key="biggest_risks",
            section_label="Key Risks & Assumptions",
            placeholder="Name the 2–3 things that must be true for this strategy to work — and what happens if they're not.",
            why_it_matters="Every strategy rests on assumptions. Making them explicit creates a watchlist — the conditions to monitor and test as you execute.",
            kb_query="strategic risks assumptions product strategy validation",
        ),
    ],
)


# ---------------------------------------------------------------------------
# Opportunity Assessment — 7 questions
# ---------------------------------------------------------------------------
OPPORTUNITY_ASSESSMENT = QuestionTree(
    artifact_type="opportunity-assessment",
    title="Opportunity Assessment",
    description="Evaluate a new opportunity before committing to build — forces problem framing before solution.",
    questions=[
        Question(
            id="oa_problem",
            text="What problem are you solving, and for whom?",
            section_key="problem",
            section_label="Problem Statement",
            placeholder="Name the specific pain, frustration, or unmet need — and who experiences it.",
            why_it_matters="The quality of your solution is bounded by the quality of your problem definition. Vague problems produce mediocre solutions. Be specific about the job-to-be-done.",
            kb_query="problem statement jobs to be done product discovery user pain",
        ),
        Question(
            id="oa_evidence",
            text="What evidence do you have that this problem is real and significant?",
            section_key="evidence",
            section_label="Evidence of Problem",
            placeholder="Cite the data, user research, support tickets, market signals, or qualitative insights that validate this is a real problem worth solving.",
            why_it_matters="Many teams build solutions for problems they assumed exist. Evidence separates conviction from assumption — and determines how much validation work remains.",
            kb_query="user research evidence problem validation customer discovery",
        ),
        Question(
            id="oa_current_solutions",
            text="How do users solve this problem today? What are the gaps in those solutions?",
            section_key="current_solutions",
            section_label="Current Alternatives",
            placeholder="Describe existing workarounds, tools, or behaviors — and where they fall short.",
            why_it_matters="Users always have a current solution, even if it's a spreadsheet or doing nothing. Understanding existing alternatives tells you what 'better' must actually mean.",
            kb_query="competitive alternatives workarounds market gaps user behavior",
        ),
        Question(
            id="oa_market_size",
            text="How large is the addressable opportunity? (TAM/SAM/SOM or rough sizing)",
            section_key="market_size",
            section_label="Market Size",
            placeholder="Estimate the total addressable market, serviceable market, or number of users affected — with your methodology.",
            why_it_matters="Market size frames ROI and strategic priority. It doesn't need to be precise, but it should be defensible. 'Big' is not a market size.",
            kb_query="TAM SAM SOM market sizing opportunity assessment",
        ),
        Question(
            id="oa_strategic_fit",
            text="Why is this the right problem for your product and company to solve?",
            section_key="strategic_fit",
            section_label="Strategic Fit",
            placeholder="Explain why you are uniquely positioned to solve this — given your mission, capabilities, customer base, and current strategy.",
            why_it_matters="Many real problems aren't the right problems for your specific company. Strategic fit prevents opportunity dilution and keeps the team focused.",
            kb_query="strategic fit product strategy company mission capability",
        ),
        Question(
            id="oa_success_metrics",
            text="How will you measure success if you solve this problem?",
            section_key="success_metrics",
            section_label="Success Metrics",
            placeholder="Define 2–3 metrics that would signal you've solved the problem — both leading and lagging indicators.",
            why_it_matters="Metrics defined after building are rationalizations, not measurements. Pre-committing to success criteria makes prioritization and investment decisions much cleaner.",
            kb_query="product metrics success criteria KPIs outcome metrics",
        ),
        Question(
            id="oa_risks",
            text="What are the biggest risks or unknowns?",
            section_key="risks",
            section_label="Key Risks",
            placeholder="Name the top 2–3 things that could derail this opportunity — technical, market, regulatory, competitive, or execution risks.",
            why_it_matters="Surfacing risks early allows you to design discovery and validation work to resolve them. Unknown unknowns are the enemy; acknowledged risks are manageable.",
            kb_query="product risks assumptions unknowns opportunity discovery",
        ),
    ],
)


# ---------------------------------------------------------------------------
# Idea → agent.md — 9 questions (Feature 2A)
# ---------------------------------------------------------------------------
IDEA_TO_AGENT = QuestionTree(
    artifact_type="idea-to-agent",
    title="Idea → agent.md",
    description="Describe your AI agent idea and get a complete agent.md specification ready for engineering.",
    questions=[
        Question(
            id="ia_purpose",
            text="What is this agent's job in one sentence?",
            section_key="purpose",
            section_label="Agent Purpose",
            placeholder="A one-sentence job description — what this agent does and why it exists.",
            why_it_matters="A clear purpose statement is the foundation everything else is derived from. If you can't state the job in one sentence, the scope is probably too broad.",
            kb_query="AI agent purpose job description scope definition",
        ),
        Question(
            id="ia_users",
            text="Who are the users of this agent? What do they need from it?",
            section_key="users",
            section_label="Users",
            placeholder="Describe who interacts with the agent and what they're trying to accomplish.",
            why_it_matters="Agents behave differently depending on user sophistication and expectations. User context drives tone, verbosity, and escalation logic.",
            kb_query="AI agent users personas user needs design",
        ),
        Question(
            id="ia_capabilities",
            text="What can this agent do? List its core actions.",
            section_key="capabilities",
            section_label="Capabilities",
            placeholder="List the specific things this agent can do — actions, queries, transformations, outputs.",
            why_it_matters="Explicit capability lists prevent scope creep and clarify what the agent is (and isn't) responsible for. Each capability implies implementation work.",
            kb_query="AI agent capabilities actions scope",
        ),
        Question(
            id="ia_tools_integrations",
            text="What tools, APIs, or data sources does it have access to?",
            section_key="tools_integrations",
            section_label="Tools & Integrations",
            placeholder="Name the tools and APIs — and what each is used for (read/write/admin access level).",
            why_it_matters="Tool permissions are a security and scope boundary. Agents should have the minimum permissions needed. Vague tool access creates unpredictable behavior.",
            kb_query="AI agent tools APIs integrations permissions access",
        ),
        Question(
            id="ia_decision_authority",
            text="What can it decide autonomously vs. what must it escalate to a human?",
            section_key="decision_authority",
            section_label="Decision Authority",
            placeholder="List decisions the agent can make independently, and situations that require human approval or input.",
            why_it_matters="This is the most critical section. Autonomous agents that escalate too rarely create risk; agents that escalate too often aren't useful. Be explicit about the boundary.",
            kb_query="AI agent autonomy human in the loop escalation decision making",
        ),
        Question(
            id="ia_constraints",
            text="What must this agent never do? List hard constraints.",
            section_key="constraints",
            section_label="Constraints",
            placeholder="List absolute prohibitions — data it cannot access, actions it cannot take, topics it must not engage with.",
            why_it_matters="Unlike humans, agents don't have implicit judgment about what's off-limits. Every hard constraint must be explicit. Missing constraints become failure modes.",
            kb_query="AI agent constraints guardrails safety limitations",
        ),
        Question(
            id="ia_success_metrics",
            text="How will you know if the agent is performing well?",
            section_key="success_metrics",
            section_label="Success Metrics",
            placeholder="Define 2–3 measurable indicators of agent quality — task completion rate, accuracy, escalation rate, user satisfaction.",
            why_it_matters="Agents without explicit success metrics can't be monitored or improved. Measurement is how you know when to adjust behavior.",
            kb_query="AI agent metrics evaluation performance measurement",
        ),
        Question(
            id="ia_tone_style",
            text="What tone and communication style should the agent use?",
            section_key="tone_style",
            section_label="Communication Style",
            placeholder="Describe how the agent should communicate — formal/casual, brief/detailed, proactive/reactive.",
            why_it_matters="Tone directly affects user trust and adoption. Mismatched tone (too casual for enterprise, too formal for consumer) creates friction that undermines even correct outputs.",
            kb_query="AI agent tone communication style UX voice",
        ),
        Question(
            id="ia_edge_cases",
            text="What are the top 3 situations where the agent might get confused, and what should it do?",
            section_key="edge_cases",
            section_label="Edge Cases & Fallbacks",
            placeholder="Describe 2–3 ambiguous or difficult scenarios and the correct behavior for each.",
            why_it_matters="Edge cases reveal the boundaries of the agent's design. Explicitly handling them in the spec prevents silent failures in production.",
            kb_query="AI agent edge cases fallbacks error handling ambiguity",
        ),
    ],
)


# ---------------------------------------------------------------------------
# Outcome-Based Roadmap — 8 questions
# ---------------------------------------------------------------------------
OUTCOME_ROADMAP = QuestionTree(
    artifact_type="outcome-roadmap",
    title="Outcome-Based Roadmap",
    description="Build a product roadmap tied to business outcomes — not features.",
    questions=[
        Question(
            id="or_strategic_goals",
            text="What are the top 2–3 business outcomes this roadmap should drive?",
            section_key="strategic_goals",
            section_label="Strategic Goals",
            placeholder="E.g., increase activation by 20%, reduce churn below 3%, grow enterprise ARR by $2M.",
            why_it_matters="Roadmaps fail when they're feature-focused instead of outcome-focused. Tying every initiative to a business outcome prevents busywork and keeps strategy visible.",
            kb_query="OKRs business outcomes product roadmap strategy",
        ),
        Question(
            id="or_current_state",
            text="What is the current baseline for each outcome? (metrics + trends)",
            section_key="current_state",
            section_label="Current State & Baseline",
            placeholder="Current metric values, recent trends, and gaps vs. target. E.g., activation is 32%, down from 36% last quarter.",
            why_it_matters="You can't track progress without a baseline. Baselines also reveal which outcomes are in worse shape and may need prioritization.",
        ),
        Question(
            id="or_key_assumptions",
            text="What hypotheses link your initiatives to these outcomes?",
            section_key="key_assumptions",
            section_label="Key Assumptions",
            placeholder="E.g., 'If we reduce onboarding friction, activation will rise 20%.' One hypothesis per initiative.",
            why_it_matters="Outcomes roadmaps are built on hypotheses. Naming assumptions makes them testable and reveals what discovery work is needed first.",
            kb_query="product assumptions validation discovery risk",
        ),
        Question(
            id="or_q1_initiatives",
            text="What ships in Q1 and which outcome does each initiative move?",
            section_key="q1_initiatives",
            section_label="Q1 Initiatives",
            placeholder="List initiatives with the specific outcome/metric each is expected to influence.",
            why_it_matters="Each initiative should have a measurable link to an outcome. If an initiative doesn't move a metric, it's probably not worth doing.",
        ),
        Question(
            id="or_q2_initiatives",
            text="What about Q2? Note dependencies on Q1 work.",
            section_key="q2_initiatives",
            section_label="Q2 Initiatives",
            placeholder="List Q2 initiatives + their outcome linkage. Note any sequencing dependencies on Q1.",
            why_it_matters="Roadmaps often fail due to poor sequencing. Q2 initiatives should build on Q1 learnings and may depend on Q1 shipping.",
        ),
        Question(
            id="or_success_criteria",
            text="Leading and lagging metrics to measure success?",
            section_key="success_criteria",
            section_label="Success Criteria",
            placeholder="Define 2–3 metrics per outcome — both leading (effort, adoption) and lagging (revenue, retention).",
            why_it_matters="Without metrics you can't tell if your roadmap is working until it's too late. Leading indicators let you course-correct early.",
        ),
        Question(
            id="or_risks",
            text="What could derail this roadmap? (technical, market, org risks)",
            section_key="risks",
            section_label="Risks & Blockers",
            placeholder="Name the top 3 risks and mitigation plans.",
            why_it_matters="Known risks can be managed; unknown ones create surprises. Explicit risk planning increases execution odds.",
        ),
        Question(
            id="or_tradeoffs",
            text="What are you NOT doing and why?",
            section_key="tradeoffs",
            section_label="Tradeoffs & Deprioritized Work",
            placeholder="List deprioritized initiatives and explain why the current outcomes take precedence.",
            why_it_matters="Saying yes to everything means no to focus. Explicitly deprioritizing work keeps the team aligned on what matters most.",
        ),
    ],
)


# ---------------------------------------------------------------------------
# RICE Prioritization — 7 questions
# ---------------------------------------------------------------------------
RICE_PRIORITIZATION = QuestionTree(
    artifact_type="rice-prioritization",
    title="RICE Prioritization",
    description="Score and rank initiatives using Reach, Impact, Confidence, and Effort.",
    questions=[
        Question(
            id="rice_problem",
            text="What problem are you prioritizing solutions for?",
            section_key="problem_statement",
            section_label="Problem Statement",
            placeholder="Describe the problem or opportunity — what are you comparing initiatives against?",
            why_it_matters="RICE is a decision tool — it only works if you're comparing apples to apples. Be clear about the scope before scoring.",
            kb_query="RICE prioritization framework product management",
        ),
        Question(
            id="rice_initiatives",
            text="List all initiatives you're considering (one per line).",
            section_key="initiatives_list",
            section_label="Initiatives",
            placeholder="E.g., Redesign onboarding\nAdd dark mode\nImprove search\nMobile app\nAPI v2",
            why_it_matters="You can only compare initiatives you've articulated. If you're missing ideas, the ranking will be incomplete.",
        ),
        Question(
            id="rice_reach",
            text="How do you define Reach? (unit + timeframe, e.g. users affected per quarter)",
            section_key="reach_definition",
            section_label="Reach Definition",
            placeholder="Define the unit: number of users, % of cohort, revenue impact, etc. Be consistent across all initiatives.",
            why_it_matters="Reach calibration determines how heavily market size factors into scoring. Misaligned definitions create unfair comparisons.",
        ),
        Question(
            id="rice_impact",
            text="How do you define Impact? (metric + multipliers: 3x massive, 2x high, 1x medium, 0.5x low)",
            section_key="impact_definition",
            section_label="Impact Definition",
            placeholder="Define what 'success' looks like per initiative — 3x, 2x, 1x, 0.5x multiplier scale or a specific metric.",
            why_it_matters="Impact is subjective. Pre-defining the metric prevents after-the-fact scoring bias.",
        ),
        Question(
            id="rice_effort",
            text="How do you measure Effort? (eng-weeks or 1–10 scale)",
            section_key="effort_definition",
            section_label="Effort Definition",
            placeholder="Define units: engineer-weeks, design days, or a 1–10 scale. Be consistent. Ask engineers for estimates.",
            why_it_matters="Effort is the divisor — bad estimates will skew the entire ranking. Ask engineers for realistic numbers.",
        ),
        Question(
            id="rice_scores",
            text="Score each initiative: Reach, Impact (3x/2x/1x/0.5x), Confidence (0–100%), Effort. Show your math.",
            section_key="scores",
            section_label="RICE Scores",
            placeholder="Initiative | Reach | Impact | Confidence | Effort | Score\nOnboarding redesign | 500 | 2x | 80% | 3 weeks | 267",
            why_it_matters="Transparency in scoring prevents arguments later — everyone can see the math. RICE = (Reach × Impact × Confidence) / Effort.",
        ),
        Question(
            id="rice_caveats",
            text="What does RICE miss? Strategic overrides to the ranking?",
            section_key="caveats",
            section_label="Caveats & Strategic Overrides",
            placeholder="Strategic bets, tech debt, team growth, regulatory requirements, or factors the formula can't capture.",
            why_it_matters="RICE is a tool, not destiny. Real prioritization factors in strategy and execution risk that a formula can't capture.",
            kb_query="RICE prioritization limitations strategy override",
        ),
    ],
)


# ---------------------------------------------------------------------------
# PRD (Product Requirements Doc) — 10 questions
# ---------------------------------------------------------------------------
PRD = QuestionTree(
    artifact_type="prd",
    title="PRD",
    description="Create a complete product requirements document — what you're building, why, and how to measure success.",
    questions=[
        Question(
            id="prd_objective",
            text="One-line objective for this initiative?",
            section_key="objective",
            section_label="Objective",
            placeholder="E.g., 'Enable users to export results as CSV', 'Reduce account creation friction by 40%'.",
            why_it_matters="Everything that follows flows from the objective. If the objective isn't clear, the PRD will be a mess.",
            kb_query="product objective problem statement PRD",
        ),
        Question(
            id="prd_success_metrics",
            text="How will you measure success? (3–4 key metrics)",
            section_key="success_metrics",
            section_label="Success Metrics",
            placeholder="E.g., '25% adoption in 90 days', '10% reduction in support tickets', 'NPS +5 points'.",
            why_it_matters="Metrics defined after shipping are excuses. Pre-committing forces rigor and makes retrospectives honest.",
            kb_query="success metrics KPIs product measurement OKRs",
        ),
        Question(
            id="prd_background",
            text="Why are we building this now? (market context, data, strategic fit)",
            section_key="background",
            section_label="Background & Context",
            placeholder="Cite customer interviews, analytics trends, competitive moves, or strategic priorities that justify this now.",
            why_it_matters="Context prevents feature creep. When engineers understand why, they make better trade-offs without asking.",
        ),
        Question(
            id="prd_target_users",
            text="Who is this for? Define the primary user persona.",
            section_key="target_users",
            section_label="Target Users",
            placeholder="Describe the user's role, goals, skill level, and day-to-day workflow relevant to this feature.",
            why_it_matters="Features designed for everyone satisfy no one. Explicit persona focus guides design trade-offs.",
            kb_query="user personas target audience product design",
        ),
        Question(
            id="prd_requirements",
            text="What must this feature do? (must-have functionality, user stories)",
            section_key="requirements",
            section_label="Requirements",
            placeholder="List the core user stories or functional requirements. What are the non-negotiable behaviors?",
            why_it_matters="Must-haves vs. nice-to-haves clarify scope. Scope creep kills shipping speed.",
        ),
        Question(
            id="prd_out_of_scope",
            text="What are you explicitly NOT building in this version?",
            section_key="out_of_scope",
            section_label="Out of Scope",
            placeholder="List features or use cases you're deferring or won't do, with a brief rationale for each.",
            why_it_matters="Out-of-scope prevents scope creep and manages stakeholder expectations proactively.",
        ),
        Question(
            id="prd_design",
            text="High-level UX intent or flow? (not detailed wireframes)",
            section_key="design_approach",
            section_label="Design Approach",
            placeholder="Sketch the general flow, key screens, or interaction model. Link to design file if available.",
            why_it_matters="Design direction up-front prevents rework. High-level intent gives designers room to iterate without going in the wrong direction.",
        ),
        Question(
            id="prd_technical",
            text="Technical constraints, architecture notes, or eng dependencies?",
            section_key="technical_considerations",
            section_label="Technical Considerations",
            placeholder="Performance targets, data model changes, API contract shifts, infrastructure implications, or known blockers.",
            why_it_matters="Early technical input prevents down-the-line surprises. Engineers should flag blockers early, not during implementation.",
        ),
        Question(
            id="prd_timeline",
            text="When should this ship? Any phased rollout strategy?",
            section_key="timeline",
            section_label="Timeline",
            placeholder="E.g., 'MVP in 6 weeks, full feature by Q3', or 'Beta with select customers first'.",
            why_it_matters="Timeline clarity sets expectations and influences scope decisions. A hard deadline changes what goes in v1.",
        ),
        Question(
            id="prd_risks",
            text="What could go wrong? (technical, adoption, market risks)",
            section_key="risks",
            section_label="Risks",
            placeholder="Name the top 2–3 risks and mitigation plans.",
            why_it_matters="Risk-aware shipping beats surprised launches. Naming risks is the first step to managing them.",
            kb_query="product risks assumptions validation testing",
        ),
    ],
)


# ---------------------------------------------------------------------------
# MRD (Market Requirements Doc) — 8 questions
# ---------------------------------------------------------------------------
MRD = QuestionTree(
    artifact_type="mrd",
    title="MRD",
    description="Define the market problem, competitive landscape, positioning, and go-to-market strategy.",
    questions=[
        Question(
            id="mrd_market_problem",
            text="What market problem does this product solve?",
            section_key="market_problem",
            section_label="Market Problem",
            placeholder="Describe the pain point, friction, or unmet need that affects a large addressable market.",
            why_it_matters="MRD starts with market, not product. If the market problem isn't clear and compelling, the rest doesn't matter.",
            kb_query="market problem TAM addressable market discovery",
        ),
        Question(
            id="mrd_tam",
            text="TAM / SAM / SOM — how large is the opportunity?",
            section_key="tam_sam_som",
            section_label="Market Size (TAM / SAM / SOM)",
            placeholder="TAM: all users globally. SAM: reachable by your model. SOM: realistic target in Y1–Y3. Show your methodology.",
            why_it_matters="Market size frames investment and growth expectations. Be defensible in your sizing — 'big' is not a market size.",
            kb_query="TAM SAM SOM market sizing opportunity assessment",
        ),
        Question(
            id="mrd_segment",
            text="Which segment are you targeting first and why?",
            section_key="target_segment",
            section_label="Target Segment",
            placeholder="E.g., 'SMB e-commerce teams', 'Enterprise SaaS companies over 500 employees', 'B2C fitness apps'.",
            why_it_matters="You can't target the entire market. Picking a segment focuses GTM, pricing, and product design.",
            kb_query="market segmentation customer targeting go-to-market strategy",
        ),
        Question(
            id="mrd_competition",
            text="Direct and indirect competitors — strengths and weaknesses?",
            section_key="competitive_landscape",
            section_label="Competitive Landscape",
            placeholder="Map 3–5 key competitors and your position vs. them. Include free, DIY, and do-nothing alternatives.",
            why_it_matters="Understanding the competitive landscape reveals positioning opportunities and pricing ceilings.",
            kb_query="competitive analysis competitive advantage differentiation",
        ),
        Question(
            id="mrd_positioning",
            text="How will you position against alternatives? What's your differentiation?",
            section_key="positioning",
            section_label="Positioning",
            placeholder="E.g., 'Easiest to use for non-technical teams', 'Most affordable enterprise-grade solution', 'Purpose-built for X industry'.",
            why_it_matters="Positioning drives messaging, pricing, and product prioritization. Vague positioning creates weak GTM.",
            kb_query="product positioning messaging differentiation brand",
        ),
        Question(
            id="mrd_pricing",
            text="Pricing model and rationale? (SaaS, freemium, marketplace, one-time, etc.)",
            section_key="pricing_model",
            section_label="Pricing Model",
            placeholder="Model, initial pricing tiers, and methodology (value-based, cost-plus, competitive).",
            why_it_matters="Pricing is a strategic lever. Early clarity prevents pricing mistakes that are hard to undo later.",
            kb_query="pricing strategy SaaS pricing model monetization",
        ),
        Question(
            id="mrd_gtm",
            text="How will you acquire customers? (sales motion, channels, launch)",
            section_key="go_to_market",
            section_label="Go-to-Market Strategy",
            placeholder="Sales model (direct, self-serve, channel), marketing channels, launch strategy, partnership opportunities.",
            why_it_matters="GTM must match your market and customer type. Misaligned GTM kills early traction even with a great product.",
            kb_query="go-to-market strategy customer acquisition channels product launch",
        ),
        Question(
            id="mrd_metrics",
            text="Market success metrics: CAC, LTV, adoption, churn, NPS, market share.",
            section_key="metrics",
            section_label="Market Success Metrics",
            placeholder="Define the metrics that signal whether you're winning in this market — and your targets for each.",
            why_it_matters="Market metrics are different from product metrics. They measure GTM effectiveness and product-market fit.",
        ),
    ],
)


# ---------------------------------------------------------------------------
# Jobs-to-be-Done — 6 questions
# ---------------------------------------------------------------------------
JOBS_TO_BE_DONE = QuestionTree(
    artifact_type="jobs-to-be-done",
    title="Jobs-to-be-Done",
    description="Understand the underlying job your customer is hiring your product to accomplish.",
    questions=[
        Question(
            id="jtbd_the_job",
            text="What job is the customer trying to accomplish? (one sentence)",
            section_key="the_job",
            section_label="The Job",
            placeholder="E.g., 'Manage a team's project schedule without losing context', 'Reduce anxiety about retirement planning'.",
            why_it_matters="Jobs thinking shifts you from feature list to customer outcome. It prevents building cool things no one wants.",
            kb_query="jobs to be done Clayton Christensen customer motivation",
        ),
        Question(
            id="jtbd_dimensions",
            text="Functional, emotional, and social dimensions of this job?",
            section_key="functional_emotional_social",
            section_label="Job Dimensions",
            placeholder="Functional: what do they need to accomplish? Emotional: how should they feel? Social: how do they want to be perceived?",
            why_it_matters="Most products fail because they solve the functional job but miss the emotional or social dimensions that drive purchasing decisions.",
            kb_query="functional job emotional job social job JTBD dimensions",
        ),
        Question(
            id="jtbd_circumstances",
            text="What triggers the need? When and where does the job occur?",
            section_key="circumstances",
            section_label="Circumstances & Triggers",
            placeholder="Context, triggers, frequency, urgency. E.g., 'When a deadline is 2 weeks away and the team is behind'.",
            why_it_matters="Jobs vary by context. Understanding when the job becomes urgent informs product timing, notifications, and onboarding.",
        ),
        Question(
            id="jtbd_current_solution",
            text="How do customers get this done today? (tools, workarounds, processes)",
            section_key="current_solution",
            section_label="Current Solution",
            placeholder="Describe the existing solution in detail — all steps, tools, and pain points. Don't skip the boring parts.",
            why_it_matters="You can't displace an existing solution unless you understand what it does well AND what it's missing.",
            kb_query="customer workarounds existing solutions competitive alternatives JTBD",
        ),
        Question(
            id="jtbd_struggles",
            text="Key struggles with current solutions? What gets abandoned or done poorly?",
            section_key="struggles",
            section_label="Struggles",
            placeholder="List 3–5 specific struggles. E.g., 'Takes 30 minutes to set up', 'Team gets out of sync', 'Only works on desktop'.",
            why_it_matters="Struggles reveal opportunity. But don't assume — verify with customers that these are real pain points.",
            kb_query="customer struggles pain points job discovery research",
        ),
        Question(
            id="jtbd_desired_outcome",
            text="What would an ideal solution look like? What outcomes matter most?",
            section_key="desired_outcome",
            section_label="Desired Outcome",
            placeholder="Describe what 'done' looks like — speed, ease, emotional payoff, social proof, cost savings, etc.",
            why_it_matters="Your product's value proposition should articulate the desired outcome better than anything else in the market.",
            kb_query="customer outcomes value proposition product positioning JTBD",
        ),
    ],
)


# ---------------------------------------------------------------------------
# Registry — keyed by artifact_type
# ---------------------------------------------------------------------------
QUESTION_TREES: dict[str, QuestionTree] = {
    "play-to-win": PLAY_TO_WIN,
    "opportunity-assessment": OPPORTUNITY_ASSESSMENT,
    "idea-to-agent": IDEA_TO_AGENT,
    "outcome-roadmap": OUTCOME_ROADMAP,
    "rice-prioritization": RICE_PRIORITIZATION,
    "prd": PRD,
    "mrd": MRD,
    "jobs-to-be-done": JOBS_TO_BE_DONE,
}

ARTIFACT_TYPES = [
    {
        "id": "play-to-win",
        "title": "Play to Win",
        "description": "Product strategy framework — define winning aspiration, where to play, and how to win.",
        "icon": "trophy",
        "question_count": len(PLAY_TO_WIN.questions),
    },
    {
        "id": "opportunity-assessment",
        "title": "Opportunity Assessment",
        "description": "Evaluate a new opportunity before committing to build.",
        "icon": "search",
        "question_count": len(OPPORTUNITY_ASSESSMENT.questions),
    },
    {
        "id": "idea-to-agent",
        "title": "Idea → agent.md",
        "description": "Turn your AI agent idea into a complete spec for engineering.",
        "icon": "bot",
        "question_count": len(IDEA_TO_AGENT.questions),
    },
    {
        "id": "outcome-roadmap",
        "title": "Outcome-Based Roadmap",
        "description": "Build a product roadmap tied to business outcomes, not features.",
        "icon": "map",
        "question_count": len(OUTCOME_ROADMAP.questions),
    },
    {
        "id": "rice-prioritization",
        "title": "RICE Prioritization",
        "description": "Score and rank initiatives using Reach, Impact, Confidence, and Effort.",
        "icon": "bar-chart-2",
        "question_count": len(RICE_PRIORITIZATION.questions),
    },
    {
        "id": "prd",
        "title": "PRD",
        "description": "Create a complete product requirements document — what you're building and why.",
        "icon": "file-text",
        "question_count": len(PRD.questions),
    },
    {
        "id": "mrd",
        "title": "MRD",
        "description": "Define the market problem, competitive landscape, and go-to-market strategy.",
        "icon": "globe",
        "question_count": len(MRD.questions),
    },
    {
        "id": "jobs-to-be-done",
        "title": "Jobs-to-be-Done",
        "description": "Understand the underlying job your customer is hiring your product to accomplish.",
        "icon": "briefcase",
        "question_count": len(JOBS_TO_BE_DONE.questions),
    },
]
