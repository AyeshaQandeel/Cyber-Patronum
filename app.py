

# import base64
# import glob
# import html
# import os

# import streamlit as st
# from agent_core import CyberPatronumAgent

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# def find_harry_image():
#     """Look for the Harry image next to app.py using several common names."""
#     for name in ["harry.png", "harry.PNG", "harry.png.png", "harry.jpg", "harry.jpeg", "image.png"]:
#         p = os.path.join(BASE_DIR, name)
#         if os.path.exists(p):
#             return p
#     matches = glob.glob(os.path.join(BASE_DIR, "*harry*.*"))
#     return matches[0] if matches else None


# def get_base64_image(path):
#     """Return the file as a base64 string (empty string if not found)."""
#     if path:
#         with open(path, "rb") as f:
#             return base64.b64encode(f.read()).decode()
#     return ""


# harry_path = find_harry_image()
# harry_b64 = get_base64_image(harry_path)
# harry_mime = "image/jpeg" if harry_path and harry_path.lower().endswith((".jpg", ".jpeg")) else "image/png"

# # Pixel cloud strip used as the sky at the top of the page
# @st.cache_data
# def build_clouds_b64(path):
#     """Load clouds.png and fade its bottom edge to transparent so it blends into the page."""
#     try:
#         from PIL import Image
#         import io
#         img = Image.open(path).convert("RGBA")
#         w, h = img.size
#         fade_start = int(h * 0.55)
#         alpha = Image.new("L", (1, h), 255)
#         for y in range(h):
#             if y > fade_start:
#                 alpha.putpixel((0, y), max(0, int(255 * (1 - (y - fade_start) / (h - fade_start)))))
#         img.putalpha(alpha.resize((w, h)))
#         buf = io.BytesIO()
#         img.save(buf, "PNG")
#         return base64.b64encode(buf.getvalue()).decode()
#     except Exception:
#         return get_base64_image(path)


# clouds_path = os.path.join(BASE_DIR, "clouds.png")
# clouds_b64 = build_clouds_b64(clouds_path) if os.path.exists(clouds_path) else ""

# # Set Page Config
# st.set_page_config(
#     page_title="Cyber-Patronum // Magical Threat Intelligence", 
#     page_icon="⚡", 
#     layout="wide",
#     initial_sidebar_state="collapsed"
# )

# # Custom Pixel Art Harry Potter Sky Aesthetic CSS
# st.markdown("""
#     <style>
#     /* Hide Default Streamlit Elements */
#     #MainMenu {visibility: hidden;}
#     footer {visibility: hidden;}
#     [data-testid="stSidebar"] {display: none;}
    
#     @keyframes floatHarry {
#         0% { transform: translateY(0px) rotate(0deg); }
#         50% { transform: translateY(-6px) rotate(-1deg); }
#         100% { transform: translateY(0px) rotate(0deg); }
#     }

#     /* Magical Pixel Sky Background */
#     .stApp {
#         background: linear-gradient(180deg, #bae6fd 0%, #e0f2fe 40%, #f0fdf4 100%);
#         font-family: 'Courier New', Courier, monospace;
#         color: #4a0404;
#     }

#     /* Top Retro Navigation Bar (No Line) */
#     .hp-nav {
#         display: flex;
#         justify-content: space-between;
#         align-items: center;
#         padding: 10px 20px;
#         font-weight: bold;
#         color: #5b1a18;
#         font-size: 0.95rem;
#         letter-spacing: 2px;
#         margin-bottom: 20px;
#         border-bottom: none !important;
#     }
#     .hp-nav-links span {
#         margin-right: 25px;
#         cursor: pointer;
#     }
#     .hp-nav-links span:hover {
#         color: #b45309;
#     }
#     .hp-hearts {
#         color: #dc2626;
#         font-size: 1.2rem;
#         letter-spacing: 4px;
#     }

