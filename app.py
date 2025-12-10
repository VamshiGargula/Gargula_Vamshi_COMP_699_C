import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from jinja2 import Template
import graphviz
from datetime import datetime
import json
import os
import traceback
import logging
from io import StringIO
import base64

st.set_page_config(page_title="Task Automator Lab", layout="wide", page_icon="Lightning")

st.markdown("""
<style>
    body {background:#f0f4ff; margin:0; padding:0;}
    .main {background:#f0f4ff; padding:0 2rem;}
    h1 {
        font-size:5.5rem; font-weight:900; text-align:center; 
        background: linear-gradient(90deg, #1e40af, #3b82f6, #60a5fa);
        -webkit-background-clip: text; background-clip: text;
        color:transparent; margin:0; padding:2rem 0 0.5rem 0;
        text-shadow: 0 10px 30px rgba(59,130,246,0.3);
    }
    .subtitle {
        text-align:center; font-size:1.8rem; color:#64748b; font-weight:500; margin-bottom:3rem;
    }
    .card {
        background:white; border-radius:24px; padding:32px; margin:30px 0;
        box-shadow:0 20px 60px rgba(30,58,138,0.12);
        border:1px solid rgba(59,130,246,0.15);
        transition:all 0.4s;
    }
    .card:hover {
        transform:translateY(-12px);
        box-shadow:0 40px 100px rgba(30,58,138,0.2);
    }
    .glow-button {
        background:linear-gradient(135deg,#3b82f6,#2563eb);
        color:white; border:none; border-radius:18px;
        padding:18px 40px; font-size:1.3rem; font-weight:700;
        box-shadow:0 12px 40px rgba(59,130,246,0.4);
        transition:all 0.3s;
        cursor:pointer;
    }
    .glow-button:hover {
        background:linear-gradient(135deg,#2563eb,#1d4ed8);
        transform:translateY(-6px);
        box-shadow:0 20px 50px rgba(59,130,246,0.5);
    }
    .step-card {
        background:#f8fafc; border-radius:16px; padding:20px; margin:12px 0;
        border-left:6px solid #3b82f6; box-shadow:0 8px 25px rgba(0,0,0,0.06);
    }
    .code-preview {
        background:#1e293b; color:#e2e8f0; border-radius:16px; padding:24px;
        font-family:'Courier New',monospace; font-size:1rem;
        box-shadow:inset 0 8px 20px rgba(0,0,0,0.3);
    }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius:14px; border:2px solid #93c5fd; padding:14px;
    }
    .stSelectbox > div > div {border-radius:14px;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>Task Automator Lab</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Build • Visualize • Execute • Export Perfect Python</div>", unsafe_allow_html=True)

if 'workflows' not in st.session_state:
    st.session_state.workflows = {}
if 'current_id' not in st.session_state:
    st.session_state.current_id = None

def generate_code(steps):
    template = """
import pandas as pd
import logging
import time
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
def retry(func, max_attempts=3, delay=1):
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                logger.error(f"Failed after {max_attempts} attempts: {e}")
                raise
            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
            time.sleep(delay)
def main():
    try:
        logger.info("Starting automation workflow")
       
        {% for step in steps %}
        # Step {{ loop.index }}: {{ step.name }}
        logger.info("Executing: {{ step.name }}")
        try:
            {% if step.type == "read_csv" %}
            df_{{ loop.index }} = pd.read_csv("{{ step.params.file }}")
            logger.info(f"Loaded {{ step.params.file }} - {len(df_{{ loop.index }})} rows")
            {% elif step.type == "filter" %}
            df_{{ loop.index }} = df_{{ step.params.source }}.query("{{ step.params.condition }}")
            logger.info(f"Filtered data - {len(df_{{ loop.index }})} rows remaining")
            {% elif step.type == "write_excel" %}
            df_{{ step.params.source }}.to_excel("{{ step.params.output }}", index=False)
            logger.info(f"Saved to {{ step.params.output }}")
            {% elif step.type == "custom" %}
            {% if step.code.strip() %}
{{ step.code | indent(12) }}
            {% else %}
            pass
            {% endif %}
            {% endif %}
        except Exception as e:
            logger.error(f"Step {{ loop.index }} failed: {e}")
            raise
       
        {% endfor %}
       
        logger.info("Workflow completed successfully!")
       
    except Exception as e:
        logger.critical(f"Workflow failed: {e}")
        raise
if __name__ == "__main__":
    main()
"""
    t = Template(template)
    return t.render(steps=steps)

def create_3d_flow(steps):
    if not steps:
        return go.Figure()
    
    x = list(range(len(steps)))
    y = [0] * len(steps)
    z = [np.sin(i/1.8)*4 for i in range(len(steps))]
    
    fig = go.Figure()
    
    for i, step in enumerate(steps):
        fig.add_trace(go.Scatter3d(
            x=[x[i]], y=[y[i]], z=[z[i]],
            mode='markers+text',
            marker=dict(size=50, color='#3b82f6', opacity=0.95, line=dict(width=4, color='#1e40af')),
            text=step['name'],
            textposition="middle center",
            textfont=dict(size=16, color="white"),
            name=step['name'],
            hoverinfo="text",
            hovertext=f"<b>{step['name']}</b><br>Type: {step['type'].replace('_',' ').title()}"
        ))
    
    for i in range(1, len(steps)):
        fig.add_trace(go.Scatter3d(
            x=[x[i-1], x[i]], y=[0,0], z=[z[i-1], z[i]],
            mode='lines',
            line=dict(color='#1e40af', width=12),
            hoverinfo='none'
        ))
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, backgroundcolor="white"),
            yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
            zaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
            camera=dict(eye=dict(x=1.8, y=1.8, z=1.8))
        ),
        paper_bgcolor="#f0f4ff",
        plot_bgcolor="#f0f4ff",
        height=700,
        margin=dict(l=0,r=0,b=0,t=0)
    )
    return fig

# MAIN LAYOUT
col_left, col_right = st.columns([1.8, 1.2])

with col_left:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Workflow Studio")

    if st.button("New Workflow", key="new_wf"):
        st.session_state.current_id = len(st.session_state.workflows)
        st.session_state.workflows[st.session_state.current_id] = {
            "name": "New Workflow",
            "steps": [],
            "created": datetime.now().isoformat()
        }
        st.rerun()

    if st.session_state.workflows:
        selected = st.selectbox("My Workflows",
            options=list(st.session_state.workflows.keys()),
            format_func=lambda x: st.session_state.workflows[x]["name"],
            key="wf_select")
        workflow = st.session_state.workflows[selected]

        workflow["name"] = st.text_input("Workflow Name", workflow["name"], key="wf_name")

        st.markdown("### Add Step")
        step_type = st.selectbox("Step Type", [
            "Read CSV", "Filter Data", "Transform Column", "Write Excel", "Send Email", "Custom Code"
        ], key="step_type")

        step_name = st.text_input("Step Name", f"Step {len(workflow['steps'])+1}", key="step_name")

        params = {}
        if "CSV" in step_type:
            params["file"] = st.text_input("CSV File Path", "data/input.csv", key="csv_path")
        elif "Filter" in step_type:
            params["source"] = st.selectbox("Source Data", ["Previous Step"], key="filter_src")
            params["condition"] = st.text_area("Filter Condition", "age > 30", key="filter_cond")
        elif "Transform" in step_type:
            params["column"] = st.text_input("Column to Transform", key="trans_col")
            params["operation"] = st.text_input("Operation (Python)", key="trans_op")
        elif "Excel" in step_type:
            params["output"] = st.text_input("Output File", "output/report.xlsx", key="excel_out")

        code = ""
        if "Custom" in step_type:
            code = st.text_area("Custom Python Code", height=200, key="custom_code",
                               placeholder="def process(data):\n    return data.upper()")

        if st.button("Add Step", key="add_step"):
            new_step = {
                "name": step_name,
                "type": step_type.lower().replace(" ", "_"),
                "params": params,
                "code": code
            }
            workflow["steps"].append(new_step)
            st.success("Step added!")
            st.rerun()

        if workflow["steps"]:
            st.markdown("### Generated Python Code")
            code = generate_code(workflow["steps"])
            st.code(code, language="python")
            st.download_button("Export Script", code, f"{workflow['name'].replace(' ','_')}.py", "text/python", key="export")

    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Instant 3D Workflow View")
    if st.session_state.current_id is not None and st.session_state.workflows[st.session_state.current_id]["steps"]:
        steps = st.session_state.workflows[st.session_state.current_id]["steps"]
        fig = create_3d_flow(steps)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Add steps to see instant 3D visualization")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Workflow Library")
    for wid, wf in st.session_state.workflows.items():
        with st.expander(f"{wf['name']} • {len(wf['steps'])} steps"):
            st.write(f"Created: {wf.get('created','N/A')[:10]}")
            if st.button("Load", key=f"load_{wid}"):
                st.session_state.current_id = wid
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
