import streamlit as st
import ast
import json
import time
import importlib.util
import os
from pathlib import Path

st.set_page_config(page_title='Task Automator Lab - Prototype', layout='wide')

if 'history' not in st.session_state:
    st.session_state['history'] = []
if 'workflow' not in st.session_state:
    st.session_state['workflow'] = {}

st.title('Task Automator Lab')

with st.sidebar:
    uploaded_module = st.file_uploader('Upload custom Python module (.py) to import functions', type=['py'])
    smtp_host = st.text_input('SMTP host (optional)')
    smtp_port = st.text_input('SMTP port (optional)')
    smtp_user = st.text_input('SMTP user (optional)')
    smtp_pass = st.text_input('SMTP pass (optional)', type='password')

st.header('1) Enter sequence of tasks in plain English (one per line)')
raw_tasks = st.text_area('Tasks', placeholder='Example: Download file from SFTP\nProcess CSV and extract rows where status=active\nUpload results to S3')

if st.button('Parse Tasks'):
    lines = [l.strip() for l in raw_tasks.splitlines() if l.strip()]
    steps = []
    for i, l in enumerate(lines, 1):
        steps.append({
            'id': f'step_{i}',
            'title': l,
            'params': {},
            'loop': None,
            'retry': {'count': 0, 'delay': 0},
            'exception_handler': '',
            'custom_function': None,
            'critical': False,
            'alert': {'enabled': False, 'recipients': []}
        })
    st.session_state['workflow'] = {'name': 'workflow_' + str(int(time.time())), 'steps': steps}
    st.session_state['history'].append(json.dumps(st.session_state['workflow']))
    st.success(f'Parsed {len(steps)} steps')