#     /* Pixel Art Title Styling */
#     .hp-title-container {
#         display: flex;
#         justify-content: space-between;
#         align-items: center;
#         margin-bottom: 15px;
#     }
#     .hp-main-title {
#         color: #5b1a18;
#         font-size: 3rem;
#         font-weight: 900;
#         letter-spacing: 4px;
#         line-height: 1.1;
#         text-shadow: 2px 2px 0px #fde047;
#     }

#     /* Floating Harry Potter Pixel Image Container */
#     .floating-harry-container {
#         animation: floatHarry 4s ease-in-out infinite;
#         filter: drop-shadow(4px 4px 0px rgba(91, 26, 24, 0.2));
#     }
#     .floating-harry-container img {
#         image-rendering: pixelated;
#         display: block;
#         width: 240px;
#         max-width: 100%;
#     }

#     /* Wizard Banner Box (Still) */
#     .hp-wizard-banner {
#         background: rgba(255, 255, 255, 0.95);
#         border: 3px solid #5b1a18;
#         box-shadow: 6px 6px 0px #5b1a18;
#         border-radius: 4px;
#         padding: 16px 20px;
#         margin-bottom: 25px;
#         display: flex;
#         align-items: center;
#         gap: 20px;
#     }

#     /* Retro Pixel Input Box (Blank by default) */
#     .stTextInput input {
#         background-color: #ffffff !important;
#         color: #4a0404 !important;
#         border: 3px solid #5b1a18 !important;
#         font-family: 'Courier New', Courier, monospace !important;
#         border-radius: 0px !important;
#         padding: 12px !important;
#         font-size: 1.1rem !important;
#         font-weight: bold !important;
#         box-shadow: 4px 4px 0px #5b1a18 !important;
#     }
#     .stTextInput label {
#         color: #5b1a18 !important;
#         font-family: 'Courier New', Courier, monospace !important;
#         font-size: 1.1rem !important;
#         font-weight: bold !important;
#     }

#     /* Retro Pixel Game Button ("START THE GAME") */
#     .stButton > button {
#         background-color: #5b1a18 !important;
#         color: #fde047 !important;
#         border: 3px solid #5b1a18 !important;
#         border-radius: 0px !important;
#         font-family: 'Courier New', Courier, monospace !important;
#         font-weight: 900 !important;
#         font-size: 1.1rem !important;
#         padding: 12px 28px !important;
#         width: 100%;
#         box-shadow: 4px 4px 0px #fde047 !important;
#         transition: all 0.1s ease-in-out !important;
#     }
#     .stButton > button:hover {
#         background-color: #7f1d1d !important;
#         transform: translate(-2px, -2px);
#         box-shadow: 6px 6px 0px #fde047 !important;
#     }

#     /* Retro Sharp Square Parchment Boxes for Results */
#     .hp-parchment-box {
#         background-color: #fffbeb;
#         border: 3px solid #5b1a18;
#         border-radius: 0px;
#         padding: 20px;
#         color: #450a0a;
#         font-family: 'Courier New', Courier, monospace;
#         box-shadow: 5px 5px 0px #5b1a18;
#         margin-top: 10px;
#         margin-bottom: 15px;
#         line-height: 1.6;
#         font-weight: bold;
#     }

#     /* Metric Display Overrides */
#     div[data-testid="stMetricValue"] {
#         color: #5b1a18 !important;
#         font-family: 'Courier New', Courier, monospace !important;
#         font-size: 2.5rem !important;
#         font-weight: 900 !important;
#     }
#     div[data-testid="stMetricLabel"] {
#         color: #b45309 !important;
#         font-family: 'Courier New', Courier, monospace !important;
#         font-weight: bold !important;
#     }
#     </style>
# """, unsafe_allow_html=True)

# # Pixel clouds across the upper part of the page (layered over the sky gradient)
# if clouds_b64:
#     st.markdown(f"""
#         <style>
#         .stApp {{
#             background:
#                 url("data:image/png;base64,{clouds_b64}") center top / 100% auto no-repeat,
#                 linear-gradient(180deg, #bae6fd 0%, #e0f2fe 40%, #f0fdf4 100%) !important;
#             image-rendering: pixelated;
#         }}
#         </style>
#     """, unsafe_allow_html=True)
# else:
#     st.warning(f"clouds.png not found. Put it in this folder: {BASE_DIR}")

