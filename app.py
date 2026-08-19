import streamlit as st
from datetime import date, time
from config import SUPPORTED_CITIES, DEFAULT_AMBULANCE_COUNT, MAX_AMBULANCE_COUNT, ANALYSIS_MODES
from demand import create_demo_records, build_demand_zones, predict_demand
from services import get_city_coordinates, get_weather, get_osm_facilities, get_route_time
from optimization import build_distance_matrix, greedy_optimize, evaluate_deployment
from quantum_engine import quantum_optimize
from map import create_map

st.set_page_config(page_title="PulseGrid", page_icon="", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
html,body,[class*="css"]{font-family:Inter,sans-serif}.stApp{background:#07111f;color:#f4f7fb}.block-container{max-width:1450px;padding:1.5rem 1rem 3rem}header[data-testid="stHeader"],[data-testid="stSidebar"]{background:transparent}[data-testid="stSidebar"]{display:none}
.topbar{display:flex;justify-content:space-between;align-items:center;padding:.4rem 0 1.8rem;border-bottom:1px solid #1c2a3c;margin-bottom:2.2rem}.brand,.hero-title,.section-title,.panel-title,.metric-value,.map-placeholder-title{font-family:"Space Grotesk",sans-serif}.brand{font-size:1.45rem;font-weight:700;letter-spacing:.08em;color:#fff}.brand-subtitle{color:#7f91a8;font-size:.78rem;margin-left:.7rem}.live-status{color:#9aabbe;font-size:.8rem}.live-dot{width:8px;height:8px;border-radius:50%;background:#28d17c;display:inline-block;margin-right:.45rem}
.hero{padding:1rem 0 2rem}.hero-label{color:#ff5b5b;font-size:.78rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase}.hero-title{font-size:clamp(2.4rem,5vw,4.5rem);line-height:.98;font-weight:700;letter-spacing:-.045em;margin:.7rem 0;color:#fff}.hero-text{max-width:720px;color:#9eafc3;font-size:1rem;line-height:1.7}
.section-title{font-size:1.35rem;font-weight:600;color:#fff;margin-bottom:.3rem}.section-text{color:#8293a8;font-size:.88rem;margin-bottom:1.2rem}.panel,.metric-box{background:#0d1929;border:1px solid #1d2c40;border-radius:16px;padding:1.25rem}.panel{height:100%}.panel-title{color:#fff;font-size:1rem;font-weight:600;margin-bottom:.75rem}.metric-box{min-height:105px}.metric-label{color:#8192a8;font-size:.74rem;text-transform:uppercase;letter-spacing:.08em}.metric-value{color:#fff;font-size:1.65rem;font-weight:600;margin-top:.4rem}.metric-description{color:#71839a;font-size:.75rem;margin-top:.2rem}.info-banner{background:#101f32;border:1px solid #20344b;border-left:3px solid #ff5b5b;border-radius:10px;padding:.9rem 1rem;color:#a7b6c8;font-size:.84rem;line-height:1.6;margin:1rem 0}.status-row{display:flex;justify-content:space-between;padding:.65rem 0;border-bottom:1px solid #1a293b;color:#9aabbe;font-size:.83rem}.status-row:last-child{border:0}.ready{color:#28d17c;font-weight:600}.pending{color:#f0b44d;font-weight:600}
div.stButton>button{background:#e84c4c;color:#fff;border:0;border-radius:9px;min-height:2.8rem;font-weight:600}div.stButton>button:hover{background:#ff5b5b;color:#fff}div.stButton>button:focus{box-shadow:0 0 0 2px #07111f,0 0 0 4px #ff5b5b}.stSelectbox label,.stNumberInput label,.stDateInput label,.stTimeInput label,.stFileUploader label{color:#a9b8c9!important;font-size:.82rem!important}.stSelectbox div[data-baseweb="select"]>div,input{background:#101d2d!important;color:#fff!important;border-color:#26384d!important;border-radius:9px!important}.stTabs [data-baseweb="tab-list"]{gap:1.5rem;border-bottom:1px solid #1c2a3c}.stTabs [data-baseweb="tab"]{color:#7f91a8;background:transparent;border:0}.stTabs [aria-selected="true"]{color:#fff}.footer{border-top:1px solid #1c2a3c;margin-top:3rem;padding-top:1.2rem;color:#63758b;font-size:.72rem;text-align:center}
</style>""", unsafe_allow_html=True)

def metric(label,value,desc):
    st.markdown(f'<div class="metric-box"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-description">{desc}</div></div>',unsafe_allow_html=True)

def status(label,value,ok=False):
    st.markdown(f'<div class="status-row"><span>{label}</span><span class="{"ready" if ok else "pending"}">{value}</span></div>',unsafe_allow_html=True)

def panel(title,rows):
    st.markdown(f'<div class="panel"><div class="panel-title">{title}</div>{"".join(f"<div class=\"status-row\"><span>{a}</span><span class=\"{'ready' if b else 'pending'}\">{c}</span></div>" for a,c,b in rows)}</div>',unsafe_allow_html=True)

st.markdown('<div class="topbar"><div><span class="brand">PULSEGRID</span><span class="brand-subtitle">EMERGENCY RESOURCE INTELLIGENCE</span></div><div class="live-status"><span class="live-dot"></span>SYSTEM READY</div></div>',unsafe_allow_html=True)
st.markdown('<div class="hero"><div class="hero-label">Emergency Medical Planning</div><h1 class="hero-title">Smarter ambulance<br>positioning.</h1><div class="hero-text">Analyze emergency demand, weather, geography, available resources, and route estimates to determine where ambulances should be positioned for improved predicted coverage and response.</div></div>',unsafe_allow_html=True)

st.markdown('<div class="section-title">Configure analysis</div><div class="section-text">Select the region and conditions you want PulseGrid to analyze.</div>',unsafe_allow_html=True)
c1,c2,c3=st.columns([1.4,1.4,.8],gap="medium")
with c1: city=st.selectbox("Location",list(SUPPORTED_CITIES.keys()),index=0)
with c2: mode=st.selectbox("Analysis conditions",ANALYSIS_MODES if "ANALYSIS_MODES" in globals() else ["Current conditions","Historical conditions","Custom scenario"])
with c3: ambulances=st.number_input("Available ambulances",1,MAX_AMBULANCE_COUNT,DEFAULT_AMBULANCE_COUNT,1)

c1,c2,c3=st.columns([1,1,.8],gap="medium")
with c1: analysis_date=st.date_input("Analysis date",date.today())
with c2: analysis_time=st.time_input("Analysis time",time(12,0))
with c3:
    st.markdown("<div style='height:1.75rem'></div>",unsafe_allow_html=True)
    analyze=st.button("Run PulseGrid analysis",use_container_width=True)

upload=st.file_uploader("Optional EMS CSV",type=["csv"],help="Required columns: timestamp, latitude, longitude. Common aliases are supported.")
demo=st.checkbox("Use simulated demo demand",value=not bool(upload))
st.markdown('<div class="info-banner">PulseGrid prioritizes available live data. Simulated demand is labeled clearly and does not represent real emergency activity.</div>',unsafe_allow_html=True)

if analyze:
    st.session_state["analysis_started"]=True
    result={}
    errors=[]

    try:
        coords=get_city_coordinates(city)
        result["coords"]=coords
    except Exception as e:
        errors.append(f"Location data unavailable: {e}")

    weather=None
    if result.get("coords"):
        try: weather=get_weather(*result["coords"])
        except Exception as e: errors.append(f"Weather unavailable: {e}")
    result["weather"]=weather

    facilities={}
    if result.get("coords"):
        try: facilities=get_osm_facilities(*result["coords"])
        except Exception as e: errors.append(f"OpenStreetMap data unavailable: {e}")

    try:
        if upload is not None and not demo:
            import pandas as pd
            records=pd.read_csv(upload)
        else:
            records=create_demo_records(city,result.get("coords"))
        zones=build_demand_zones(records,result.get("coords"))
        zones=predict_demand(zones,weather=weather,mode=mode)
        result["records"],result["zones"]=records,zones
    except Exception as e:
        errors.append(f"Demand processing failed: {e}")
        zones=None

    selected_classical=[]
    selected_quantum=[]
    distance_matrix=None

    if zones is not None and facilities:
        try:
            facility_list=facilities.get("ems",facilities.get("facilities",[]))
            distance_matrix=build_distance_matrix(zones,facility_list)
            selected_classical=greedy_optimize(distance_matrix,zones,facility_list,ambulances)
            result["facility_list"]=facility_list
            result["distance_matrix"]=distance_matrix
        except Exception as e:
            errors.append(f"Classical optimization failed: {e}")

        try:
            q=quantum_optimize(zones,result.get("facility_list",[]),ambulances,max_qubits=min(len(result.get("facility_list",[])),12))
            if isinstance(q,dict) and q.get("success") and q.get("selected_facilities"):
                selected_quantum=q["selected_facilities"]
            result["quantum"]=q
        except Exception as e:
            result["quantum"]={"success":False,"error":str(e)}

    deployment=selected_quantum or selected_classical
    result["classical"]=selected_classical
    result["deployment"]=deployment

    route_times={}
    if zones is not None and deployment:
        for f in deployment:
            for i,z in zones.iterrows() if hasattr(zones,"iterrows") else enumerate(zones):
                try:
                    lat=z["latitude"] if isinstance(z,dict) else z.latitude
                    lon=z["longitude"] if isinstance(z,dict) else z.longitude
                    key=(f.get("latitude"),f.get("longitude"),lat,lon) if isinstance(f,dict) else (getattr(f,"latitude",None),getattr(f,"longitude",None),lat,lon)
                    route_times[key]=get_route_time(f,{"latitude":lat,"longitude":lon})
                except Exception:
                    continue

    result["route_times"]=route_times

    try:
        optimized=evaluate_deployment(deployment,zones,route_times)
        baseline=evaluate_deployment(result.get("facility_list",[])[:ambulances],zones,route_times)
        result["optimized_eval"],result["baseline_eval"]=optimized,baseline
    except Exception as e:
        errors.append(f"Deployment evaluation unavailable: {e}")
        result["optimized_eval"],result["baseline_eval"]={},{} 

    st.session_state["pulsegrid"]=result
    st.session_state["pulsegrid_errors"]=errors

data=st.session_state.get("pulsegrid")
errors=st.session_state.get("pulsegrid_errors",[])

if errors:
    for e in errors: st.warning(e)

st.markdown('<div class="section-title">Data readiness</div>',unsafe_allow_html=True)
a,b,c,d=st.columns(4,gap="medium")
with a: panel("Weather",[("Data source","NWS",bool(data and data.get("weather"))),("Live conditions","Available" if data and data.get("weather") else "Unavailable",bool(data and data.get("weather")))])
with b: panel("Traffic / routing",[("Data source","OSRM",bool(data and data.get("route_times"))),("Route estimates","Available" if data and data.get("route_times") else "Pending",bool(data and data.get("route_times")))])
with c: panel("EMS data",[("Historical records","Loaded" if data and data.get("records") is not None else "Pending",bool(data and data.get("records") is not None)),("Geographic data","Processed" if data and data.get("zones") is not None else "Pending",bool(data and data.get("zones") is not None))])
with d: panel("Road / facilities",[("Network data","Loaded" if data and data.get("facility_list") else "Pending",bool(data and data.get("facility_list"))),("Hospitals","Loaded" if data and data.get("coords") else "Pending",bool(data and data.get("coords")))])

st.markdown("<div style='height:2rem'></div>",unsafe_allow_html=True)
map_col,metric_col=st.columns([2.1,1],gap="medium")

with map_col:
    st.markdown('<div class="section-title">Emergency coverage map</div>',unsafe_allow_html=True)
    if data and data.get("coords"):
        try:
            m=create_map(data["coords"],data.get("zones"),data.get("facility_list",[]),data.get("deployment",[]),data.get("classical",[]),data.get("facilities",{}).get("hospitals",[]))
            from streamlit_folium import st_folium
            st_folium(m,use_container_width=True,height=520)
        except Exception as e:
            st.error(f"Map unavailable: {e}")
    else:
        st.markdown('<div class="panel" style="height:520px;display:flex;align-items:center;justify-content:center;text-align:center"><div><div class="map-placeholder-title">Interactive map will appear here</div><div class="map-placeholder-text">Run PulseGrid to display demand zones, EMS facilities, hospitals, and optimized ambulance locations.</div></div></div>',unsafe_allow_html=True)

with metric_col:
    st.markdown('<div class="section-title">Analysis overview</div>',unsafe_allow_html=True)
    opt=data.get("optimized_eval",{}) if data else {}
    base=data.get("baseline_eval",{}) if data else {}
    demand_total=opt.get("total_demand",sum(data["zones"]["predicted_demand"]) if data and data.get("zones") is not None and "predicted_demand" in data["zones"] else None)
    baseline_time=base.get("average_response_time",base.get("weighted_average_response_time"))
    optimized_time=opt.get("average_response_time",opt.get("weighted_average_response_time"))
    improvement=((baseline_time-optimized_time)/baseline_time*100) if baseline_time and optimized_time else None
    metric("Predicted demand",f"{demand_total:.0f}" if isinstance(demand_total,(int,float)) else "--","emergency demand for selected period")
    st.markdown("<div style='height:.7rem'></div>",unsafe_allow_html=True)
    metric("Baseline response",f"{baseline_time:.1f} min" if isinstance(baseline_time,(int,float)) else "--","estimated average response time")
    st.markdown("<div style='height:.7rem'></div>",unsafe_allow_html=True)
    metric("Optimized response",f"{optimized_time:.1f} min" if isinstance(optimized_time,(int,float)) else "--","estimated average response time")
    st.markdown("<div style='height:.7rem'></div>",unsafe_allow_html=True)
    metric("Estimated improvement",f"{improvement:.1f}%" if isinstance(improvement,(int,float)) else "--","baseline compared with optimized")

st.markdown("<div style='height:2rem'></div>",unsafe_allow_html=True)
tab1,tab2,tab3,tab4=st.tabs(["Deployment","Conditions","Why this deployment","Quantum engine"])

with tab1:
    st.markdown('<div class="panel"><div class="panel-title">Baseline vs. optimized deployment</div>',unsafe_allow_html=True)
    if data and data.get("deployment"):
        st.write("Optimized deployment")
        st.dataframe(data["deployment"],use_container_width=True)
        if data.get("classical"):
            st.write("Classical deployment")
            st.dataframe(data["classical"],use_container_width=True)
        if opt.get("coverage_percentage") is not None: st.metric("Demand covered",f'{opt["coverage_percentage"]:.1f}%')
    else: st.write("Run an analysis to see deployment results.")
    st.markdown("</div>",unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="panel"><div class="panel-title">Local conditions</div>',unsafe_allow_html=True)
    if data and data.get("weather"):
        st.json(data["weather"])
    else: st.write("Weather information is unavailable.")
    st.markdown("</div>",unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="panel"><div class="panel-title">Why did PulseGrid choose these locations?</div>',unsafe_allow_html=True)
    if data and data.get("zones") is not None:
        z=data["zones"]
        st.write("Locations are selected using predicted demand and distance from candidate emergency facilities. Higher-demand zones receive greater weight.")
        st.dataframe(z,use_container_width=True)
    else: st.write("Run an analysis to generate the deployment explanation.")
    st.markdown("</div>",unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="panel"><div class="panel-title">Quantum optimization</div>',unsafe_allow_html=True)
    q=data.get("quantum",{}) if data else {}
    if q.get("success"):
        st.success("QAOA completed successfully.")
        st.write(f'Qubits: {q.get("num_qubits","N/A")}')
        st.write(f'Repetitions: {q.get("repetitions","N/A")}')
        st.write(f'Objective value: {q.get("objective_value","N/A")}')
    elif q:
        st.warning(f'QAOA unavailable or unsuccessful: {q.get("error","No feasible quantum result was returned.")}')
        st.write("The classical optimizer remains the fallback.")
    else: st.write("Run an analysis to start the quantum experiment.")
    st.markdown("</div>",unsafe_allow_html=True)

st.markdown('<div class="footer">PulseGrid is a decision-support research prototype. Results are estimates based on available data and do not replace emergency dispatch decisions.</div>',unsafe_allow_html=True)
