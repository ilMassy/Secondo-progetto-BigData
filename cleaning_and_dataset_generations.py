import pandas as pd
import re
import shutil
import os

# Directory di base e percorsi file
BASE_DIR = '/home/massimiliano/datasets/US_Used_cars_dataset'
INPUT_RAW_PATH = os.path.join(BASE_DIR, 'used_cars_data.csv')
CLEANED_PATH = os.path.join(BASE_DIR, 'used_cars_data_cleaned.csv')

# Cartelle di output per i due job
JOB1_DIR = os.path.join(BASE_DIR, 'job1')
JOB2_DIR = os.path.join(BASE_DIR, 'job2')
os.makedirs(JOB1_DIR, exist_ok=True)
os.makedirs(JOB2_DIR, exist_ok=True)

# Percorsi file output per job 1
J1_CLEANED = os.path.join(JOB1_DIR, 'used_cars_data_cleaned.csv')
J1_100K = os.path.join(JOB1_DIR, 'used_cars_data_100k.csv')
J1_500K = os.path.join(JOB1_DIR, 'used_cars_data_500k.csv')
J1_1M = os.path.join(JOB1_DIR, 'used_cars_data_1m.csv')
J1_2X = os.path.join(JOB1_DIR, 'used_cars_data_2x.csv')

# Percorsi file output per job 2
J2_CLEANED = os.path.join(JOB2_DIR, 'used_cars_data_cleaned.csv')
J2_100K = os.path.join(JOB2_DIR, 'used_cars_data_100k.csv')
J2_500K = os.path.join(JOB2_DIR, 'used_cars_data_500k.csv')
J2_1M = os.path.join(JOB2_DIR, 'used_cars_data_1m.csv')
J2_2X = os.path.join(JOB2_DIR, 'used_cars_data_2x.csv')

CHUNK_SIZE = 10_000

# Colonne da mantenere nella prima pulizia del dataset grezzo
RAW_COLUMNS_TO_KEEP = [
    "city", "daysonmarket", "description", "engine_displacement",
    "horsepower", "make_name", "model_name", "price", "year"
]

# Pulizia iniziale del dataset grezzo
print("Inizio pulizia dataset iniziale...")
first_write = True
for chunk in pd.read_csv(INPUT_RAW_PATH, chunksize=CHUNK_SIZE):
    chunk = chunk[RAW_COLUMNS_TO_KEEP]
    chunk = chunk.dropna(subset=RAW_COLUMNS_TO_KEEP)
    chunk = chunk[(chunk["price"] > 100) & (chunk["price"] < 300_000)]
    chunk.to_csv(CLEANED_PATH, mode='w' if first_write else 'a', header=first_write, index=False)
    first_write = False
print(f"Dataset pulito salvato in: {CLEANED_PATH}\n")

# === JOB 1 ===
print("Inizio job 1...")
J1_COLS = ["make_name", "model_name", "price", "year"]
rows_100k, rows_500k, rows_1m = [], [], []
total_rows = 0
first_write = True
for chunk in pd.read_csv(CLEANED_PATH, chunksize=CHUNK_SIZE):
    chunk = chunk[J1_COLS].dropna()
    chunk.to_csv(J1_CLEANED, mode='w' if first_write else 'a', header=first_write, index=False)
    first_write = False

    # Campionamento per 100k / 500k / 1M
    if total_rows < 1_000_000:
        needed_100k = 100_000 - sum(len(c) for c in rows_100k)
        needed_500k = 500_000 - sum(len(c) for c in rows_500k)
        needed_1m = 1_000_000 - sum(len(c) for c in rows_1m)
        if needed_100k > 0: rows_100k.append(chunk.head(needed_100k))
        if needed_500k > 0: rows_500k.append(chunk.head(needed_500k))
        if needed_1m > 0: rows_1m.append(chunk.head(needed_1m))
    total_rows += len(chunk)

# Salvataggio campioni
if rows_100k: pd.concat(rows_100k).head(100_000).to_csv(J1_100K, index=False)
if rows_500k: pd.concat(rows_500k).head(500_000).to_csv(J1_500K, index=False)
if rows_1m: pd.concat(rows_1m).head(1_000_000).to_csv(J1_1M, index=False)

# Duplicazione file completo 2x
with open(J1_2X, 'w') as out_file:
    with open(J1_CLEANED, 'r') as in_file:
        shutil.copyfileobj(in_file, out_file)
    with open(J1_CLEANED, 'r') as in_file:
        next(in_file)
        shutil.copyfileobj(in_file, out_file)
print("Job 1 completato.\n")

# === JOB 2 ===
print("Inizio job 2...")
J2_COLS = ["city", "daysonmarket", "description", "price", "year"]
count_100k = count_500k = count_1m = total_rows = 0
for path in [J2_CLEANED, J2_100K, J2_500K, J2_1M]:
    open(path, 'w').close()  # Svuota i file

def clean_description(desc):
    cleaned = re.sub(r'[^a-zA-Z\s]', '', str(desc).lower())
    return ' '.join(cleaned.split())

for chunk in pd.read_csv(CLEANED_PATH, chunksize=CHUNK_SIZE):
    chunk = chunk[J2_COLS].dropna()
    chunk['description'] = chunk['description'].apply(clean_description)

    # Salva dataset completo job2
    chunk.to_csv(J2_CLEANED, mode='a', header=total_rows == 0, index=False, quoting=1)

    # Campioni
    if count_100k < 100_000:
        to_write = chunk.head(100_000 - count_100k)
        to_write.to_csv(J2_100K, mode='a', header=count_100k == 0, index=False, quoting=1)
        count_100k += len(to_write)
    if count_500k < 500_000:
        to_write = chunk.head(500_000 - count_500k)
        to_write.to_csv(J2_500K, mode='a', header=count_500k == 0, index=False, quoting=1)
        count_500k += len(to_write)
    if count_1m < 1_000_000:
        to_write = chunk.head(1_000_000 - count_1m)
        to_write.to_csv(J2_1M, mode='a', header=count_1m == 0, index=False, quoting=1)
        count_1m += len(to_write)
    total_rows += len(chunk)

# Duplicazione file completo 2x job2
with open(J2_2X, 'w') as out_file:
    with open(J2_CLEANED, 'r') as in_file:
        shutil.copyfileobj(in_file, out_file)
    with open(J2_CLEANED, 'r') as in_file:
        next(in_file)
        shutil.copyfileobj(in_file, out_file)

print("Job 2 completato.")
print("Tutte le operazioni sono state completate con successo!")
