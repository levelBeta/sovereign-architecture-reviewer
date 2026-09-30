import streamlit as st
import json, os, glob, time

from rules import evaluate
from explain import explain
from audit import record, verify_chain
from sovereignty import sovereignty_check

st.set_page_config(page_title="builderAnts Sovereign Architecture Reviewer", layout="wide")

SEVERITY_COLOR = {"critical": "🔴", "high": "🟠", "medium": "🟡"}

st.title("Sovereign Architecture Review Agent")
st.caption("100% local · No cloud dependency · Findings mapped to Well-Architected pillars, "
           "CPS 234-aligned control areas, and zero-trust principles.")

tab_review, tab_audit = st.tabs(["Review", "Audit Log"])

with tab_review:
    configs = sorted(glob.glob("configs/*.json"))
    labels = {c: json.load(open(c))["name"] for c in configs}
    choice = st.selectbox("Select architecture to review", configs, format_func=lambda c: labels[c])

    role = st.selectbox("Reviewer role (for audit trail)", ["ciso", "risk_officer", "analyst"])

    col1, col2 = st.columns([1, 1])
    with col1:
        run_clicked = st.button("Run Review", type="primary")
    with col2:
        st.empty()

    if run_clicked:
        pid = os.getpid()
        pre_sovereign, _ = sovereignty_check(pid=pid)

        cfg = json.load(open(choice))
        findings = evaluate(cfg)

        st.subheader(f"Results: {cfg['name']}")
        counts = {"critical": 0, "high": 0, "medium": 0}
        for f in findings:
            counts[f["severity"]] += 1
        st.markdown(f"**{len(findings)} findings** — "
                   f"🔴 {counts['critical']} critical · 🟠 {counts['high']} high · 🟡 {counts['medium']} medium")

        lockin = [f for f in findings if f["lockin"]]
        if lockin:
            st.info(f"Portability note: {len(lockin)} finding(s) indicate vendor lock-in risk, "
                    f"not a security risk on their own.")

        if not findings:
            st.success("No findings. This configuration passes all checks in this review.")
        else:
            t0 = time.time()
            progress = st.progress(0, text="Starting review...")
            for i, f in enumerate(findings, 1):
                progress.progress(i / len(findings), text=f"Explaining finding {i}/{len(findings)}...")
                narrative = explain(f)
                icon = SEVERITY_COLOR[f["severity"]]
                with st.expander(f"{icon} [{f['severity'].upper()}] {f['title']} — `{f['resource']}`"):
                    st.markdown(f"**Evidence:** {f['evidence']}")
                    st.markdown(f"**Well-Architected pillar:** {f['pillar']}")
                    st.markdown(f"**CPS 234-aligned area:** {f['cps234_area']}")
                    st.markdown(f"**Zero-trust principle:** {f['zero_trust']}")
                    st.markdown(f"**Remediation:** {f['remediation']}")
                    st.markdown(f"\n{narrative}")
            progress.empty()
            elapsed = time.time() - t0
            st.caption(f"Reviewed in {elapsed:.1f}s, entirely offline.")

        post_sovereign, post_ext = sovereignty_check(pid=pid)
        st.divider()
        st.subheader("Sovereignty check")
        c1, c2 = st.columns(2)
        c1.metric("Outbound connections from this review", "0" if post_sovereign else str(len(post_ext)))
        c2.metric("Model used", "qwen2.5:3b (local, CPU)")
        if post_sovereign:
            st.success("Confirmed: this review process made zero outbound network connections.")
        else:
            st.warning(f"Unexpected external connections detected: {post_ext}")

        entry = record({
            "action": "review", "config": os.path.basename(choice),
            "findings": len(findings), "role": role,
            "sovereign": bool(post_sovereign),
        })
        st.caption(f"Audit entry recorded — hash `{entry['hash'][:16]}...`")

with tab_audit:
    st.subheader("Audit Log")
    ok, details = verify_chain()
    if ok:
        st.success("Chain valid — no tampering detected.")
    else:
        st.error("Chain integrity FAILED — see details below.")
    for d in details:
        st.text(d)

    if os.path.exists("audit.jsonl"):
        st.divider()
        st.caption("Raw log entries")
        with open("audit.jsonl") as f:
            for line in f:
                st.json(json.loads(line))
    else:
        st.info("No reviews logged yet. Run a review to create the first audit entry.")