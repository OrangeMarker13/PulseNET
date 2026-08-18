import numpy as np

try:
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator
    from qiskit_optimization import QuadraticProgram
    from qiskit_optimization.algorithms import MinimumEigenOptimizer
    from qiskit_algorithms import QAOA
    from qiskit_algorithms.optimizers import COBYLA

    QISKIT_AVAILABLE = True

except ImportError:
    QISKIT_AVAILABLE = False


def create_ambulance_problem(
    cost_matrix,
    ambulance_count
):
    if cost_matrix is None:
        return None

    if cost_matrix.size == 0:
        return None

    demand_count, location_count = cost_matrix.shape

    if ambulance_count > location_count:
        ambulance_count = location_count

    problem = QuadraticProgram(
        name="pulsegrid_ambulance_positioning"
    )

    for location in range(location_count):
        problem.binary_var(
            name=f"x_{location}"
        )

    linear = {}

    for location in range(location_count):
        average_cost = float(
            np.mean(cost_matrix[:, location])
        )

        linear[f"x_{location}"] = average_cost

    problem.minimize(
        linear=linear
    )

    constraint = {}

    for location in range(location_count):
        constraint[f"x_{location}"] = 1

    problem.linear_constraint(
        linear=constraint,
        sense="==",
        rhs=ambulance_count,
        name="ambulance_count"
    )

    return problem


def run_qaoa(
    problem,
    reps=2
):
    if not QISKIT_AVAILABLE:
        return {
            "status": "unavailable",
            "reason": "qiskit dependencies are not installed"
        }

    if problem is None:
        return {
            "status": "error",
            "reason": "optimization problem is empty"
        }

    try:
        simulator = AerSimulator()

        qaoa = QAOA(
            sampler=simulator,
            optimizer=COBYLA(maxiter=100),
            reps=reps
        )

        optimizer = MinimumEigenOptimizer(
            qaoa
        )

        result = optimizer.solve(problem)

        selected_locations = []

        for variable, value in zip(
            result.variables,
            result.x
        ):
            if value > 0.5:
                selected_locations.append(
                    int(variable.name.split("_")[1])
                )

        return {
            "status": "success",
            "selected_locations": selected_locations,
            "objective_value": float(
                result.fval
            ),
            "raw_result": result
        }

    except Exception as error:
        return {
            "status": "error",
            "reason": str(error)
        }


def create_quantum_circuit(
    number_of_qubits
):
    if number_of_qubits <= 0:
        return None

    circuit = QuantumCircuit(
        number_of_qubits
    )

    for qubit in range(number_of_qubits):
        circuit.h(qubit)

    return circuit


def get_quantum_status():
    if QISKIT_AVAILABLE:
        return {
            "available": True,
            "engine": "Qiskit QAOA"
        }

    return {
        "available": False,
        "engine": None
    }
