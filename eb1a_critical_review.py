
import streamlit as st
import docx
import re

st.set_page_config(page_title="EB1A Critical Role Questionnaire Checker", layout="wide")
st.title("EB1A Critical Role Questionnaire Review Tool")

st.markdown("""
This tool analyzes your uploaded **Critical Role Questionnaire** for **EB1A** to ensure it meets USCIS-compliant standards.  
**Eligibility Criteria Checked:**  
- At least 3-4 distinct projects filled using separate sets  
- No more than 2 distinct organizations  
- Each question answered in **detailed, non-generic** manner  
- Every project includes **quantifiable impact metrics**  
- The role must reflect criticality to **both the project and organization**
- Project and organization names must be clear

Please upload a `.docx` file with one questionnaire set per project.
""")

uploaded_file = st.file_uploader("Upload the filled Critical Role Questionnaire (.docx format only)", type=["docx"])

if uploaded_file:
    doc = docx.Document(uploaded_file)
    text = " ".join([para.text for para in doc.paragraphs if para.text.strip()])
    st.subheader("Extracted Text Preview")
    st.text_area("Document Contents", text, height=300)

    # Extract all project sections by identifying repeated questionnaire headings (e.g., Project Title)
    projects = re.split(r"(?i)project title[:：]", text)[1:]  # skip first empty split
    st.markdown(f"### 📊 Project Sets Found: {len(projects)}")

    # Basic validity
    warnings = []
    feedback = []

    if len(projects) < 3:
        warnings.append("❌ Less than 3 distinct project entries found. Minimum 3–4 are required.")

    org_names = set()
    for i, proj in enumerate(projects, 1):
        proj_feedback = []
        proj = "Project Title: " + proj

        # Check for organization name
        org_match = re.search(r"(?i)organization name[:：]?\s*(.+)", proj)
        if org_match:
            org = org_match.group(1).strip().split("\n")[0]
            org_names.add(org)
        else:
            proj_feedback.append("⚠️ Organization name not clearly mentioned.")

        # Check for length and completeness
        if len(proj.split()) < 300:
            proj_feedback.append("⚠️ Project response appears too short. Add more detailed responsibilities and outcomes.")

        # Check for criticality indicators
        if not re.search(r"(?i)critical|lead|led|responsible|drove|strategic|owned", proj):
            proj_feedback.append("⚠️ Project lacks keywords indicating critical role.")

        # Check for impact metrics
        if not re.search(r"(?i)[0-9]{1,3}%|\$[0-9]+|[0-9]+\s+(users|clients|systems|transactions|leads|deals|properties)", proj):
            proj_feedback.append("⚠️ No quantifiable impact metrics found. Include measurable results or metrics.")

        feedback.append((i, proj_feedback))

    if len(org_names) > 2:
        warnings.append(f"❌ Found more than 2 organizations: {', '.join(org_names)}")

    st.markdown("### ⚠️ General Warnings")
    if warnings:
        for w in warnings:
            st.error(w)
    else:
        st.success("✅ General eligibility structure is good!")

    st.markdown("### 📝 Project-by-Project Feedback")
    for i, proj_fb in feedback:
        with st.expander(f"Feedback for Project {i}"):
            if proj_fb:
                for issue in proj_fb:
                    st.warning(issue)
            else:
                st.success("✅ Project is sufficiently detailed and meets requirements.")

    st.markdown("---")
    st.info("For best results, ensure each project section uses the full questionnaire and includes detailed, metrics-backed explanations.")