# # Top Retro Game Navigation Bar (No bottom line)
# st.markdown("""
#     <div class="hp-nav">
#         <div class="hp-hearts" style="margin-left: auto;">[♥ ♥ ♥]</div>
#     </div>
# """, unsafe_allow_html=True)

# # Header Section with Floating Pixel Harry Potter
# st.markdown(f"""
#     <div class="hp-title-container">
#         <div>
#             <div class="hp-main-title">CYBER-PATRONUM</div>
#             <div style="color: #b45309; font-weight: bold; font-size: 1.05rem; letter-spacing: 1px;">
#                 [ HOGWARTS MAGICAL THREAT INTELLIGENCE & INVESTIGATION AGENT ]
#             </div>
#         </div>
#         <div class="floating-harry-container">
#             <img src="data:{harry_mime};base64,{harry_b64}" alt="Harry Potter on broomstick" />
#         </div>
#     </div>
# """, unsafe_allow_html=True)

# if not harry_b64:
#     st.warning(f"harry.png not found. Put it in this folder: {BASE_DIR}")

# # Wizard Banner Card (Still)
# st.markdown("""
#     <div class="hp-wizard-banner">
#         <div style="font-size: 2rem;">⚡</div>
#         <div>
#             <div style="color: #5b1a18; font-weight: 900; font-size: 1.1rem; letter-spacing: 1px;">SPELLCASTER ASSISTANT ONLINE</div>
#             <div style="color: #78350f; font-size: 0.95rem; font-weight: bold; margin-top: 2px;">
#                 "Expecto Patronum! Enter any target domain or IP below to cast investigation spells and ward off dark anomalies."
#             </div>
#         </div>
#     </div>
# """, unsafe_allow_html=True)

# # Input Controls (Blank default value for universal website testing)
# col_input, col_btn = st.columns([3, 1])

# with col_input:
#     target_input = st.text_input(
#         "CAST SPELL // TARGET INPUT",
#         value="",
#         placeholder="e.g. google.com, github.com, 185.220.101.5"
#     )

# with col_btn:
#     st.write(" ")
#     st.write(" ")
#     run_scan = st.button("START THE SCAN")

# # Scan Execution & Retro Report Results
# if run_scan:
#     if not target_input.strip():
#         st.markdown("""
#             <div class="hp-parchment-box" style="border-color: #dc2626; color: #dc2626;">
#                 SPELL FAILED: Please enter a valid target domain or IP address to investigate.
#             </div>
#         """, unsafe_allow_html=True)
#     else:
#         with st.spinner("Casting OSINT spells across DNS, registry, certificate and reputation nodes..."):
#             agent = CyberPatronumAgent(target_input)
#             raw_data = agent.fetch_live_dns_ip_data()
#             flags = agent.run_heuristic_checks(raw_data)
#             report = agent.generate_explanation(raw_data, flags)

#         st.markdown("---")
#         st.markdown(f"""
#             <div style="color: #5b1a18; font-weight: 900; font-size: 1.3rem; margin-bottom: 10px; letter-spacing: 1px;">
#                 [ INVESTIGATION REPORT: {html.escape(str(report['target']))} ]
#             </div>
#         """, unsafe_allow_html=True)

#         r_col1, r_col2 = st.columns([1, 2])

#         # ---- LEFT: score, verdict, and only the telemetry we actually have ----
#         with r_col1:
#             st.metric(
#                 label="DARK ARTS RISK SCORE",
#                 value=f"{report['risk_score']}%",
#                 delta=report['confidence'] + " Confidence",
#                 delta_color="off",
#             )
#             st.markdown(f"""
#                 <div class="hp-parchment-box" style="padding: 10px 14px; margin-top: 0;">
#                     {html.escape(str(report['verdict']))}
#                 </div>
#             """, unsafe_allow_html=True)

