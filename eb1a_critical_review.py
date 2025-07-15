import streamlit as st
import docx
import re
from collections import defaultdict

# --- Utility Functions ---
def extract_text_from_docx(docx_file):
    doc = docx.Document(docx_file)
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

def split_into_projects(text):
    project_sections = re.split(r'(?i)(?=Project\s+\d+[:\s])', text)
    return [proj.strip() for proj in project_sections if len(proj.strip()) > 100]  # Ignore non-substantive sections

def evaluate_project_section(proj_text):
    checks = {
        "Answers all questions": len(re.findall(r'(?i)(Q\d+[:\s])', proj_text)) >= 8,  # assuming ~8 major questions
        "Mentions organization": bool(re.search(r'(?i)(company|organization|employer|team|firm)', proj_text)),
        "Includes impact metrics": bool(re.search(r'(\d+%|\$\d+|million|thousand|ROI|revenue|savings)', proj_text)),
        "Shows criticality": bool(re.search(r'(?i)(critical role|led|architect|strategic|transformed|pillar)', proj_text)),
        "Is project-specific": not bool(re.search(r'(?i)(multiple projects|various initiatives|across organizations)', proj_text)),
    }
    return checks

def summarize_evaluation(projects):
    summary = []
    for idx, proj in enumerate(projects):
        result = evaluate_project_section(proj)
        status = "\n".join([f"✅ {k}" if v else f"❌ {k}" for k, v in result.items()])
        summary.append((f"Project {idx+1}", result, status))
    return summary

def summarize_what_is_present(raw_text, projects):
    orgs = set(re.findall(r'(?i)(?<=Organization: )[A-Za-z0-9 &()\-]+', raw_text))
    present = defaultdict(str)
    present["Total Projects"] = str(len(projects))
    present["Organizations Mentioned"] = ", ".join(orgs) if orgs else "Not clearly mentioned"
    return present

# --- Streamlit UI ---
st.set_page_config(page_title="EB1A Critical Role Eligibility Checker", layout="centered")
st.title("EB1A Critical Role Questionnaire Evaluator")
st.markdown("Upload a filled Critical Role Questionnaire (DOCX) to assess eligibility and completeness.")

uploaded = st.file_uploader("Upload DOCX File", type="docx")

if uploaded:
    raw_text = extract_text_from_docx(uploaded)
    projects = split_into_projects(raw_text)

    st.markdown(f"### 📁 {len(projects)} project(s) detected")

    if len(projects) < 3:
        st.error("You need at least 3 distinct, project-specific questionnaires filled.")

    orgs = set(re.findall(r'(?i)(?<=Organization: )[A-Za-z0-9 &()\-]+', raw_text))
    if len(orgs) > 2:
        st.warning(f"Too many organizations detected: {len(orgs)}. Limit to 2 organizations.")
    else:
        st.success(f"Organizations detected: {', '.join(orgs) if orgs else 'Not clearly mentioned'}")

    present_summary = summarize_what_is_present(raw_text, projects)
    st.markdown("---")
    st.markdown("## 🧾 Summary of What’s Available")
    for k, v in present_summary.items():
        st.markdown(f"- **{k}**: {v}")

    st.markdown("---")
    st.markdown("## 🔍 Project-wise Evaluation")

    results = summarize_evaluation(projects)
    for title, result, status in results:
        st.markdown(f"### {title}")
        st.code(status)

    st.markdown("---")
    st.markdown("## 🧭 Missing or Required Elements")
    for idx, (_, result, _) in enumerate(results):
        st.markdown(f"### Project {idx+1}")
        missing = [k for k, v in result.items() if not v]
        if not missing:
            st.success("✅ All required elements present.")
        else:
            st.warning("❌ Missing: " + ", ".join(missing))

    st.markdown("---")
    st.markdown("✅ For best results:")
    st.markdown("- Ensure each project has its **own full questionnaire**.")
    st.markdown("- Include **impact metrics** (%, $, etc.).")
    st.markdown("- Explain **your role’s strategic importance to the organization**.")
    st.markdown("- Limit to **max 2 organizations**, 3–4 strong projects.")

    st.success("Evaluation complete. Make adjustments to maximize eligibility and avoid RFEs.")
