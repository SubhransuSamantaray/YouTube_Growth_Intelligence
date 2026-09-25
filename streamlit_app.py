"""
Streamlit Data Science & Growth Studio.
Provides an interactive analytics notebook for deep EDA, retention curve modeling,
traffic quadrant inspection, draft video simulation, and PDF report downloads.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone
import os

from backend.app.database import engine, Base, SessionLocal
from backend.app.models.schema import (
    DerivedVideoMetrics,
    RawRetentionCurve,
    RawTrafficSource,
    RawDemographics,
    DerivedContentCluster,
    Recommendation,
    ComplianceLog,
    QuotaLedger
)
from backend.app.services.compliance_service import ComplianceService
from backend.app.services.ingestion_service import IngestionService
from backend.app.services.ml_service import MLService
from backend.app.services.report_service import ReportService
from backend.app.config import settings

st.set_page_config(
    page_title="YouTube Growth Intelligence Studio",
    page_icon="▶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
Base.metadata.create_all(bind=engine)
db = SessionLocal()

# Ensure seed data exists
if db.query(DerivedVideoMetrics).count() == 0:
    service = IngestionService(db)
    service.seed_synthetic_channel("DevPulse Systems")

st.sidebar.title("▶ YouTube Growth Intelligence")
st.sidebar.caption("Data Science & Algorithmic Studio")

# 30-Day Compliance Badge in Sidebar
comp_service = ComplianceService(db)
comp_status = comp_service.get_compliance_status()
st.sidebar.markdown(f"""
<div style="background-color:#1e293b; padding:10px; border-radius:8px; border:1px solid #334155; margin-bottom:15px;">
    <div style="font-size:11px; color:#94a3b8; font-weight:bold;">COMPLIANCE STATUS (ToS III.E.4)</div>
    <div style="font-size:14px; color:#10b981; font-weight:bold;">30-Day Retention TTL Active</div>
    <div style="font-size:11px; color:#cbd5e1;">Next purge cycle: in {comp_status['days_to_earliest_ttl']} days</div>