if st.session_state.get('workflow'):
    wf = st.session_state['workflow']
    st.header('Workflow:')
    wf_name = st.text_input('Workflow name', value=wf.get('name'))
    wf['name'] = wf_name
    for step in wf['steps']:
        with st.expander(step['title']):
            title = st.text_input('Title', value=step['title'], key=step['id'] + '_title')
            step['title'] = title
            params_text = st.text_area('Input parameters as JSON (e.g. {"file_path":"string"})', value=json.dumps(step.get('params') or {}), key=step['id'] + '_params')
            try:
                step['params'] = json.loads(params_text)
            except Exception:
                st.error('Invalid JSON for params')
            loop_type = st.selectbox('Loop type', options=['none', 'for', 'while'], index=0, key=step['id'] + '_loop_type')
            if loop_type != 'none':
                loop_expr = st.text_input('Loop expression (for: iterable variable; while: condition)', key=step['id'] + '_loop_expr')
                step['loop'] = {'type': loop_type, 'expr': loop_expr}
            else:
                step['loop'] = None
            retry_count = st.number_input('Retry count', min_value=0, step=1, value=step['retry'].get('count', 0), key=step['id'] + '_retry_count')
            retry_delay = st.number_input('Retry delay seconds', min_value=0, step=1, value=step['retry'].get('delay', 0), key=step['id'] + '_retry_delay')
            step['retry'] = {'count': int(retry_count), 'delay': int(retry_delay)}
            exc_handler = st.text_area('Exception handler body (Python code to run in except block)', value=step.get('exception_handler', ''), key=step['id'] + '_exc')
            step['exception_handler'] = exc_handler
            custom_func_name = st.text_input('Custom function name to call (from uploaded module)', value=step.get('custom_function') or '', key=step['id'] + '_cust')
            step['custom_function'] = custom_func_name or None
            critical = st.checkbox('Mark task critical', value=step.get('critical', False), key=step['id'] + '_crit')
            step['critical'] = critical
            alert_enabled = st.checkbox('Enable alert for this task', value=step.get('alert', {}).get('enabled', False), key=step['id'] + '_alert')
            recipients = st.text_input('Alert recipients (comma separated emails)', value=','.join(step.get('alert', {}).get('recipients', [])), key=step['id'] + '_alert_recip')
            step['alert'] = {'enabled': alert_enabled, 'recipients': [r.strip() for r in recipients.split(',') if r.strip()]}

    st.session_state['workflow'] = wf

    st.header('2) Generated script (editable)')

    def build_script(workflow, module_filename=None):
        lines = []
        lines.append('import logging')
        lines.append('import time')
        if smtp_host and smtp_port and smtp_user and smtp_pass:
            lines.append('import smtplib')
            lines.append('from email.message import EmailMessage')
        if module_filename:
            lines.append('import importlib.util')
            lines.append("spec=importlib.util.spec_from_file_location('custom', r'" + module_filename.replace("\\", "\\\\") + "')")
            lines.append("custom=importlib.util.module_from_spec(spec)")
            lines.append('spec.loader.exec_module(custom)')
        lines.append("logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')")
        lines.append('def send_alert(subject,body,recipients):')
        if smtp_host and smtp_port and smtp_user and smtp_pass:
            lines.append('    msg=EmailMessage()')
            lines.append("    msg['Subject']=subject")
            lines.append("    msg.set_content(body)")
            lines.append('    with smtplib.SMTP_SSL("' + smtp_host + '",' + smtp_port + ') as s:')
            lines.append('        s.login("' + smtp_user + '","' + smtp_pass + '")')
            lines.append('        s.send_message(msg)')
        else:
            lines.append('    return')
        for step in workflow['steps']:
            fn_name = step['id']
            lines.append('def ' + fn_name + '(context):')
            if step['params']:
                lines.append('    params=context.get("' + fn_name + '_params",{})')
            if step['custom_function']:
                lines.append('    if hasattr(custom,"' + step['custom_function'] + '"):')
                lines.append('        func=getattr(custom,"' + step['custom_function'] + '")')
                lines.append('        return func(**(context.get("' + fn_name + '_params",{})))')
            if step['loop']:
                if step['loop']['type'] == 'for':
                    lines.append('    for item in ' + (step['loop']['expr'] or '[]') + ':')
                    lines.append('        logging.info("running ' + fn_name + ' iteration")')
                    body_prefix = '        '
                else:
                    lines.append('    while ' + (step['loop']['expr'] or 'False') + ':')
                    lines.append('        logging.info("running ' + fn_name + ' iteration")')
                    body_prefix = '        '
            else:
                body_prefix = '    '
            if not step['custom_function']:
                lines.append(body_prefix + "logging.info('Executing: " + step['title'].replace("'", "\\'") + "')")
            if step['retry'] and step['retry'].get('count', 0) > 0:
                lines.append(body_prefix + 'attempt=0')
                lines.append(body_prefix + 'while attempt<' + str(step['retry']['count']) + ':')
                lines.append(body_prefix + '    try:')
                lines.append(body_prefix + '        pass')
                lines.append(body_prefix + '        break')
                lines.append(body_prefix + '    except Exception as e:')
                if step['exception_handler']:
                    for l in step['exception_handler'].splitlines():
                        lines.append(body_prefix + '    ' + l)
                lines.append(body_prefix + '    attempt+=1')
                lines.append(body_prefix + '    time.sleep(' + str(step['retry']['delay']) + ')')
            else:
                if step['exception_handler']:
                    lines.append(body_prefix + 'try:')
                    lines.append(body_prefix + '    pass')
                    lines.append(body_prefix + 'except Exception as e:')
                    for l in step['exception_handler'].splitlines():
                        lines.append(body_prefix + '    ' + l)
            if step['critical']:
                lines.append(body_prefix + "logging.error('Task " + fn_name + " marked critical - check results')")
            if step['alert'] and step['alert'].get('enabled') and smtp_host and smtp_port and smtp_user and smtp_pass:
                lines.append(body_prefix + "send_alert('Alert: " + fn_name.replace("'", "\\'") + "','Task reported issue'," + str(step['alert'].get('recipients', [])) + ')')
        lines.append('def run_workflow():')
        lines.append('    context={}')
        for step in workflow['steps']:
            lines.append('    ' + step['id'] + '(context)')
        lines.append("if __name__=='__main__':")
        lines.append('    run_workflow()')
        return '\n'.join(lines)

    module_path = None
    if uploaded_module is not None:
        module_path = os.path.join('uploaded_modules', uploaded_module.name)
        Path('uploaded_modules').mkdir(exist_ok=True)
        with open(module_path, 'wb') as f:
            f.write(uploaded_module.getvalue())

    script_text = build_script(wf, module_path)
    editor = st.text_area('Script editor', value=script_text, height=400, key='script_editor')

    try:
        ast.parse(editor)
        valid = True
    except Exception as e:
        valid = False
        st.error('Script has syntax errors: ' + str(e))

    if st.button('Save script to file') and valid:
        filename = st.text_input('Output filename', value=wf['name'] + '.py', key='out_file')
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(editor)
            st.success(f'Saved to {filename}')

    st.download_button('Download script', data=editor, file_name=wf['name'] + '.py', mime='text/x-python')

    st.header('3) Edit history (session)')
    for i, h in enumerate(st.session_state['history']):
        st.write(f'Version {i+1} - {json.loads(h).get("name") if h else ""}')

    if st.button('Save workflow template'):
        template_name = st.text_input('Template filename', value=wf['name'] + '_template.json', key='template_name')
        if template_name:
            with open(template_name, 'w', encoding='utf-8') as f:
                json.dump(wf, f, indent=2)
            st.success(f'Template saved to {template_name}')

    st.header('4) Import custom functions into runtime (demo)')
    if module_path and st.button('Load uploaded module now'):
        spec = importlib.util.spec_from_file_location('custom', module_path)
        custom = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(custom)
        st.success('Module loaded as variable "custom" in generated script when executed')
