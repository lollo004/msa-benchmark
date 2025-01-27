# Bioinformatics MSA Algorithm Comparison
Here, you can find details about the code. For more details, refer to the Research Project's paper.

## The Repository contains:
- outputs: MSA alignements calculated by different algorithms.
- scores: Total evaluation of result and execution resources for each algorithm.
- csv: All tuples scores collected from execution time.
- run_benchmark.py: Script to run locally benchmark (Requires all binaries installed - do not try to run locally!).
- Dockerfile: Docker enviroment used for testing. Ubuntu system.

## Process:
1. We downloaded all the MSA algorithms official implementations.
2. We downloaded BaliBASE4 from the official website.
3. We read documentations and understood how to tweak the behavior of each executable (number of threads, input formats, output formats, etc.).
4. We developed a the python script along with the graph drawer script.
5. We reduced the BaliBASE full dimension to an accessible number of input sequences for benchmarking on our hardware.
6. We ran the benchmark.

### About the run_benchmark python script:
We used BioPython to evaluated the score of each alignement produced by algorithms.
Each algorithm is been executed on 16 threads on a Ubuntu Linux system docker container.
This script was responsible of the entire benchmark pipeline: Run script, measuring time and memory usage, score evaluation and data accounting.

### About the draw_chart python script:
We plotted all results on 4 different charts showing across algorithms: Memory Usage, Time, SP score, TC score.
Finally, we normalized data and plotted it on a Radio Chart.
