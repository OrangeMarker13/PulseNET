import numpy as np
from config import MAX_QUANTUM_QUBITS, QUANTUM_SHOTS, QUANTUM_REPETITIONS

try:
    from qiskit_optimization import QuadraticProgram
    from qiskit_optimization.algorithms import MinimumEigenOptimizer
    from qiskit_algorithms import QAOA
    from qiskit_algorithms.optimizers import COBYLA
    from qiskit_aer.primitives import SamplerV2
    QISKIT_AVAILABLE=True
except ImportError:
    QISKIT_AVAILABLE=False

def create_ambulance_problem(cost_matrix,ambulance_count,max_qubits=MAX_QUANTUM_QUBITS):
    if cost_matrix is None or np.size(cost_matrix)==0:
        return None,{"status":"error","reason":"empty cost matrix"}
    cost=np.asarray(cost_matrix,dtype=float)
    _,locations=cost.shape
    limit=min(locations,max_qubits)
    count=min(max(1,int(ambulance_count)),limit)
    if limit<1:
        return None,{"status":"error","reason":"no usable facilities"}
    usefulness=1/(1+cost[:,:limit])
    scores=np.sum(usefulness,axis=0)
    problem=QuadraticProgram("pulsegrid_ambulance_positioning")
    for i in range(limit):
        problem.binary_var(f"x_{i}")
    linear={f"x_{i}":-float(scores[i]) for i in range(limit)}
    quadratic={}
    penalty=max(float(np.max(scores)),1.0)*2
    for i in range(limit):
        for j in range(i+1,limit):
            overlap=float(np.sum(np.minimum(usefulness[:,i],usefulness[:,j])))
            quadratic[(f"x_{i}",f"x_{j}")]=overlap*.15+2*penalty
        linear[f"x_{i}"]+=penalty*(1-2*count)
    problem.minimize(linear=linear,quadratic=quadratic)
    problem.linear_constraint(linear={f"x_{i}":1 for i in range(limit)},sense="==",rhs=count,name="ambulance_count")
    return problem,{"status":"ready","qubits":limit,"ambulance_count":count,"candidate_count":locations}

def run_qaoa(problem,reps=QUANTUM_REPETITIONS,shots=QUANTUM_SHOTS):
    if not QISKIT_AVAILABLE:
        return {"status":"unavailable","reason":"Qiskit dependencies are not installed"}
    if problem is None:
        return {"status":"error","reason":"optimization problem is empty"}
    try:
        sampler=SamplerV2(default_shots=shots)
        qaoa=QAOA(sampler=sampler,optimizer=COBYLA(maxiter=50),reps=reps)
        result=MinimumEigenOptimizer(qaoa).solve(problem)
        selected=[i for i,v in enumerate(result.x) if v>.5]
        return {"status":"success","selected_locations":selected,"objective_value":float(result.fval),"qubits":problem.get_num_vars(),"repetitions":reps,"shots":shots} if selected else {"status":"error","reason":"QAOA returned no selected facilities"}
    except Exception as error:
        return {"status":"error","reason":str(error)}

def solve_quantum_deployment(cost_matrix,ambulance_count,max_qubits=MAX_QUANTUM_QUBITS,reps=QUANTUM_REPETITIONS,shots=QUANTUM_SHOTS):
    problem,info=create_ambulance_problem(cost_matrix,ambulance_count,max_qubits)
    if problem is None:return info
    result=run_qaoa(problem,reps,shots)
    result.update({k:v for k,v in info.items() if k not in result})
    return result

def quantum_optimize(cost_matrix,ambulance_count,max_qubits=MAX_QUANTUM_QUBITS,reps=QUANTUM_REPETITIONS,shots=QUANTUM_SHOTS):
    return solve_quantum_deployment(cost_matrix,ambulance_count,max_qubits,reps,shots)

def create_quantum_circuit(number_of_qubits):
    try:
        from qiskit import QuantumCircuit
        if number_of_qubits<=0:return None
        circuit=QuantumCircuit(number_of_qubits)
        circuit.h(range(number_of_qubits))
        return circuit
    except ImportError:
        return None

def get_quantum_status():
    return {"available":QISKIT_AVAILABLE,"engine":"Qiskit QAOA" if QISKIT_AVAILABLE else None,"max_qubits":MAX_QUANTUM_QUBITS,"shots":QUANTUM_SHOTS,"repetitions":QUANTUM_REPETITIONS}
