import numpy as np
from config import RESPONSE_THRESHOLD_MINUTES

def _v(x,k,d=None):
    return x.get(k,d) if isinstance(x,dict) else getattr(x,k,d)

def calculate_distance_km(lat1,lon1,lat2,lon2):
    a=np.radians([lat1,lat2]); dlat=np.radians(lat2-lat1); dlon=np.radians(lon2-lon1)
    h=np.sin(dlat/2)**2+np.cos(a[0])*np.cos(a[1])*np.sin(dlon/2)**2
    return float(2*6371*np.arcsin(np.sqrt(np.clip(h,0,1))))

def calculate_distance(lat1,lon1,lat2,lon2):
    return calculate_distance_km(lat1,lon1,lat2,lon2)

def build_distance_matrix(demand_zones,candidate_locations):
    if demand_zones is None or candidate_locations is None or len(demand_zones)==0 or len(candidate_locations)==0:
        return np.empty((0,0))
    zones=demand_zones.to_dict("records") if hasattr(demand_zones,"to_dict") else demand_zones
    return np.array([[calculate_distance_km(_v(z,"latitude"),_v(z,"longitude"),_v(l,"latitude"),_v(l,"longitude")) for l in candidate_locations] for z in zones])

def build_travel_cost_matrix(demand_zones,candidate_locations):
    return build_distance_matrix(demand_zones,candidate_locations)

def greedy_optimize(distance_matrix,demand_zones,candidate_locations,ambulance_count):
    if distance_matrix.size==0 or not candidate_locations or ambulance_count<=0:
        return []
    zones=demand_zones.to_dict("records") if hasattr(demand_zones,"to_dict") else demand_zones
    weights=np.array([max(float(_v(z,"predicted_demand",_v(z,"historical_demand",0))),0) for z in zones])
    selected=[]; remaining=set(range(len(candidate_locations)))
    for _ in range(min(ambulance_count,len(candidate_locations))):
        best=None; score=float("inf")
        for i in remaining:
            nearest=np.min(distance_matrix[:,selected+[i]],axis=1)
            s=float(np.sum(nearest*weights))
            if s<score: score,best=s,i
        if best is None: break
        selected.append(best); remaining.remove(best)
    return [candidate_locations[i] for i in selected]

def calculate_coverage(demand,travel_time,response_threshold=RESPONSE_THRESHOLD_MINUTES):
    return float(demand) if travel_time is not None and travel_time<=response_threshold else 0.0

def evaluate_deployment(deployment,demand_zones,route_times=None,response_threshold=RESPONSE_THRESHOLD_MINUTES):
    if demand_zones is None or len(demand_zones)==0:
        return {"total_demand":0,"covered_demand":0,"coverage_percentage":0,"average_response_time":None}
    zones=demand_zones.to_dict("records") if hasattr(demand_zones,"to_dict") else demand_zones
    total=sum(max(float(_v(z,"predicted_demand",0)),0) for z in zones)
    covered=weighted=0.0; route_times=route_times or {}
    for z in zones:
        demand=max(float(_v(z,"predicted_demand",0)),0); best=None
        for f in deployment or []:
            key=(_v(f,"latitude"),_v(f,"longitude"),_v(z,"latitude"),_v(z,"longitude"))
            value=route_times.get(key)
            if isinstance(value,dict): value=value.get("duration_minutes",value.get("travel_time"))
            try:
                if value is not None:
                    value=float(value); best=value if best is None else min(best,value)
            except (TypeError,ValueError): pass
        if best is not None:
            weighted+=demand*best
            covered+=calculate_coverage(demand,best,response_threshold)
    return {"total_demand":total,"covered_demand":covered,"coverage_percentage":covered/total*100 if total else 0,"average_response_time":weighted/total if total and weighted else None}

def create_optimization_problem(demand_zones,candidate_locations,ambulance_count,response_threshold=RESPONSE_THRESHOLD_MINUTES):
    if demand_zones is None or len(demand_zones)==0 or not candidate_locations or ambulance_count<=0:
        return None
    return {"demand_zones":demand_zones,"candidate_locations":candidate_locations,"ambulance_count":min(ambulance_count,len(candidate_locations)),"response_threshold":response_threshold,"cost_matrix":build_distance_matrix(demand_zones,candidate_locations)}

def calculate_baseline_score(demand_zones,baseline_locations,route_times=None,response_threshold=RESPONSE_THRESHOLD_MINUTES):
    return evaluate_deployment(baseline_locations,demand_zones,route_times,response_threshold)

def calculate_optimized_score(demand_zones,optimized_locations,route_times=None,response_threshold=RESPONSE_THRESHOLD_MINUTES):
    return evaluate_deployment(optimized_locations,demand_zones,route_times,response_threshold)

def compare_deployments(baseline,optimized):
    bt,ot=baseline.get("average_response_time"),optimized.get("average_response_time")
    return {"baseline_coverage":baseline.get("coverage_percentage",0),"optimized_coverage":optimized.get("coverage_percentage",0),"coverage_improvement":optimized.get("coverage_percentage",0)-baseline.get("coverage_percentage",0),"baseline_response_time":bt,"optimized_response_time":ot,"response_time_improvement":((bt-ot)/bt*100) if bt and ot else 0}
