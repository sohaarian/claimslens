import streamlit as st
from textwrap import dedent


def render_html(content):
    """
    Render ClaimsLens HTML without Streamlit Markdown interpreting
    indented HTML as code blocks.
    """
    content = dedent(content).strip()

    if hasattr(st, "html"):
        st.html(content)
    else:
        st.markdown(
            content,
            unsafe_allow_html=True,
        )


GLOBAL_CSS = r"""
<style>

:root {
    --cl-bg: #050705;
    --cl-bg2: #080b09;
    --cl-panel: #0b0f0c;
    --cl-panel2: #101510;
    --cl-text: #f3f6f1;
    --cl-muted: #89938a;
    --cl-dim: #59635a;
    --cl-line: rgba(255,255,255,.10);
    --cl-line2: rgba(200,255,50,.22);
    --cl-accent: #c8ff32;
}

/* ==========================================================
   FORCE TRUE DARK CANVAS
   ========================================================== */

html,
body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.stMain,
.main {
    background:
        radial-gradient(
            circle at 76% -10%,
            rgba(200,255,50,.075),
            transparent 27%
        ),
        radial-gradient(
            circle at 15% 25%,
            rgba(60,100,72,.055),
            transparent 22%
        ),
        #050705 !important;
    color: var(--cl-text) !important;
}

[data-testid="stHeader"] {
    background: rgba(5,7,5,.82) !important;
    backdrop-filter: blur(16px);
    border-bottom: 1px solid rgba(255,255,255,.055);
}

.block-container {
    max-width: 1280px !important;
    padding-top: 2rem !important;
    padding-bottom: 7rem !important;
}

/* ==========================================================
   TYPOGRAPHY
   ========================================================== */

html,
body,
p,
label,
button,
input,
textarea,
[class*="css"] {
    font-family:
        "Avenir Next",
        "Helvetica Neue",
        Helvetica,
        Arial,
        sans-serif !important;
}

h1,
h2,
h3 {
    font-family:
        "Avenir Next",
        "Helvetica Neue",
        Helvetica,
        Arial,
        sans-serif !important;

    color: var(--cl-text) !important;
    letter-spacing: -.045em !important;
}

h1 {
    font-size: clamp(3rem, 6vw, 5.6rem) !important;
    line-height: .95 !important;
    font-weight: 700 !important;
}

h2 {
    font-size: 2.2rem !important;
    margin-top: 3.5rem !important;
    font-weight: 650 !important;
}

h3 {
    font-size: 1.35rem !important;
    font-weight: 620 !important;
}

p,
li,
label {
    color: #aeb7af !important;
    line-height: 1.65 !important;
}

code,
kbd,
pre,
[data-testid="stCode"] {
    font-family:
        "SFMono-Regular",
        Menlo,
        Monaco,
        Consolas,
        monospace !important;
}

/* ==========================================================
   SIDEBAR
   ========================================================== */

section[data-testid="stSidebar"] {
    background: #050705 !important;
    border-right: 1px solid var(--cl-line) !important;
}

section[data-testid="stSidebar"] > div {
    padding-top: 1.7rem !important;
}

section[data-testid="stSidebar"] a {
    color: #848e85 !important;
    font-size: .80rem !important;
    letter-spacing: .025em;
}

section[data-testid="stSidebar"] a:hover {
    color: var(--cl-text) !important;
}

section[data-testid="stSidebar"] [aria-current="page"] {
    background: rgba(200,255,50,.07) !important;
    border-left: 1px solid var(--cl-accent);
    color: white !important;
}

/* ==========================================================
   INPUTS
   ========================================================== */

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
div[data-testid="stTextInput"] input,
input {
    background: #090d0a !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,.115) !important;
    border-radius: 2px !important;
}

div[data-baseweb="select"] > div:focus-within,
div[data-testid="stTextInput"] input:focus {
    border-color: rgba(200,255,50,.55) !important;
    box-shadow: 0 0 0 1px rgba(200,255,50,.08) !important;
}

/* ==========================================================
   METRICS
   ========================================================== */

div[data-testid="stMetric"] {
    background: #090d0a !important;
    border-top: 1px solid var(--cl-line) !important;
    border-bottom: 1px solid var(--cl-line) !important;
    padding: 1.35rem 1.1rem !important;
}

div[data-testid="stMetricLabel"] {
    color: #69736a !important;
    text-transform: uppercase;
    letter-spacing: .12em;
    font-size: .63rem !important;
}

div[data-testid="stMetricValue"] {
    color: var(--cl-text) !important;
    letter-spacing: -.045em;
}

/* ==========================================================
   DATAFRAME / EXPANDERS
   ========================================================== */

div[data-testid="stDataFrame"] {
    border: 1px solid var(--cl-line) !important;
    border-radius: 2px !important;
    overflow: hidden;
}

div[data-testid="stExpander"] {
    background: #080c09 !important;
    border: 1px solid rgba(255,255,255,.10) !important;
    border-radius: 2px !important;
    margin-top: 1rem !important;
    margin-bottom: 1.8rem !important;
}

div[data-testid="stExpander"]:hover {
    border-color: rgba(200,255,50,.30) !important;
}

/* ==========================================================
   STREAMLIT INFO/WARNING
   ========================================================== */

div[data-testid="stAlert"] {
    border-radius: 2px !important;
    background: #0a0f0b !important;
    border: 1px solid rgba(255,255,255,.085) !important;
}

/* ==========================================================
   CLAIMSLENS BRAND BAR
   ========================================================== */

.cl-brandbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    min-height: 58px;
    padding: 0 0 1.1rem 0;
    border-bottom: 1px solid var(--cl-line);
    margin-bottom: 2rem;
}

.cl-brand-left {
    display: flex;
    align-items: center;
    gap: .8rem;
}

.cl-brand-name {
    color: white;
    text-transform: uppercase;
    font-size: .71rem;
    font-weight: 700;
    letter-spacing: .20em;
}

.cl-brand-status {
    color: var(--cl-accent);
    text-transform: uppercase;
    letter-spacing: .14em;
    font-size: .60rem;
}

.cl-brand-dot {
    width: 5px;
    height: 5px;
    background: var(--cl-accent);
    border-radius: 50%;
    box-shadow:
        0 0 8px rgba(200,255,50,.8),
        0 0 18px rgba(200,255,50,.25);
}

/* ==========================================================
   ACTUAL CLAIMSLENS LOGO
   ========================================================== */

.cl-logo-small {
    width: 50px;
    height: 50px;
    position: relative;
    perspective: 300px;
}

.cl-logo-small::before,
.cl-logo-small::after {
    content: "";
    position: absolute;
    inset: 6px;
    border: 1px solid var(--cl-accent);
    border-radius: 50%;
}

.cl-logo-small::after {
    inset: 15px;
    background: var(--cl-accent);
    box-shadow: 0 0 14px rgba(200,255,50,.8);
}

.cl-logo-slash {
    position: absolute;
    width: 1px;
    height: 52px;
    background: rgba(255,255,255,.72);
    left: 24px;
    top: -1px;
    transform: rotate(42deg);
}

/* ==========================================================
   HERO
   ========================================================== */

.cl-hero {
    display: grid;
    grid-template-columns: minmax(0,1.25fr) minmax(330px,.75fr);
    gap: 4rem;
    min-height: 485px;
    align-items: center;
    border-bottom: 1px solid var(--cl-line);
    padding: 1.5rem 0 4rem;
    margin-bottom: 3.5rem;
}

.cl-hero-kicker {
    color: var(--cl-accent);
    font-size: .68rem;
    text-transform: uppercase;
    letter-spacing: .22em;
    font-weight: 650;
    margin-bottom: 1.1rem;
}

.cl-hero-title {
    color: white;
    font-size: clamp(3.4rem, 5.5vw, 6.1rem);
    font-weight: 720;
    line-height: .92;
    letter-spacing: -.065em;
    margin: 0;
    white-space: nowrap;
    text-align: center;
}

.cl-hero-title-outline {
    display: none;
}

.cl-hero-copy {
    max-width: 720px;
    font-size: 1.03rem;
    color: #9aa49b;
    margin-top: 1.8rem;
    line-height: 1.72;
}

.cl-hero-rule {
    width: 100%;
    height: 1px;
    background: var(--cl-line);
    margin: 1.7rem 0;
}

.cl-hero-tag {
    display: inline-block;
    font-family:
        "SFMono-Regular",
        Menlo,
        monospace;
    color: #69736a;
    letter-spacing: .10em;
    text-transform: uppercase;
    font-size: .61rem;
}

/* ==========================================================
   3D EVIDENCE LENS
   ========================================================== */

.cl-lens-stage {
    width: 360px;
    height: 360px;
    max-width: 100%;
    margin: auto;
    position: relative;
    perspective: 850px;
    display: flex;
    justify-content: center;
    align-items: center;
}

.cl-lens-glow {
    position: absolute;
    width: 210px;
    height: 210px;
    border-radius: 50%;
    background:
        radial-gradient(
            circle,
            rgba(200,255,50,.15) 0%,
            rgba(200,255,50,.04) 34%,
            transparent 70%
        );
    filter: blur(7px);
    animation: clPulse 3.8s ease-in-out infinite;
}

.cl-ring {
    position: absolute;
    border-radius: 50%;
    border: 1px solid rgba(200,255,50,.45);
    transform-style: preserve-3d;
}

.cl-ring-a {
    width: 235px;
    height: 235px;
    animation: clOrbitA 13s linear infinite;
}

.cl-ring-b {
    width: 185px;
    height: 185px;
    border-color: rgba(255,255,255,.20);
    animation: clOrbitB 9s linear infinite reverse;
}

.cl-ring-c {
    width: 280px;
    height: 105px;
    border-color: rgba(200,255,50,.24);
    animation: clOrbitC 16s linear infinite;
}

.cl-lens-core {
    width: 78px;
    height: 78px;
    border-radius: 50%;
    border: 1px solid var(--cl-accent);
    background:
        radial-gradient(
            circle at 40% 35%,
            rgba(240,255,200,.9),
            var(--cl-accent) 8%,
            rgba(200,255,50,.22) 27%,
            #091009 62%
        );
    box-shadow:
        0 0 16px rgba(200,255,50,.35),
        0 0 54px rgba(200,255,50,.12);
    z-index: 5;
    animation: clCore 4.4s ease-in-out infinite;
}

.cl-lens-core::after {
    content: "CL";
    position: absolute;
    color: white;
    font-size: .72rem;
    font-weight: 700;
    letter-spacing: .11em;
    margin-left: 27px;
    margin-top: 29px;
}

.cl-node {
    position: absolute;
    width: 8px;
    height: 8px;
    background: #0a0f0b;
    border: 1px solid var(--cl-accent);
    border-radius: 50%;
    box-shadow: 0 0 9px rgba(200,255,50,.44);
    z-index: 7;
}

.cl-node-one {
    top: 55px;
    right: 62px;
    animation: clNode1 6s ease-in-out infinite;
}

.cl-node-two {
    bottom: 63px;
    left: 48px;
    animation: clNode2 7.5s ease-in-out infinite;
}

.cl-node-three {
    bottom: 85px;
    right: 39px;
    border-color: #ff715f;
    box-shadow: 0 0 10px rgba(255,113,95,.5);
    animation: clNode3 5s ease-in-out infinite;
}

.cl-node-label {
    position: absolute;
    color: #687169;
    font-family:
        "SFMono-Regular",
        Menlo,
        monospace;
    font-size: .55rem;
    letter-spacing: .08em;
    text-transform: uppercase;
}

.cl-label-a {
    top: 36px;
    right: 5px;
}

.cl-label-b {
    bottom: 39px;
    left: 8px;
}

.cl-label-c {
    bottom: 60px;
    right: -4px;
    color: #a76a61;
}

.cl-scanline {
    position: absolute;
    width: 280px;
    height: 1px;
    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(200,255,50,.60),
            transparent
        );
    animation: clScan 4.5s ease-in-out infinite;
}

@keyframes clOrbitA {
    from {
        transform:
            rotateX(64deg)
            rotateZ(0deg);
    }
    to {
        transform:
            rotateX(64deg)
            rotateZ(360deg);
    }
}

@keyframes clOrbitB {
    from {
        transform:
            rotateY(68deg)
            rotateZ(0deg);
    }
    to {
        transform:
            rotateY(68deg)
            rotateZ(360deg);
    }
}

@keyframes clOrbitC {
    from {
        transform:
            rotateX(73deg)
            rotateY(20deg)
            rotateZ(0deg);
    }
    to {
        transform:
            rotateX(73deg)
            rotateY(20deg)
            rotateZ(360deg);
    }
}

@keyframes clCore {
    0%, 100% {
        transform:
            translateZ(0)
            scale(1);
    }
    50% {
        transform:
            translateZ(35px)
            scale(1.055);
    }
}

@keyframes clPulse {
    0%, 100% {
        opacity: .5;
        transform: scale(.94);
    }
    50% {
        opacity: 1;
        transform: scale(1.08);
    }
}

@keyframes clNode1 {
    0%, 100% {
        transform: translate3d(0,0,0);
    }
    50% {
        transform: translate3d(-16px,11px,30px);
    }
}

@keyframes clNode2 {
    0%, 100% {
        transform: translate3d(0,0,0);
    }
    50% {
        transform: translate3d(19px,-11px,25px);
    }
}

@keyframes clNode3 {
    0%, 100% {
        transform: translate3d(0,0,0);
    }
    50% {
        transform: translate3d(-10px,-16px,32px);
    }
}

@keyframes clScan {
    0%, 100% {
        transform: translateY(-90px);
        opacity: 0;
    }

    20% {
        opacity: .7;
    }

    80% {
        opacity: .7;
    }

    100% {
        transform: translateY(90px);
        opacity: 0;
    }
}

/* ==========================================================
   FIRST-TIME USER GUIDE
   ========================================================== */

.cl-guide {
    border-top: 1px solid var(--cl-line);
    border-bottom: 1px solid var(--cl-line);
    margin: 2rem 0 4rem;
}

.cl-guide-head {
    display: grid;
    grid-template-columns: 1fr 2fr;
    padding: 1.4rem 0;
    border-bottom: 1px solid var(--cl-line);
}

.cl-guide-label {
    color: var(--cl-accent);
    font-size: .64rem;
    text-transform: uppercase;
    letter-spacing: .18em;
    font-weight: 650;
}

.cl-guide-intro {
    color: #c4cbc5;
    max-width: 740px;
    line-height: 1.65;
}

.cl-guide-grid {
    display: grid;
    grid-template-columns: repeat(4,1fr);
}

.cl-guide-step {
    min-height: 180px;
    padding: 1.3rem 1.35rem 1.6rem;
    border-right: 1px solid var(--cl-line);
}

.cl-guide-step:last-child {
    border-right: 0;
}

.cl-guide-number {
    color: #59635a;
    font-family:
        "SFMono-Regular",
        Menlo,
        monospace;
    font-size: .61rem;
    letter-spacing: .12em;
    margin-bottom: 2.6rem;
}

.cl-guide-title {
    color: white;
    font-size: .93rem;
    font-weight: 650;
    margin-bottom: .55rem;
}

.cl-guide-copy {
    color: #7e887f;
    font-size: .78rem;
    line-height: 1.55;
}

/* ==========================================================
   PAGE PURPOSE
   ========================================================== */

.cl-purpose {
    display: grid;
    grid-template-columns: 1fr 2.3fr;
    border-top: 1px solid var(--cl-line);
    border-bottom: 1px solid var(--cl-line);
    padding: 1.4rem 0;
    margin: 1.4rem 0 3rem;
}

.cl-purpose-label {
    color: var(--cl-accent);
    text-transform: uppercase;
    letter-spacing: .17em;
    font-size: .63rem;
}

.cl-purpose-copy {
    color: #abb4ac;
    line-height: 1.65;
}

/* ==========================================================
   CLAIM REVIEW IMPROVEMENTS
   ========================================================== */

hr {
    border: 0 !important;
    border-top: 1px solid var(--cl-line) !important;
    margin: 3.5rem 0 2.6rem !important;
}

[data-testid="stCaptionContainer"] {
    color: #687269 !important;
    line-height: 1.55 !important;
}

.claim-card,
.missing-box {
    background: #090d0a !important;
    border: 1px solid var(--cl-line) !important;
    border-radius: 2px !important;
}

/* ==========================================================
   OLD EYEBROWS
   ========================================================== */

.eyebrow {
    display: none !important;
}

/* ==========================================================
   RESPONSIVE
   ========================================================== */

@media(max-width: 900px) {
    .cl-hero {
        grid-template-columns: 1fr;
    }

    .cl-lens-stage {
        width: 300px;
        height: 300px;
    }

    .cl-guide-grid {
        grid-template-columns: repeat(2,1fr);
    }

    .cl-purpose,
    .cl-guide-head {
        grid-template-columns: 1fr;
        gap: .8rem;
    }
}

@media(max-width: 600px) {
    .cl-guide-grid {
        grid-template-columns: 1fr;
    }

    .cl-guide-step {
        border-right: 0;
        border-bottom: 1px solid var(--cl-line);
    }

    .cl-hero-title,
    .cl-hero-title-outline {
        font-size: 4rem;
    }
}



/* ==========================================================
   FINAL CLAIMSLENS BRAND / HERO COMPOSITION
   ========================================================== */

/* Give the masthead real breathing room below Streamlit chrome */
.block-container {
    padding-top: 4.8rem !important;
    max-width: 1320px !important;
}

/* ----------------------------------------------------------
   Brand masthead
   ---------------------------------------------------------- */

.cl-brandbar {
    min-height: 108px !important;
    padding: 1rem 0 1.65rem 0 !important;
    margin-top: 0 !important;
    margin-bottom: 2.6rem !important;
    overflow: visible !important;
}

.cl-brand-left {
    gap: 1.15rem !important;
}

/* MUCH larger top ClaimsLens logo */
.cl-logo-small {
    width: 82px !important;
    height: 82px !important;
    flex: 0 0 82px !important;
    overflow: visible !important;
}

.cl-logo-small::before {
    inset: 8px !important;
    border-width: 2px !important;
    box-shadow:
        0 0 20px rgba(200,255,50,.18),
        inset 0 0 16px rgba(200,255,50,.08) !important;
}

.cl-logo-small::after {
    inset: 25px !important;
    box-shadow:
        0 0 16px rgba(200,255,50,.95),
        0 0 36px rgba(200,255,50,.28) !important;
}

.cl-logo-slash {
    width: 1px !important;
    height: 86px !important;
    left: 40px !important;
    top: -2px !important;
}

.cl-brand-name {
    font-size: 1.08rem !important;
    letter-spacing: .23em !important;
    font-weight: 720 !important;
}

.cl-brand-status {
    font-size: .64rem !important;
    letter-spacing: .16em !important;
}


/* ----------------------------------------------------------
   Hero composition
   ---------------------------------------------------------- */

.cl-hero {
    grid-template-columns:
        minmax(0, 1.12fr)
        minmax(470px, .88fr) !important;

    gap: 4rem !important;
    min-height: 575px !important;
    align-items: center !important;

    padding-top: .5rem !important;
    padding-bottom: 4rem !important;
}

/* EVERYTHING ON LEFT USES EXACT SAME LEFT EDGE */
.cl-hero > div:first-child {
    text-align: left !important;
    align-self: center !important;
    width: 100% !important;
}

.cl-hero-kicker {
    text-align: left !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
    margin-bottom: 1.25rem !important;

    font-size: .72rem !important;
    letter-spacing: .22em !important;
}

/* The title is ONE DOM element already.
   Force one line + left alignment. */
.cl-hero-title {
    display: block !important;
    width: max-content !important;
    max-width: none !important;

    white-space: nowrap !important;
    text-align: left !important;

    margin: 0 !important;
    padding: 0 !important;

    font-size: clamp(
        3.55rem,
        5.15vw,
        6.15rem
    ) !important;

    line-height: .90 !important;
    letter-spacing: -.068em !important;
    font-weight: 760 !important;

    color: #f7f8f5 !important;
}

.cl-hero-title-outline {
    display: none !important;
}

.cl-hero-rule {
    margin: 2.3rem 0 2rem !important;
    width: 100% !important;
}

.cl-hero-copy {
    margin-left: 0 !important;
    margin-right: 0 !important;
    max-width: 720px !important;

    font-size: 1.04rem !important;
    line-height: 1.72 !important;
    color: #a5aea6 !important;
}

.cl-hero-tag {
    font-size: .61rem !important;
    letter-spacing: .12em !important;
}


/* ----------------------------------------------------------
   Make the evidence-lens visual genuinely substantial
   ---------------------------------------------------------- */

.cl-lens-stage {
    width: 590px !important;
    height: 590px !important;
    max-width: none !important;
    transform: scale(1) !important;
}

.cl-lens-glow {
    width: 390px !important;
    height: 390px !important;
}

.cl-ring-a {
    width: 420px !important;
    height: 420px !important;
}

.cl-ring-b {
    width: 325px !important;
    height: 325px !important;
}

.cl-ring-c {
    width: 500px !important;
    height: 190px !important;
}

.cl-lens-core {
    width: 145px !important;
    height: 145px !important;
}

.cl-lens-core::after {
    margin-left: 54px !important;
    margin-top: 57px !important;
    font-size: .9rem !important;
}

.cl-scanline {
    width: 500px !important;
}


/* ----------------------------------------------------------
   More premium editorial structure
   ---------------------------------------------------------- */

.cl-purpose {
    padding: 2rem 0 !important;
    margin: 3.8rem 0 4.4rem !important;
    grid-template-columns: .85fr 2.15fr !important;
}

.cl-purpose-label {
    font-size: .66rem !important;
    letter-spacing: .20em !important;
}

.cl-purpose-copy {
    font-size: 1rem !important;
    line-height: 1.75 !important;
}

.cl-guide {
    margin-top: 2.8rem !important;
    margin-bottom: 5rem !important;
}

.cl-guide-head {
    padding: 1.8rem 0 !important;
}

.cl-guide-intro {
    font-size: .98rem !important;
    line-height: 1.72 !important;
}

.cl-guide-step {
    min-height: 210px !important;
    padding: 1.5rem 1.5rem 1.9rem !important;
}

.cl-guide-title {
    font-size: .96rem !important;
}

.cl-guide-copy {
    font-size: .80rem !important;
    line-height: 1.62 !important;
}


/* ----------------------------------------------------------
   Investment-grade visual restraint
   ---------------------------------------------------------- */

/* thinner, more architectural lines */
.cl-hero,
.cl-brandbar,
.cl-purpose,
.cl-guide,
hr {
    border-color: rgba(255,255,255,.075) !important;
}

/* restrained data surfaces */
div[data-testid="stMetric"] {
    background:
        linear-gradient(
            180deg,
            rgba(255,255,255,.018),
            rgba(255,255,255,.006)
        ) !important;

    border-color: rgba(255,255,255,.075) !important;
}

/* Stronger section typography */
h2 {
    font-size: 2.35rem !important;
    letter-spacing: -.045em !important;
}

h3 {
    font-size: 1.3rem !important;
}


/* ----------------------------------------------------------
   Responsive — desktop stays ONE LINE
   ---------------------------------------------------------- */

@media (min-width: 851px) {

    .cl-hero-title {
        white-space: nowrap !important;
    }

}

@media (max-width: 1100px) {

    .cl-hero {
        grid-template-columns:
            minmax(0, 1fr)
            minmax(390px, .85fr) !important;
    }

    .cl-hero-title {
        font-size: 4.1rem !important;
    }

    .cl-lens-stage {
        width: 470px !important;
        height: 470px !important;
        transform: scale(.88) !important;
    }

}

@media (max-width: 850px) {

    .cl-hero {
        grid-template-columns: 1fr !important;
    }

    .cl-hero-title {
        font-size: 3.7rem !important;
        white-space: nowrap !important;
    }

    .cl-lens-stage {
        width: 420px !important;
        height: 420px !important;
        margin-left: 0 !important;
    }

}

</style>
"""