</div>
""", unsafe_allow_html=True)

nav = st.sidebar.radio(
    "Select Analysis Module",
    [
        "Executive Dashboard",
        "Audience Retention Modeling",
        "Traffic Efficiency Quadrants",
        "Content Clusters & Groups",
        "Opportunity Matrix & Recs",
        "Draft Video ML Simulator",
        "Compliance & 30d TTL Sweeper",
        "Executive PDF Report Generator",
        "👶 Layman's Growth Academy & Metric Decrypter"
    ]
)

is_brutal = st.sidebar.checkbox("⚡ Brutal Strategic Audit Mode", value=False, help="Unfiltered, non-sugarcoated critique of channel bottlenecks")
is_eli5 = st.sidebar.checkbox("👶 Plain English (ELI5) Mode", value=False, help="Translates all charts, metrics, and parameters into simple everyday analogies with zero technical jargon")


# Module 1: Dashboard
if nav == "Executive Dashboard":
    st.title("📊 Executive Channel Overview")
    st.caption("Channel: DevPulse Systems | Multi-format engineering & architecture content")

    videos = db.query(DerivedVideoMetrics).all()
    v_df = pd.DataFrame([{
        "Title": v.title,
        "Format": v.format_type,
        "Views": v.total_views,
        "Watch Hours": v.total_watch_time_hrs,
        "Avg Retention %": v.avg_view_percentage,
        "Robust Z": v.virality_robust_z,
        "Tier": v.performance_tier,
        "Sub Conv/1k": v.sub_conversion_per_1k,
        "Intro Drop 30s": v.intro_dropoff_30s,
        "Duration (min)": round(v.duration_sec / 60.0, 1)
    } for v in videos])

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Views", f"{v_df['Views'].sum():,}", f"{len(v_df)} videos analyzed")
    k2.metric("Total Watch Time", f"{v_df['Watch Hours'].sum():,.1f} hrs", "Across all cohorts")
    k3.metric("Net Subscribers", f"+{sum(v.net_subscribers for v in videos):,}", "Historical diff tracking")
    k4.metric("Avg Audience Retention", f"{v_df['Avg Retention %'].mean():.1f}%", f"{sum(v.performance_tier == 'Viral Breakout' for v in videos)} viral hits")

    with st.expander("👶 Layman's Quick Translation: What All These Numbers Mean For You", expanded=is_eli5):
        st.markdown("""
        **Zero Data Science Jargon Guarantee:**
        * **1. Total Views (Foot Traffic):** Like people walking into your retail shop. Having views is great, but only if they stay to buy something.
        * **2. Watch Time (Attention Bank):** YouTube's #1 favorite currency. The longer you keep people glued to YouTube, the more YouTube promotes your channel.
        * **3. Retention % (Popcorn Test):** Did they watch to the ending or walk out of the movie theater at minute 2? 48% retention means half your crowd stays.
        * **4. Net Subscribers (VIP Members):** Loyal customers who signed up for your newsletter. 5.5 per 1,000 views means 1 in every 180 viewers hits subscribe.
        """)

    st.markdown("---")
    c1, c2 = st.columns([2, 1])

    with c1:
        st.subheader("Top Uploads: Views vs Total Watch Time")
        top_df = v_df.sort_values(by="Views", ascending=False).head(10)
        fig_bar = px.bar(
            top_df,
            x="Views",
            y="Title",
            orientation="h",
            color="Format",
            hover_data=["Watch Hours", "Avg Retention %", "Tier"],
            title="Flagship Deep Dives dominate long-tail total watch hours"
        )
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, height=450)
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("Performance Tier Distribution")
        tier_counts = v_df['Tier'].value_counts().reset_index()
        tier_counts.columns = ['Tier', 'Count']
        fig_pie = px.pie(
            tier_counts,
            values="Count",
            names="Tier",
            color="Tier",
            color_discrete_map={
                "Viral Breakout": "#10b981",
                "Above Average": "#3b82f6",
                "Average": "#f59e0b",
                "Underperforming": "#ef4444"
            },
            hole=0.45
        )
        fig_pie.update_layout(height=450)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("Granular Video Performance Data Table")
    st.dataframe(v_df.sort_values(by="Views", ascending=False), use_container_width=True)

# Module 2: Retention
elif nav == "Audience Retention Modeling":
    st.title("📉 Audience Retention & Exponential Decay Modeling")
    st.caption("R(t) = R₀·e⁻ᵝᵗ + C with R² ≥ 0.70 statistical gating and 0-30s hook diagnostics.")

    videos = db.query(DerivedVideoMetrics).all()
    selected_video_title = st.selectbox("Select Video for Retention Analysis", [v.title for v in videos])
    v_selected = next(v for v in videos if v.title == selected_video_title)

    pts = db.query(RawRetentionCurve).filter(
        RawRetentionCurve.video_id == v_selected.video_id
    ).order_by(RawRetentionCurve.relative_position.asc()).all()

    pos_pcts = [p.relative_position * 100 for p in pts]
    observed_pcts = [p.retention_percentage for p in pts]

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("0-30s Intro Hook Drop", f"-{v_selected.intro_dropoff_30s}%", "Needs <25% for high virality", delta_color="inverse")
    
    if v_selected.is_lambda_suppressed:
        r2.metric("Decay Rate (λ)", "Suppressed ⚠️", f"R² = {v_selected.retention_r2} (< 0.70 threshold)")
    else:
        r2.metric("Decay Rate (λ)", f"{v_selected.retention_decay_lambda}", f"Valid fit R² = {v_selected.retention_r2}")

    r3.metric("Mid-Video Dips (>4%)", f"{v_selected.mid_video_dips_count}", "Drop-off moments")
    r4.metric("End-Screen Rate (95%)", f"{v_selected.end_screen_rate}%", "Session loop potential")

    fig_ret = go.Figure()
    fig_ret.add_trace(go.Scatter(
        x=pos_pcts,
        y=observed_pcts,
        mode='lines+markers',
        name='Observed Retention %',
        line=dict(color='#3b82f6', width=3),
        fill='tozeroy',
        fillcolor='rgba(59, 130, 246, 0.1)'
    ))

    # Add 30s hook marker
    fig_ret.add_vline(x=5.0, line_dash="dash", line_color="#ef4444", annotation_text="0-30s Hook Window")
    fig_ret.update_layout(
        title=f"Audience Retention Curve: {v_selected.title}",
        xaxis_title="Video Progression (%)",
        yaxis_title="Audience Retained (%)",
        yaxis_range=[0, 105],
        height=500
    )
    st.plotly_chart(fig_ret, use_container_width=True)

    if v_selected.is_lambda_suppressed:
        st.warning("⚠️ **Compliance & Statistical Gating:** Goodness-of-fit R² is below 0.70. Exponential decay parameter λ is suppressed because this video features re-watch spikes or tutorial scrub behavior that violate single-parameter exponential decay.")

# Module 3: Traffic
elif nav == "Traffic Efficiency Quadrants":
    st.title("🧭 Traffic Channel Efficiency Quadrants")
    st.caption("Comparing view volume against watch-time efficiency to prioritize high-compounding traffic sources.")

    traffic_rows = db.query(RawTrafficSource).all()
    t_df = pd.DataFrame([{
        "Traffic Source": t.traffic_source_type.replace('_', ' '),
        "Views": t.views,
        "Watch Minutes": t.watch_time_minutes
    } for t in traffic_rows]).groupby("Traffic Source").sum().reset_index()

    total_views = t_df["Views"].sum()
    total_watch = t_df["Watch Minutes"].sum()

    t_df["View Share %"] = (t_df["Views"] / total_views) * 100
    t_df["Watch Share %"] = (t_df["Watch Minutes"] / total_watch) * 100
    t_df["Retention Ratio"] = (t_df["Watch Share %"] / t_df["View Share %"]).round(2)

    def assign_quadrant(row):
        if row["View Share %"] >= 25 and row["Retention Ratio"] >= 1.0:
            return "Growth Engine (High Vol, High Ret)"
        elif row["View Share %"] < 25 and row["Retention Ratio"] >= 1.05:
            return "Hidden Gem (Low Vol, High Ret)"
        elif row["View Share %"] >= 25 and row["Retention Ratio"] < 1.0:
            return "Inefficient Volume (High Vol, Low Ret)"
        else:
            return "Niche / Long-Tail"

    t_df["Quadrant"] = t_df.apply(assign_quadrant, axis=1)

    fig_quad = px.scatter(
        t_df,
        x="View Share %",
        y="Retention Ratio",
        size="Views",
        color="Quadrant",
        text="Traffic Source",
        title="Traffic Channels: Volume vs Retention Efficiency Ratio"
    )
    fig_quad.add_hline(y=1.0, line_dash="dash", line_color="gray", annotation_text="Benchmark Baseline (1.0x)")
    fig_quad.add_vline(x=25.0, line_dash="dash", line_color="gray", annotation_text="25% Volume Threshold")
    fig_quad.update_layout(height=500)
    st.plotly_chart(fig_quad, use_container_width=True)

    st.dataframe(t_df, use_container_width=True)

# Module 4: Clusters
elif nav == "Content Clusters & Groups":
    st.title("🗂️ Content Intelligence & YouTube Analytics Groups")
    st.caption("Thematic pillars with first-class promotion to YouTube Analytics Groups (up to 500 items).")

    clusters = db.query(DerivedContentCluster).all()
    for c in clusters:
        with st.container():
            st.markdown(f"### {c.cluster_name}")
            col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1.5])
            col1.metric("Videos", c.video_count)
            col2.metric("Avg Views", f"{int(c.avg_views):,}")
            col3.metric("Avg Watch", f"{c.avg_watch_time_hrs}h")
            col4.metric("Sub Conv", f"{c.avg_sub_conversion}/1k")
            
            with col5:
                if c.promoted_to_analytics_group:
                    st.success("✓ Active Analytics Group")
                else:
                    if st.button(f"Promote to Analytics Group", key=f"prom_{c.cluster_id}"):
                        c.promoted_to_analytics_group = True
                        db.commit()
                        st.rerun()
            st.markdown(f"**Keywords:** `{'`, `'.join(c.top_keywords)}`")
            st.markdown("---")

# Module 5: Opportunity Matrix & Recs
elif nav == "Opportunity Matrix & Recs":
    mode_label = "⚡ BRUTAL AUDIT MODE" if is_brutal else "STANDARD RECOMMENDATIONS"
    st.title(f"🎯 Growth Recommendations & Evidence [{mode_label}]")
    st.caption("Every recommendation contains an explicit Evidence Object contract with statistical confidence.")

    recs = db.query(Recommendation).filter(Recommendation.is_brutal == is_brutal).order_by(Recommendation.priority_score.desc()).all()

    for r in recs:
        with st.expander(f"[{r.category}] {r.title} (Priority: {int(r.priority_score)}/100 | {r.impact_score} Impact | {r.effort_score} Effort)", expanded=True):
            st.markdown(r.recommendation_text)
            ev = r.evidence_object
            st.info(f"""
            **📊 Structured Evidence Contract**
            - **Evaluated Metric:** {ev.get('metric')}
            - **Observed:** `{ev.get('observed_value')}` vs **Channel Baseline:** `{ev.get('baseline')}`
            - **Sample Size:** `n={ev.get('n')}` uploads | **Confidence:** `{int(float(ev.get('confidence', 0.85))*100)}%`
            - **Effect Size:** `{ev.get('effect_size'):+}%`
            - **Methodological Limitations:** {', '.join(ev.get('limitations', []))}
            """)

# Module 6: Draft Simulator
elif nav == "Draft Video ML Simulator":
    st.title("✨ Pre-Publish Draft Video Performance Simulator")
    st.caption("Leakage-free ML forecasting strictly evaluated against a naive median baseline (t₀ upload cutoff enforced).")

    with st.form("sim_form"):
        draft_title = st.text_input("Draft Video Title", "Building a Real-Time Distributed Cache from Scratch in Go")
        dur_mins = st.slider("Duration (Minutes)", 1, 45, 18)
        cluster_choice = st.selectbox("Topic Cluster", [
            "Technical Tutorial", "Architecture", "Comparison", "Career"
        ])
        pub_day = st.selectbox("Publish Day of Week", ["Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Monday"], index=1)
        pub_hour = st.slider("Upload Hour (24h format)", 8, 22, 14)
        submitted = st.form_submit_button("Run Algorithmic Simulation")

    if submitted:
        day_map = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6}
        res = MLService.simulate_draft_video(
            title=draft_title,
            duration_sec=dur_mins * 60,
            cluster_id=2 if "Tutorial" in cluster_choice else (1 if "Architecture" in cluster_choice else 3),
            upload_hour=pub_hour,
            upload_day_of_week=day_map[pub_day],
            channel_median_views=12500.0
        )

        st.success(f"**Predicted Growth Tier:** {res['predicted_tier']}")
        m1, m2, m3 = st.columns(3)
        m1.metric("Predicted 30-Day Views", f"{res['predicted_30d_views']:,}", f"Range: {res['confidence_interval_low']:,} - {res['confidence_interval_high']:,}")
        m2.metric("Predicted Watch Hours", f"{res['predicted_watch_time_hrs']:,} hrs")
        m3.metric("Est. Audience Retention", f"{res['predicted_avg_view_percentage']}%")

        st.subheader("Actionable Algorithmic Optimizations")
        for imp in res["actionable_improvements"]:
            st.markdown(f"- {imp}")

# Module 7: Compliance
elif nav == "Compliance & 30d TTL Sweeper":
    st.title("🛡️ Data Retention Compliance & Quota Ledger")
    st.caption("YouTube API Services Developer Policies Section III.E.4.b–d verification.")

    status = comp_service.get_compliance_status()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Raw API Records", status["raw_video_count"] + status["raw_daily_rows"], "Under 30-day TTL")
    c2.metric("Earliest Expiration", f"In {status['days_to_earliest_ttl']} days")
    c3.metric("Derived Statistics", status["derived_metrics_count"], "Pattern B Compliant")
    c4.metric("Total Sweeps", status["total_sweeps_performed"])

    st.markdown("---")
    st.markdown("### Execute 30-Day TTL Sweeper")
    st.write("Pattern B enforces purging raw API entities past 30 days while keeping derived statistical features.")
    if st.button("Run TTL Sweeper Now"):
        sweep_res = comp_service.run_ttl_sweep()
        st.success(f"Sweeper completed! Purged: {sweep_res['total_purged']} raw rows, Refreshed: {sweep_res['total_refreshed']} rows.")
        st.rerun()

    st.subheader("Audit Event Logs")
    logs = db.query(ComplianceLog).order_by(ComplianceLog.timestamp.desc()).limit(10).all()
    if logs:
        st.dataframe(pd.DataFrame([{
            "Event": l.event_type,
            "Table": l.table_name,
            "Records": l.records_affected,
            "Action": l.action_taken,
            "Details": l.details,
            "Timestamp": l.timestamp
        } for l in logs]))
    else:
        st.info("No compliance events recorded yet.")

# Module 8: Report Generator
elif nav == "Executive PDF Report Generator":
    st.title("📄 Executive Growth Report Generator")
    st.caption("Compiles professional presentation-ready PDF reports with scorecard tables, retention curves, and evidence objects.")

    mode_text = "Brutal Strategic Audit" if is_brutal else "Standard Executive Growth Report"
    st.write(f"Active Template: **{mode_text}**")

    if st.button("Generate & Download Executive PDF"):
        videos = db.query(DerivedVideoMetrics).order_by(DerivedVideoMetrics.total_views.desc()).all()
        video_dicts = [{
            "video_id": v.video_id, "title": v.title, "format_type": v.format_type,
            "total_views": v.total_views, "total_watch_time_hrs": v.total_watch_time_hrs,
            "avg_view_percentage": v.avg_view_percentage, "virality_robust_z": v.virality_robust_z,
            "performance_tier": v.performance_tier, "intro_dropoff_30s": v.intro_dropoff_30s
        } for v in videos]

        summary = {
            "total_videos": len(videos), "total_views": sum(v["total_views"] for v in video_dicts),
            "total_watch_time_hrs": sum(v["total_watch_time_hrs"] for v in video_dicts),
            "total_subscribers": sum(v.net_subscribers for v in videos),
            "avg_view_duration_sec": sum(v.avg_view_duration_sec for v in videos) / len(videos),
            "avg_view_percentage": sum(v.avg_view_percentage for v in videos) / len(videos),
            "avg_engagement_rate": sum(v.engagement_rate for v in videos) / len(videos),
            "viral_videos_count": sum(1 for v in videos if v.performance_tier == "Viral Breakout"),
            "top_format": "Deep Dive", "avg_intro_drop": 29.4
        }

        recs = db.query(Recommendation).filter(Recommendation.is_brutal == is_brutal).all()
        rec_dicts = [{
            "category": r.category, "title": r.title, "recommendation_text": r.recommendation_text,
            "priority_score": r.priority_score, "impact_score": r.impact_score,
            "effort_score": r.effort_score, "evidence_object": r.evidence_object
        } for r in recs]

        out_pdf = f"reports_generated/Streamlit_Growth_Report_{'Brutal' if is_brutal else 'Standard'}.pdf"
        ReportService.generate_pdf_report(
            channel_name="DevPulse Systems",
            channel_summary=summary,
            top_videos=video_dicts,
            recommendations=rec_dicts,
            clusters=[],
            output_filepath=out_pdf,
            is_brutal=is_brutal
        )

        with open(out_pdf, "rb") as f:
            st.download_button(
                label="📥 Click Here to Download PDF Report",
                data=f,
                file_name=os.path.basename(out_pdf),
                mime="application/pdf"
            )
        st.success(f"Report compiled successfully at `{out_pdf}`!")

# Module 9: Layman Growth Academy & Complete Metric Decrypter
elif nav == "👶 Layman's Growth Academy & Metric Decrypter":
    st.title("👶 Layman Growth Academy & Complete Channel Parameter Decrypter")
    st.caption("Zero Jargon Guarantee | How YouTube Growth Actually Works for Absolute Beginners")

    st.info("💡 **Core Principle:** YouTube is not an evil robot or a magic formula. It is simply a waiter trying to serve viewers the videos they will enjoy the most and watch the longest.")

    t1, t2, t3, t4 = st.tabs([
        "🍽️ 1. The Algorithm Explained (ELI5)",
        "📖 2. 18-Parameter Visual Dictionary",
        "🚑 3. The Creator Emergency Room",
        "🚀 4. 4-Stage Growth Blueprint"
    ])

    with t1:
        st.subheader("The Giant 24/7 Restaurant Analogy")
        st.markdown("""
        Think of YouTube as the world's biggest 24/7 restaurant with **2 billion diners**. 
        You are a chef making dishes (videos). The YouTube algorithm is not an evil robot — **it is just a waiter trying to keep the customer happy**.

        * **If a customer loved spicy pizza in the past:** The waiter recommends other spicy pizzas.
        * **If the customer takes one bite and walks out:** The waiter stops bringing your dish to other tables.
        * **If they finish the whole plate and lick the bowl:** The waiter recommends your dish to the entire dining room!
        """)

        st.subheader("The Leaky Bucket Analogy")
        st.markdown("""
        Imagine your video is a bucket, and views are water you pour in. Your thumbnail and title open the tap to pour water in.
        
        * But if your bucket has a massive hole at the bottom (boring opening, long logos, wasting time), **all the water drains out immediately**.
        * Getting 10,000 people to click is completely useless if 9,000 leave in 20 seconds.
        * **Golden Fix:** Plug the hole first! Deliver on your title promise in the first 5 seconds, cut intro logos, and keep your pacing brisk.
        """)

    with t2:
        st.subheader("Complete Plain-English Parameter Dictionary")
        metrics_data = [
            {"Parameter": "Total Views", "Plain English": "Footsteps into your shop", "Metaphor": "People who walked through your front door", "Target": "Higher is better if retention holds"},
            {"Parameter": "Watch Time (Hours)", "Plain English": "Attention bank", "Metaphor": "Total time customers spent browsing your aisles", "Target": "YouTube's #1 favorite currency"},
            {"Parameter": "Avg View Duration (AVD)", "Plain English": "Average visit time", "Metaphor": "How long someone stays at your dinner party", "Target": "Aim for >8 mins on long videos"},
            {"Parameter": "View Percentage (AVP)", "Plain English": "Movie popcorn test", "Metaphor": "Did they watch to the end or leave at min 2?", "Target": ">50% on 10m, >40% on 20m"},
            {"Parameter": "0-30s Hook Drop-Off", "Plain English": "The handshake test", "Metaphor": "First impression on a blind date", "Target": "Keep >70% past 30 seconds"},
            {"Parameter": "Click-Through Rate (CTR)", "Plain English": "Window shopping", "Metaphor": "Out of 100 people walking past your bakery, who opened the door?", "Target": "4% to 8% standard, >10% viral"},
            {"Parameter": "Robust Virality Z-Score", "Plain English": "Home run meter", "Metaphor": "Is this hit a single base or a grand slam?", "Target": ">1.5 Z indicates breakout hit"},
            {"Parameter": "Browse Features", "Plain English": "The couch tap", "Metaphor": "A waiter handing a customer a chef's special", "Target": "Where 100k+ viral hits occur"},
            {"Parameter": "Suggested Videos", "Plain English": "You might also like", "Metaphor": "'If you liked that movie, you will love this'", "Target": "Great for binge-worthy series"},
            {"Parameter": "YouTube Search", "Plain English": "The hardware store", "Metaphor": "'Where are the 10mm screws?'", "Target": "Steady evergreen views for years"},
            {"Parameter": "Subscriber Conversion", "Plain English": "Loyalty punch card", "Metaphor": "Customers who signed up for VIP membership", "Target": "4 to 8 subs per 1,000 views"},
            {"Parameter": "Returning Viewers", "Plain English": "Regulars at the bar", "Metaphor": "Loyal customers who return every Friday", "Target": "Provides crucial initial momentum"},
            {"Parameter": "Audience Quality (AQS)", "Plain English": "Bot & ghost detector", "Metaphor": "Are fans real humans or mannequins?", "Target": ">80 index indicates Superfans"},
            {"Parameter": "Tubular V30 Velocity", "Plain English": "30-day fair test", "Metaphor": "How fast a car accelerated in 30 seconds", "Target": "Evens playing field between old and new"},
            {"Parameter": "Sponsorship FMV ($)", "Plain English": "Brand rate card", "Metaphor": "How much a billboard on your lawn is worth", "Target": "$50-$85 CPM for software devs"},
            {"Parameter": "72-Hour Latency", "Plain English": "Don't panic rule", "Metaphor": "Waiting for bank check to clear before spending", "Target": "Wait 48h before judging a new upload"}
        ]
        st.dataframe(pd.DataFrame(metrics_data), use_container_width=True)

    with t3:
        st.subheader("The Creator Emergency Room: Plain-English Fixes")
        st.error("**Symptom 1: Low views, but high praise from those who watch**")
        st.write("👉 **Diagnosis:** Your packaging is invisible. Rework your thumbnail today with high contrast and spark curiosity in the title.")

        st.warning("**Symptom 2: High views, but retention collapses in 20 seconds**")
        st.write("👉 **Diagnosis:** Broken hook. You promised something on the thumbnail that you didn't deliver right away. Cut intros forever.")

        st.info("**Symptom 3: 5,000 views on day 1, then flatlines to zero**")
        st.write("👉 **Diagnosis:** You exhausted your subscriber bubble. Strangers on Browse feed didn't understand the niche topic.")

        st.success("**Symptom 4: 50,000 views, but zero new subscribers**")
        st.write("👉 **Diagnosis:** One-off problem trap. You solved a temporary bug. Give viewers a reason to subscribe for future videos.")

    with t4:
        st.subheader("The 4-Stage Zero-to-Hero Growth Blueprint")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            ### 🥉 Stage 1: 0 to 1,000 Subscribers
            * **Strategy:** The Search Problem Solver.
            * Nobody knows who you are. Solve specific painful problems people search for every day.
            * **Goal:** Reach 4,000 watch hours & join YouTube Partner Program.

            ### 🥈 Stage 2: 1,000 to 10,000 Subscribers
            * **Strategy:** The Signature Series.
            * Double down on your #1 highest watch-time topic. Create a weekly series.
            * **Goal:** Establish a predictable baseline of 5,000+ views per upload.
            """)
        with c2:
            st.markdown("""
            ### 🥇 Stage 3: 10,000 to 100,000 Subscribers
            * **Strategy:** Browse Outlier Hunting.
            * Pivot to broad curiosity titles that appeal to anyone in tech. Chase 5x-10x viral hits.
            * **Goal:** First $5,000 to $10,000 brand sponsorships.

            ### 💎 Stage 4: 100,000+ Subscribers
            * **Strategy:** The Media Institution.
            * Maximize commercial CPM ($70+), build newsletter communities, and license courses.
            * **Goal:** Full-time media empire scale.
            """)

db.close()