#             hidden = {"Unknown", "Unknown Org", "Unknown ASN", "None published", "None", ""}
#             rows = [
#                 ("Resolved IP", report['ip']),
#                 ("Location", report['country']),
#                 ("House Org", report['org']),
#                 ("ASN", report['asn']),
#                 ("Reverse DNS", report['reverse_dns']),
#                 ("Domain Age", report['domain_age']),
#                 ("TLS Ward", report['tls_summary']),
#             ]
#             rows = [(k, v) for k, v in rows if v is not None and str(v) not in hidden and not str(v).startswith("N/A")]
#             row_html = "".join(f"<div>{k}: <code>{html.escape(str(v))}</code></div>" for k, v in rows)
#             st.markdown(f"""
#                 <div class="hp-parchment-box">
#                     <div style="color: #b45309; margin-bottom: 6px;">[ TELEMETRY DATA ]</div>
#                     {row_html or "<div>No public telemetry available.</div>"}
#                 </div>
#             """, unsafe_allow_html=True)

#         # ---- RIGHT: reasoning, compact ward flags, then the full evidence ----
#         with r_col2:
#             st.markdown("""
#                 <div style="color: #5b1a18; font-weight: bold; margin-bottom: 5px;">[ MAGICAL AI REASONING // TRACK 2 ]</div>
#             """, unsafe_allow_html=True)
#             st.markdown(f'<div class="hp-parchment-box" style="margin-top: 0;">{report["explanation"]}</div>', unsafe_allow_html=True)

#             st.markdown("""
#                 <div style="color: #5b1a18; font-weight: bold; margin-top: 10px; margin-bottom: 5px;">[ PATRONUM WARD FLAGS ]</div>
#             """, unsafe_allow_html=True)
#             for f in report['flags']:
#                 if "ANOMALY" in f or "FORBIDDEN" in f:
#                     box_color = "#dc2626"
#                 elif "WARNING" in f:
#                     box_color = "#d97706"
#                 elif "WARD" in f:
#                     box_color = "#15803d"
#                 else:
#                     box_color = "#5b1a18"
#                 st.markdown(
#                     f'<div class="hp-parchment-box" style="border-color: {box_color}; padding: 8px 12px; margin: 4px 0; box-shadow: 3px 3px 0px {box_color};">{html.escape(f)}</div>',
#                     unsafe_allow_html=True,
#                 )

#             if report.get("details"):
#                 with st.expander("[ FULL EVIDENCE SCROLL ]"):
#                     st.markdown(f'<div class="hp-parchment-box" style="margin-top: 0;">{report["details"]}</div>', unsafe_allow_html=True)
import base64
import glob
import html
import os

import streamlit as st
from agent_llm import run_investigation

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def find_harry_image():
    """Look for the Harry image next to app.py using several common names."""
    for name in ["harry.png", "harry.PNG", "harry.png.png", "harry.jpg", "harry.jpeg", "image.png"]:
        p = os.path.join(BASE_DIR, name)
        if os.path.exists(p):
            return p
    matches = glob.glob(os.path.join(BASE_DIR, "*harry*.*"))
    return matches[0] if matches else None


def get_base64_image(path):
    """Return the file as a base64 string (empty string if not found)."""
    if path:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


def get_nvidia_key():
    """NVIDIA key from the environment, or from .streamlit/secrets.toml. Never hard-code it."""
    key = os.environ.get("NVIDIA_API_KEY")
    if key:
        return key
    try:
        return st.secrets.get("NVIDIA_API_KEY")
    except Exception:
        return None


harry_path = find_harry_image()
harry_b64 = get_base64_image(harry_path)
harry_mime = "image/jpeg" if harry_path and harry_path.lower().endswith((".jpg", ".jpeg")) else "image/png"