BRAND_BAR = """
<div class="cl-brandbar">
    <div class="cl-brand-left">
        <div class="cl-logo-small">
            <div class="cl-logo-slash"></div>
        </div>
        <div class="cl-brand-name">ClaimsLens</div>
    </div>

    <div style="display:flex;align-items:center;gap:.55rem;">
        <div class="cl-brand-dot"></div>
        <div class="cl-brand-status">
            Evidence Assurance Active
        </div>
    </div>
</div>
"""


LENS_VISUAL = """
<div class="cl-lens-stage">
    <div class="cl-lens-glow"></div>

    <div class="cl-ring cl-ring-a"></div>
    <div class="cl-ring cl-ring-b"></div>
    <div class="cl-ring cl-ring-c"></div>

    <div class="cl-scanline"></div>

    <div class="cl-lens-core"></div>

    <div class="cl-node cl-node-one"></div>
    <div class="cl-node cl-node-two"></div>
    <div class="cl-node cl-node-three"></div>

    <div class="cl-node-label cl-label-a">
        source evidence
    </div>

    <div class="cl-node-label cl-label-b">
        authority verified
    </div>

    <div class="cl-node-label cl-label-c">
        gap detected
    </div>
</div>
"""


def install_ui():
    render_html(
        GLOBAL_CSS
    )


