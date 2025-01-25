import os
import subprocess
import time
import psutil
from pathlib import Path
from Bio import AlignIO
from itertools import combinations
import json
import csv

# Configurazione di base
BALI_BASE_DIR = "BaliBASE_reduced"
OUTPUT_DIR = "outputs"
BINARIES_DIR = "binaries"
SCORES_DIR = "scores"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SCORES_DIR, exist_ok=True)

def monitor_resources_and_execute(command):
    """Esegue un comando e monitora tempo e memoria durante l'esecuzione."""
    start_time = time.time()
    process = psutil.Popen(command, shell=True)
    max_memory = process.memory_info().rss / (1024 * 1024) # Convert to MB
    polling_interval=0.01 # 10 ms    
    while "someProgram" in (p.name() for p in psutil.process_iter()):
        try:
            time.sleep(polling_interval)
            max_memory = max(process.memory_info().rss / (1024 * 1024), max_memory)
        except psutil.NoSuchProcess:
            break            
    process.wait()
    end_time = time.time()
    execution_time = end_time - start_time

    return execution_time, max_memory

def calculate_sp_score(alignment):
    """Calcola il punteggio Sum-of-Pairs (SP)."""
    sp_score = 0
    num_columns = alignment.get_alignment_length()
    for col_idx in range(num_columns):
        column = alignment[:, col_idx]
        for seq1, seq2 in combinations(column, 2):
            if seq1 == seq2:
                sp_score += 1
    return sp_score

def calculate_tc_score(alignment):
    """Calcola il punteggio Total Column (TC)."""
    tc_score = 0
    num_columns = alignment.get_alignment_length()
    for col_idx in range(num_columns):
        column = alignment[:, col_idx]
        if len(set(column)) == 1:
            tc_score += 1
    return tc_score

def analyze_alignment(output_file, format="fasta"):
    """Analizza l'allineamento e calcola SP e TC."""
    alignment = AlignIO.read(output_file, format)
    sp_score = calculate_sp_score(alignment)
    tc_score = calculate_tc_score(alignment)
    return sp_score, tc_score

def benchmark_algorithm(algorithm_name, command_template):
    """Esegue i benchmark per tutti i file .tfa in BaliBASE."""
    results = []
    total_sp_score = 0
    total_tc_score = 0
    total_time = 0
    total_memory = 0
    file_count = 0

    # Processa ogni file .tfa nella directory BaliBASE
    for tfa_file in Path(BALI_BASE_DIR).glob("*.tfa"):
        filename = tfa_file.stem
        output_file = f"{filename}_{algorithm_name}"

        # Sostituzione dinamica dei segnaposto nel comando
        if algorithm_name == "pasta":
            command = command_template.format(
                inputs=BALI_BASE_DIR,
                outputs=OUTPUT_DIR,
                input_file=f"{filename}.tfa"    
            )
        else:
            command = command_template.format(
                binaries=BINARIES_DIR,
                inputs=BALI_BASE_DIR,
                outputs=OUTPUT_DIR,
                output_file=output_file,
                input_file=f"{filename}.tfa"       
            )
            
        print(f"Executing: {command}")
        execution_time, max_memory = monitor_resources_and_execute(command)

        format = "fasta"
        # Tool doesn't provide output alignement file rename - manually
        if algorithm_name == "pasta": 
            process = psutil.Popen(f"mv {OUTPUT_DIR}/pastajob.marker001.{filename}.tfa.aln {OUTPUT_DIR}/{filename}_pasta", shell=True)
            process.wait()
            process = psutil.Popen(f"rm {OUTPUT_DIR}/past*", shell=True)
            process.wait()
        elif algorithm_name == "tcoffee":
            format = "clustal"
            process = psutil.Popen("rm *.dnd", shell=True)
            process.wait()
        
        # Analizza i punteggi SP e TC
        sp_score, tc_score = analyze_alignment(f"{OUTPUT_DIR}/{output_file}", format)

        # Accumula i totali
        total_sp_score += sp_score
        total_tc_score += tc_score
        total_time += execution_time
        total_memory += max_memory
        file_count += 1

        # Salva i risultati del singolo file
        result = {
            "file": filename,
            "execution_time": execution_time,
            "memory_usage": max_memory,
            "sp_score": sp_score,
            "tc_score": tc_score
        }
        results.append(result)

        print(f"Completato: {filename} | Tempo: {execution_time:.2f}s | Memoria: {max_memory:.2f}MB")
        print(f"SP Score: {sp_score} | TC Score: {tc_score}\n")

        # Salva i punteggi medi in un file JSON
    totals = {
        "algorithm": algorithm_name,
        "sp_score": total_sp_score,
        "tc_score": total_tc_score,
        "execution_time": total_time,
        "usage_memory": total_memory
    }
    json_path = Path(SCORES_DIR) / f"{algorithm_name}.json"
    with open(json_path, "w") as json_file:
        json.dump(totals, json_file, indent=4)

    print(f"Total scored written in: {json_path}")
    return results

def save_results(results, output_csv="benchmark_results.csv"):
    """Salva i risultati in un file CSV."""
    with open(output_csv, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"Risultati salvati in: {output_csv}")

if __name__ == "__main__":
    
    results_mafft = benchmark_algorithm(
        algorithm_name="mafft",
        command_template="mafft --thread 12 {inputs}/{input_file} > {outputs}/{output_file}"
    )    
    
    results_tcoffee = benchmark_algorithm(
        algorithm_name="tcoffee",
        command_template="sources/t_coffee/bin/t_coffee -thread 12 -output clustalw -outfile {output_file} -seq {inputs}/{input_file} -outfile {outputs}/{output_file}"
    )
    
    results_pasta = benchmark_algorithm(
        algorithm_name="pasta",
        command_template="python3 sources/pasta/run_pasta.py --auto -i {inputs}/{input_file} -o {outputs} --datatype=protein"
    )

    results_clustalw = benchmark_algorithm(
        algorithm_name="clustalw2",
        command_template="{binaries}/clustalw2 -OUTFILE={outputs}/{output_file} -QUIET -INFILE={inputs}/{input_file} -OUTPUT=FASTA"
    )
    save_results(results_clustalw, output_csv="clustalw_benchmark_results.csv")

    results_famsa = benchmark_algorithm(
        algorithm_name="famsa",
        command_template="{binaries}/famsa {inputs}/{input_file} {outputs}/{output_file}"
    )

    results_muscle = benchmark_algorithm(
        algorithm_name="muscle5",
        command_tamplate="{binaries}/muscle5 -align {inputs}/{input_file} -output {outputs}/{output_file}"
    )

       
    save_results(results_famsa, output_csv="famsa_benchmark_results.csv")