# Pixel cloud strip used as the sky at the top of the page
@st.cache_data
def build_clouds_b64(path):
    """Load clouds.png and fade its bottom edge to transparent so it blends into the page."""
    try:
        from PIL import Image
        import io
        img = Image.open(path).convert("RGBA")
        w, h = img.size
        fade_start = int(h * 0.55)
        alpha = Image.new("L", (1, h), 255)
        for y in range(h):
            if y > fade_start:
                alpha.putpixel((0, y), max(0, int(255 * (1 - (y - fade_start) / (h - fade_start)))))
        img.putalpha(alpha.resize((w, h)))
        buf = io.BytesIO()
        img.save(buf, "PNG")
        return base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return get_base64_image(path)


clouds_path = os.path.join(BASE_DIR, "clouds.png")
clouds_b64 = build_clouds_b64(clouds_path) if os.path.exists(clouds_path) else ""

# Set Page Config
st.set_page_config(
    page_title="Cyber-Patronum // Magical Threat Intelligence", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Pixel Art Harry Potter Sky Aesthetic CSS
st.markdown("""
    <style>
    /* Hide Default Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    
    @keyframes floatHarry {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-6px) rotate(-1deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }

    /* Magical Pixel Sky Background */
    .stApp {
        background: linear-gradient(180deg, #bae6fd 0%, #e0f2fe 40%, #f0fdf4 100%);
        font-family: 'Courier New', Courier, monospace;
        color: #4a0404;
    }

    /* Top Retro Navigation Bar (No Line) */
    .hp-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 20px;
        font-weight: bold;
        color: #5b1a18;
        font-size: 0.95rem;
        letter-spacing: 2px;
        margin-bottom: 20px;
        border-bottom: none !important;
    }
    .hp-nav-links span {
        margin-right: 25px;
        cursor: pointer;
    }
    .hp-nav-links span:hover {
        color: #b45309;
    }
    .hp-hearts {
        color: #dc2626;
        font-size: 1.2rem;
        letter-spacing: 4px;
    }

    /* Pixel Art Title Styling */
    .hp-title-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
    }
    .hp-main-title {
        color: #5b1a18;
        font-size: 3rem;
        font-weight: 900;
        letter-spacing: 4px;
        line-height: 1.1;
        text-shadow: 2px 2px 0px #fde047;
    }

    /* Floating Harry Potter Pixel Image Container */
    .floating-harry-container {
        animation: floatHarry 4s ease-in-out infinite;
        filter: drop-shadow(4px 4px 0px rgba(91, 26, 24, 0.2));
    }
    .floating-harry-container img {
        image-rendering: pixelated;
        display: block;
        width: 240px;
        max-width: 100%;
    }

    /* Wizard Banner Box (Still) */
    .hp-wizard-banner {
        background: rgba(255, 255, 255, 0.95);
        border: 3px solid #5b1a18;
        box-shadow: 6px 6px 0px #5b1a18;
        border-radius: 4px;
        padding: 16px 20px;
        margin-bottom: 25px;
        display: flex;
        align-items: center;
        gap: 20px;
    }

    /* Retro Pixel Input Box (Blank by default) */
    .stTextInput input {
        background-color: #ffffff !important;
        color: #4a0404 !important;
        border: 3px solid #5b1a18 !important;
        font-family: 'Courier New', Courier, monospace !important;
        border-radius: 0px !important;
        padding: 12px !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        box-shadow: 4px 4px 0px #5b1a18 !important;
    }
    .stTextInput label {
        color: #5b1a18 !important;
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
    }

    /* Retro Pixel Game Button ("START THE SCAN") */
    .stButton > button {
        background-color: #5b1a18 !important;
        color: #fde047 !important;
        border: 3px solid #5b1a18 !important;
        border-radius: 0px !important;
        font-family: 'Courier New', Courier, monospace !important;
        font-weight: 900 !important;
        font-size: 1.1rem !important;
        padding: 12px 28px !important;
        width: 100%;
        box-shadow: 4px 4px 0px #fde047 !important;
        transition: all 0.1s ease-in-out !important;
    }
    .stButton > button:hover {
        background-color: #7f1d1d !important;
        transform: translate(-2px, -2px);
        box-shadow: 6px 6px 0px #fde047 !important;
    }

    /* Retro Sharp Square Parchment Boxes for Results */
    .hp-parchment-box {
        background-color: #fffbeb;
        border: 3px solid #5b1a18;
        border-radius: 0px;
        padding: 20px;
        color: #450a0a;
        font-family: 'Courier New', Courier, monospace;
        box-shadow: 5px 5px 0px #5b1a18;
        margin-top: 10px;
        margin-bottom: 15px;
        line-height: 1.6;
        font-weight: bold;
    }

    /* Metric Display Overrides */
    div[data-testid="stMetricValue"] {
        color: #5b1a18 !important;
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 2.5rem !important;
        font-weight: 900 !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #b45309 !important;
        font-family: 'Courier New', Courier, monospace !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

# Pixel clouds across the upper part of the page (layered over the sky gradient)
if clouds_b64:
    st.markdown(f"""
        <style>
        .stApp {{
            background:
                url("data:image/png;base64,{clouds_b64}") center top / 100% auto no-repeat,
                linear-gradient(180deg, #bae6fd 0%, #e0f2fe 40%, #f0fdf4 100%) !important;
            image-rendering: pixelated;
        }}
        </style>
    """, unsafe_allow_html=True)
else:
    st.warning(f"clouds.png not found. Put it in this folder: {BASE_DIR}")

# Top Retro Game Navigation Bar (No bottom line)
st.markdown("""
    <div class="hp-nav">
        <div class="hp-hearts" style="margin-left: auto;">[♥ ♥ ♥]</div>
    </div>
""", unsafe_allow_html=True)

# Header Section with Floating Pixel Harry Potter
st.markdown(f"""
    <div class="hp-title-container">
        <div>
            <div class="hp-main-title">CYBER-PATRONUM</div>
            <div style="color: #b45309; font-weight: bold; font-size: 1.05rem; letter-spacing: 1px;">
                [ HOGWARTS MAGICAL THREAT INTELLIGENCE & INVESTIGATION AGENT ]
            </div>
        </div>
        <div class="floating-harry-container">
            <img src="data:{harry_mime};base64,{harry_b64}" alt="Harry Potter on broomstick" />
        </div>
    </div>
""", unsafe_allow_html=True)

if not harry_b64:
    st.warning(f"harry.png not found. Put it in this folder: {BASE_DIR}")

# Wizard Banner Card (Still)
st.markdown("""
    <div class="hp-wizard-banner">
        <div style="font-size: 2rem;">⚡</div>
        <div>
            <div style="color: #5b1a18; font-weight: 900; font-size: 1.1rem; letter-spacing: 1px;">SPELLCASTER ASSISTANT ONLINE</div>
            <div style="color: #78350f; font-size: 0.95rem; font-weight: bold; margin-top: 2px;">
                "Expecto Patronum! Enter any target domain or IP below to cast investigation spells and ward off dark anomalies."
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Input Controls (Blank default value for universal website testing)
col_input, col_btn = st.columns([3, 1])

with col_input:
    target_input = st.text_input(
        "CAST SPELL // TARGET INPUT",
        value="",
        placeholder="e.g. google.com, github.com, 185.220.101.5"
    )

with col_btn:
    st.write(" ")
    st.write(" ")
    run_scan = st.button("START THE SCAN")

# Scan Execution & Retro Report Results
if run_scan:
    if not target_input.strip():
        st.markdown("""
            <div class="hp-parchment-box" style="border-color: #dc2626; color: #dc2626;">
                SPELL FAILED: Please enter a valid target domain or IP address to investigate.
            </div>
        """, unsafe_allow_html=True)
    else:
        with st.spinner("Casting OSINT spells across DNS, registry, certificate and reputation nodes..."):
            result = run_investigation(target_input, api_key=get_nvidia_key())
            report = result["report"]

        st.markdown("---")
        st.markdown(f"""
            <div style="color: #5b1a18; font-weight: 900; font-size: 1.3rem; margin-bottom: 10px; letter-spacing: 1px;">
                [ INVESTIGATION REPORT: {html.escape(str(report['target']))} ]
            </div>
        """, unsafe_allow_html=True)

        r_col1, r_col2 = st.columns([1, 2])

        # ---- LEFT: score, verdict, and only the telemetry we actually have ----
        with r_col1:
            st.metric(
                label="DARK ARTS RISK SCORE",
                value=f"{report['risk_score']}%",
                delta=report['confidence'] + " Confidence",
                delta_color="off",
            )
            st.markdown(f"""
                <div class="hp-parchment-box" style="padding: 10px 14px; margin-top: 0;">
                    {html.escape(str(report['verdict']))}
                </div>
            """, unsafe_allow_html=True)

            hidden = {"Unknown", "Unknown Org", "Unknown ASN", "None published", "None", ""}
            rows = [
                ("Resolved IP", report['ip']),
                ("Location", report['country']),
                ("House Org", report['org']),
                ("ASN", report['asn']),
                ("Reverse DNS", report['reverse_dns']),
                ("Domain Age", report['domain_age']),
                ("TLS Ward", report['tls_summary']),
            ]
            rows = [(k, v) for k, v in rows if v is not None and str(v) not in hidden and not str(v).startswith("N/A")]
            row_html = "".join(f"<div>{k}: <code>{html.escape(str(v))}</code></div>" for k, v in rows)
            st.markdown(f"""
                <div class="hp-parchment-box">
                    <div style="color: #b45309; margin-bottom: 6px;">[ TELEMETRY DATA ]</div>
                    {row_html or "<div>No public telemetry available.</div>"}
                </div>
            """, unsafe_allow_html=True)

        # ---- RIGHT: reasoning, compact ward flags, then the full evidence ----
        with r_col2:
            st.markdown("""
                <div style="color: #5b1a18; font-weight: bold; margin-bottom: 5px;">[ MAGICAL AI REASONING // TRACK 2 ]</div>
            """, unsafe_allow_html=True)
            st.markdown(f'<div class="hp-parchment-box" style="margin-top: 0;">{report["explanation"]}</div>', unsafe_allow_html=True)

            mode_label = {
                "nemotron": "NEMOTRON AGENT",
                "nemotron+fallback": "NEMOTRON AGENT + STANDARD CHECKS",
                "fallback": "FIXED PIPELINE",
            }.get(result["mode"], "AGENT")
            with st.expander(f"[ SPELL LOG // {len(result['log'])} STEPS // {mode_label} ]"):
                log_lines = "<br>".join(
                    f"<b>{e['step']}. {html.escape(str(e['action']))}</b> &mdash; {html.escape(str(e['thought']))}"
                    f"<br>&nbsp;&nbsp;&rarr; {html.escape(str(e['observation']))}"
                    for e in result["log"]
                )
                notice = f"<br><br><i>{html.escape(result['notice'])}</i>" if result.get("notice") else ""
                st.markdown(f'<div class="hp-parchment-box" style="margin-top: 0;">{log_lines}{notice}</div>', unsafe_allow_html=True)

            st.markdown("""
                <div style="color: #5b1a18; font-weight: bold; margin-top: 10px; margin-bottom: 5px;">[ PATRONUM WARD FLAGS ]</div>
            """, unsafe_allow_html=True)
            for f in report['flags']:
                if "ANOMALY" in f or "FORBIDDEN" in f:
                    box_color = "#dc2626"
                elif "WARNING" in f:
                    box_color = "#d97706"
                elif "WARD" in f:
                    box_color = "#15803d"
                else:
                    box_color = "#5b1a18"
                st.markdown(
                    f'<div class="hp-parchment-box" style="border-color: {box_color}; padding: 8px 12px; margin: 4px 0; box-shadow: 3px 3px 0px {box_color};">{html.escape(f)}</div>',
                    unsafe_allow_html=True,
                )

            if report.get("details"):
                with st.expander("[ FULL EVIDENCE SCROLL ]"):
                    st.markdown(f'<div class="hp-parchment-box" style="margin-top: 0;">{report["details"]}</div>', unsafe_allow_html=True)