def brand_hero(kicker, title, outline, description, tag):
    render_html(
        BRAND_BAR
    )

    full_title = f"{title} {outline}"

    html = f"""
    <section class="cl-hero">
        <div>
            <div class="cl-hero-kicker">
                {kicker}
            </div>

            <div class="cl-hero-title">
                {full_title}
            </div>

            <div class="cl-hero-rule"></div>

            <div class="cl-hero-copy">
                {description}
            </div>

            <div style="margin-top:1.3rem;">
                <span class="cl-hero-tag">
                    {tag}
                </span>
            </div>
        </div>

        {LENS_VISUAL}
    </section>
    """

    render_html(
        html
    )

def page_purpose(label, copy):
    render_html(
        f"""
        <div class="cl-purpose">
            <div class="cl-purpose-label">
                {label}
            </div>
            <div class="cl-purpose-copy">
                {copy}
            </div>
        </div>
        """
    )


def first_time_guide(page):
    if page == "claims":

        intro = (
            "ClaimsLens is a review system. You do not need to understand "
            "the AI before using it. Begin with the worklist, select a claim, "
            "and follow the evidence chain ClaimsLens presents."
        )

        steps = [
            (
                "01",
                "Start with the worklist",
                "Claims needing the most evidence review appear first. "
                "Use the filters when you want to narrow the portfolio."
            ),
            (
                "02",
                "Select a claim",
                "Claim Review converts the portfolio alert into an explanation "
                "of each consequential obligation."
            ),
            (
                "03",
                "Read the evidence chain",
                "Documentary State tells you what the file supports. "
                "Evidence Reviewed shows what ClaimsLens relied on."
            ),
            (
                "04",
                "Resolve the evidence gap",
                "Current Blocker and Missing Proof tell you what prevents a "
                "stronger conclusion and what should be verified next."
            ),
        ]

    elif page == "validation":

        intro = (
            "Use this page when you want to know whether ClaimsLens was tested "
            "rigorously, how the frozen V1 system performed, and where the "
            "research still has limitations."
        )

        steps = [
            (
                "01",
                "Research question",
                "Start here to understand exactly what the experiment is trying "
                "to determine."
            ),
            (
                "02",
                "Locked benchmark",
                "These are the frozen V1 results. They were evaluated separately "
                "from later development experiments."
            ),
            (
                "03",
                "Why abstention matters",
                "This section explains why ClaimsLens sometimes returns "
                "UNVERIFIABLE instead of forcing a conclusion."
            ),
            (
                "04",
                "Failure modes",
                "End here to see where the system still fails and what has not "
                "yet been established."
            ),
        ]

    else:

        intro = (
            "Use this page when you want the technical explanation of how "
            "ClaimsLens works under the hood. It is not required for ordinary "
            "claim review."
        )

        steps = [
            (
                "01",
                "System architecture",
                "Follow the pipeline from longitudinal records through evidence "
                "extraction, authority, timing, dependencies, and state reconstruction."
            ),
            (
                "02",
                "Core capabilities",
                "These are the four system-level capabilities that distinguish "
                "ClaimsLens from a simple document summarizer."
            ),
            (
                "03",
                "AssuranceNet",
                "This is the experimental ML layer used to study robustness, "
                "correctness assurance, and selective prediction."
            ),
            (
                "04",
                "Release gates",
                "The model must pass prespecified safety and robustness criteria "
                "before a new locked evaluation is allowed."
            ),
        ]

    cards = ""

    for number, title, copy in steps:
        cards += f"""
        <div class="cl-guide-step">
            <div class="cl-guide-number">{number}</div>
            <div class="cl-guide-title">{title}</div>
            <div class="cl-guide-copy">{copy}</div>
        </div>
        """

    render_html(
        f"""
        <section class="cl-guide">
            <div class="cl-guide-head">
                <div class="cl-guide-label">
                    First time here
                </div>
                <div class="cl-guide-intro">
                    {intro}
                </div>
            </div>

            <div class="cl-guide-grid">
                {cards}
            </div>
        </section>
        """
    )
