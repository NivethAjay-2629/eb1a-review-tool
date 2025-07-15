import streamlit as st
import docx
import re

# --- Utility Functions ---
def extract_text_from_docx(docx_file):
    doc = docx.Document(docx_file)
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

def split_into_projects(text):
    # Use more aggressive project detection
    project_sections = re.split(r'(?i)(Project\s*\d+[:\s\-])', text)
    combined = []
    for i in range(1, len(project_sections), 2):
        title = project_sections[i].strip()
        content = project_sections[i+1].strip() if i+1 < len(project_sections) else ""
        if len(content) > 100:
            combined.append(f"{title}\n{content}")
    return combined

def evaluate_project_section(proj_text):
    checks = {
        "answers_all_questions": len(re.findall(r'(?i)(Q\d+[:\s])', proj_text)) >= 8,
        "mentions_org": bool(re.search(r'(?i)(company|organization|employer|team|firm)', proj_text)),
        "includes_metrics": bool(re.search(r'(\d+%|\$\d+|million|thousand|ROI|revenue|savings)', proj_text)),
        "shows_criticality": bool(re.search(r'(?i)(critical role|led|architect|strategic|transformed|pillar)', proj_text)),
        "project_specific": not bool(re.search(r'(?i)(multiple projects|various initiatives|across organizations)', proj_text)),
    }
    missing = [k for k, v in checks.items() if not v]
    return checks, missing

def summarize_evaluation(projects):
    summary = []
    for idx, proj in enumerate(projects):
        result, missing = evaluate_project_section(proj)
        status = "\n".join([f"✅ {k.replace('_',' ').capitalize()}" if v else f"❌ {k.replace('_',' ').capitalize()}" for k, v in result.items()])
        detail = "\n- " + "\n- ".join(missing) if missing else "None"
        summary.append((f"Project {idx+1}", status, detail))
    return summary

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
        st.error("❌ You need at least 3 distinct, project-specific questionnaires filled.")
    else:
        st.success("✅ Minimum project count satisfied.")

    orgs = set(re.findall(r'(?i)(?<=Organization: )[A-Za-z0-9 &()\-]+', raw_text))
    if len(orgs) > 2:
        st.warning(f"⚠️ Too many organizations detected: {len(orgs)}. Limit to 2 organizations.")
    elif len(orgs) == 0:
        st.error("❌ No organization detected. Please use 'Organization: <name>' format.")
    else:
        st.success(f"✅ Organizations detected: {', '.join(orgs)}")

    st.markdown("---")
    st.markdown("## 🔍 Project-wise Evaluation")

    results = summarize_evaluation(projects)
    for title, status, missing in results:
        st.markdown(f"### {title}")
        st.code(status)
        st.markdown(f"**Missing elements:**{missing}")

    st.markdown("---")
    st.markdown("✅ For best results:")
    st.markdown("- Ensure each project has its **own full questionnaire**, starting with 'Project 1:', 'Project 2:', etc.")
    st.markdown("- Include **impact metrics** (%, $, etc.).")
    st.markdown("- Explain **your role’s strategic importance**.")
    st.markdown("- Limit to **max 2 organizations**, 3–4 strong projects.")

    st.success("✅ Evaluation complete. Make improvements where needed to maximize USCIS readiness.")
