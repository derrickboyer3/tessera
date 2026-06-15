'''
    Optimization Loop Pass
    ----------------------
    Transpiler pass that runs a specified list of optimization passes in a loop, either for a fixed number
    of iterations or until convergence (no further gate count reduction). This allows for more thorough
    optimization since some passes may enable further optimizations in subsequent passes.

    Operates in two modes:

    Fixed iterations mode (default): runs the specified passes for a set number of iterations.
    Convergence mode: continues to run the passes until no further reduction in gate count is observed
    or until a maximum number of iterations is reached to prevent infinite loops.

    Convergence is detected by comparing instruction count between iterations; passes that rewrite
    the circuit without changing gate count will not trigger further loops.

    Args:
        passes:                  List of TranspilerPass instances to run each iteration
        optimization_iterations: 1 (default) | positive int = fixed iterations | -1 = run until gate count converges
        max_iterations:          Safety cap for convergence mode only (default 1000)
        debug_on:                If True, prints gate counts before and after each inner pass

    Example usage in TesseraTranspiler:
        optimization_passes = [CancelAdjacentPass(), MergeRotationsPass()]
        optimization_loop = OptimizationLoopPass(optimization_passes, optimization_iterations=-1, max_iterations=100)

    This pass should be run after routing and basis translation, and can be used to run multiple
    optimization passes together in a loop.

    Raises:
        ValueError: If optimization_iterations is 0 or less than -1.
        ValueError: If max_iterations is not a positive integer.
'''
from tessera.transpiler_pass import TranspilerPass

def log_before(pass_, circuit):
    print(f"[Tessera] Running pass: {pass_.name} | Gates: {len(circuit.instructions)}")

def log_after(pass_, circuit):
    print(f"[Tessera] Finished pass: {pass_.name} | Gates: {len(circuit.instructions)}")

class OptimizationLoopPass(TranspilerPass):
    def __init__(self, passes, optimization_iterations=1, max_iterations=1000, debug_on=False):
        if optimization_iterations < -1 or optimization_iterations == 0:
            raise ValueError("optimization_iterations must be a positive integer or -1 for convergence mode")
        if max_iterations <= 0:
            raise ValueError("max_iterations must be a positive integer")
        self.passes = passes
        self.optimization_iterations = optimization_iterations
        self.max_iterations = max_iterations
        self.debug_on = debug_on
        self.log_before = log_before
        self.log_after = log_after

    def loop_int(self, circuit):
        for i in range(self.optimization_iterations):
            for pass_ in self.passes:
                if self.debug_on:
                    self.log_before(pass_, circuit)
                circuit = pass_.run(circuit)
                if self.debug_on:
                    self.log_after(pass_, circuit)
        return circuit

    def loop_until_convergence(self, circuit):
        prev_gate_count = len(circuit.instructions) + 1  # Start with a gate count that's guaranteed to be higher than the initial count
        iteration_count = 0
        while True:
            for pass_ in self.passes:
                if self.debug_on:
                    self.log_before(pass_, circuit)
                circuit = pass_.run(circuit)
                if self.debug_on:
                    self.log_after(pass_, circuit)
            current_gate_count = len(circuit.instructions)
            if current_gate_count >= prev_gate_count:  # No improvement, stop the loop
                break
            prev_gate_count = current_gate_count
            iteration_count += 1
            if iteration_count >= self.max_iterations:
                print(f"[Tessera] Reached maximum iterations ({self.max_iterations}) without convergence. Stopping optimization loop.")
                break
        return circuit


    def run(self, circuit):
        if self.optimization_iterations == -1:
            return self.loop_until_convergence(circuit)
        else:
            return self.loop_int(circuit)
