# agent_core.py
import pandas as pd
import numpy as np
import json, os, math
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

OUTPUT_DIR = "outputs"
MEMORY_FILE = "memory.json"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Memory helpers ---
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"analyses": []}

def save_memory(mem):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(mem, f, indent=2, ensure_ascii=False)

def add_memory_entry(question, summary, artifacts=[]):
    mem = load_memory()
    entry = {"timestamp": datetime.utcnow().isoformat()+"Z",
             "question": question,
             "summary": summary,
             "artifacts": artifacts}
    mem["analyses"].append(entry)
    save_memory(mem)

# --- Loading ---
def load_csv(path_or_buffer, nrows=None):
    df = pd.read_csv(path_or_buffer, nrows=nrows)
    return df

# --- Type detection ---
def detect_column_types(df):
    types = {}
    for col in df.columns:
        s = df[col]
        if pd.api.types.is_numeric_dtype(s):
            types[col] = "numeric"
        elif pd.api.types.is_datetime64_any_dtype(s):
            types[col] = "datetime"
        else:
            # try date parse
            try:
                pd.to_datetime(s.dropna().unique()[:3])
                types[col] = "datetime"
            except Exception:
                # low cardinality -> categorical
                if s.nunique(dropna=True) < min(50, len(s)/2):
                    types[col] = "categorical"
                else:
                    types[col] = "text"
    return types

# --- Descriptive stats ---
def descriptive_stats(df, cols=None):
    if cols is None:
        cols = df.columns.tolist()
    stats = {}
    for col in cols:
        s = df[col]
        if pd.api.types.is_numeric_dtype(s):
            stats[col] = {
                "count": int(s.count()),
                "mean": float(np.nanmean(s)),
                "median": float(np.nanmedian(s)),
                "std": float(np.nanstd(s, ddof=1)) if s.count()>1 else None,
                "var": float(np.nanvar(s, ddof=1)) if s.count()>1 else None,
                "min": float(np.nanmin(s)),
                "25%": float(np.nanpercentile(s,25)),
                "50%": float(np.nanpercentile(s,50)),
                "75%": float(np.nanpercentile(s,75)),
                "max": float(np.nanmax(s)),
                "n_unique": int(s.nunique(dropna=True)),
                "n_missing": int(s.isna().sum())
            }
        else:
            stats[col] = {
                "count": int(s.count()),
                "n_unique": int(s.nunique(dropna=True)),
                "top": s.value_counts(dropna=True).idxmax() if s.nunique(dropna=True)>0 else None,
                "freq_top": int(s.value_counts(dropna=True).max()) if s.nunique(dropna=True)>0 else 0,
                "n_missing": int(s.isna().sum())
            }
    return stats

# --- Plots ---
def plot_histogram(df, column, bins=50, save_as=None):
    plt.figure(figsize=(8,4))
    sns.histplot(df[column].dropna(), bins=bins)
    plt.title(f"Histogram of {column}")
    plt.tight_layout()
    if save_as:
        plt.savefig(save_as)
        plt.close()
        return save_as
    else:
        return plt

def plot_boxplot(df, column, save_as=None):
    plt.figure(figsize=(6,4))
    sns.boxplot(x=df[column].dropna())
    plt.title(f"Boxplot of {column}")
    plt.tight_layout()
    if save_as:
        plt.savefig(save_as)
        plt.close()
        return save_as
    else:
        return plt

def plot_correlation_heatmap(df, numeric_cols, save_as=None):
    corr = df[numeric_cols].corr()
    plt.figure(figsize=(10,8))
    sns.heatmap(corr, annot=False, cmap="coolwarm", vmin=-1, vmax=1)
    plt.title("Correlation heatmap")
    plt.tight_layout()
    if save_as:
        plt.savefig(save_as)
        plt.close()
        return save_as
    return plt

def plot_scatter_matrix(df, columns, save_as=None):
    pd.plotting.scatter_matrix(df[columns].sample(n=min(500,len(df))), figsize=(12,12))
    plt.tight_layout()
    if save_as:
        plt.savefig(save_as)
        plt.close()
        return save_as
    return plt

# --- Outlier detection ---
def detect_outliers_iqr(series):
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    low = q1 - 1.5*iqr
    high = q3 + 1.5*iqr
    out_mask = (series < low) | (series > high)
    return out_mask, {"low": float(low), "high": float(high)}

def detect_outliers_isolationforest(df, numeric_cols, contamination=0.01):
    iso = IsolationForest(contamination=contamination, random_state=42)
    X = df[numeric_cols].fillna(0)
    iso.fit(X)
    preds = iso.predict(X)
    # -1 -> outlier, 1 -> inlier
    mask = preds == -1
    return mask

# --- Clustering ---
def run_kmeans(df, numeric_cols, n_clusters=3):
    X = df[numeric_cols].fillna(0)
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    k = KMeans(n_clusters=n_clusters, random_state=42)
    labels = k.fit_predict(Xs)
    return labels, k

# --- Correlation with target ---
def correlation_with_target(df, target_col):
    numeric = df.select_dtypes(include=[np.number]).columns.tolist()
    if target_col not in numeric:
        return None
    corrs = {}
    for c in numeric:
        if c==target_col: continue
        try:
            corrs[c] = float(df[c].corr(df[target_col]))
        except:
            corrs[c] = None
    # sort by absolute correlation
    sorted_corr = sorted(corrs.items(), key=lambda x: abs(x[1]) if x[1] is not None else 0, reverse=True)
    return sorted_corr

# --- High-level query processor (improved) ---
def answer_question(df, question_text):
    q = question_text.lower().strip()
    types = detect_column_types(df)
    numeric_cols = [c for c,t in types.items() if t=="numeric"]
    
    # Pergunta 1: Tipos de dados
    if any(word in q for word in ["tipos", "tipo de dado", "tipos de dados", "categorias"]):
        ans = types
        add_memory_entry(question_text, "Detected column types.", [])
        return {"answer": ans, "type": "types"}
    
    # Pergunta 2: Distribuição/Histograma
    if any(word in q for word in ["distribuição", "histogram", "histograma", "frequência"]):
        for c in df.columns:
            if c.lower() in q:
                path = os.path.join(OUTPUT_DIR, f"hist_{c}.png")
                plot_histogram(df, c, save_as=path)
                add_memory_entry(question_text, f"Histogram generated for {c}.", [path])
                return {"answer": f"Histogram of {c} generated.", "artifact": path, "type": "histogram"}
        if numeric_cols:
            var_col = df[numeric_cols].var().idxmax()
            path = os.path.join(OUTPUT_DIR, f"hist_{var_col}.png")
            plot_histogram(df, var_col, save_as=path)
            add_memory_entry(question_text, f"Histogram generated for {var_col}.", [path])
            return {"answer": f"Histogram of {var_col} generated.", "artifact": path, "type": "histogram"}
    
    # Pergunta 3: Intervalo/Min/Max
    if any(word in q for word in ["intervalo", "mínimo", "máximo", "range", "min", "max"]):
        stats = descriptive_stats(df, numeric_cols)
        summary = {c: {"min": stats[c]["min"], "max": stats[c]["max"]} for c in numeric_cols}
        add_memory_entry(question_text, "Returned min/max for numeric columns.", [])
        return {"answer": summary, "type": "range"}
    
    # Média/Mediana
    if any(word in q for word in ["média", "mediana", "tendência central", "mean", "median"]):
        stats = descriptive_stats(df, numeric_cols)
        summary = {c: {"mean": stats[c]["mean"], "median": stats[c]["median"]} for c in numeric_cols}
        add_memory_entry(question_text, "Returned mean/median for numeric columns.", [])
        return {"answer": summary, "type": "central_tendency"}
    
    # Variabilidade
    if any(word in q for word in ["variabilidade", "desvio", "variância", "std", "var"]):
        stats = descriptive_stats(df, numeric_cols)
        summary = {c: {"std": stats[c]["std"], "var": stats[c]["var"]} for c in numeric_cols}
        add_memory_entry(question_text, "Returned std/var for numeric columns.", [])
        return {"answer": summary, "type": "variability"}
    
    # Taxa de fraude ou classe
    if any(word in q for word in ["taxa", "proporção", "percentual", "fraude", "class"]):
        target_candidates = [c for c in df.columns if "class" in c.lower() or "fraud" in c.lower()]
        if target_candidates:
            target = target_candidates[0]
            counts = df[target].value_counts()
            total = len(df)
            proportions = (counts / total * 100).to_dict()
            add_memory_entry(question_text, f"Calculated proportion for {target}.", [])
            return {"answer": {"column": target, "counts": counts.to_dict(), "proportions": proportions, "total": total}, "type": "proportion"}
    
    # Outliers
    if any(word in q for word in ["outliers", "valores atípicos", "anomalias", "atípico"]):
        iqr_outliers = {}
        for c in numeric_cols:
            mask, bounds = detect_outliers_iqr(df[c].dropna())
            n_out = int(mask.sum()) if hasattr(mask,'sum') else 0
            iqr_outliers[c] = {"n_outliers": n_out, "bounds": bounds}
        if len(numeric_cols) >= 2:
            iso_mask = detect_outliers_isolationforest(df, numeric_cols, contamination=0.005)
            n_iso = int(iso_mask.sum())
        else:
            n_iso = 0
        add_memory_entry(question_text, f"Detected outliers via IQR and IsolationForest.", [])
        return {"answer": {"iqr_summary": iqr_outliers, "isolation_forest_outliers": n_iso}, "type": "outliers"}
    
    # Correlação
    if any(word in q for word in ["correlação", "relacionadas", "influência", "correlation"]):
        target_candidates = [c for c in df.columns if "class" in c.lower() or "target" in c.lower() or "fraud" in c.lower()]
        if target_candidates:
            target = target_candidates[0]
            corrs = correlation_with_target(df, target)
            path = os.path.join(OUTPUT_DIR, "correlation_heatmap.png")
            plot_correlation_heatmap(df, numeric_cols, save_as=path)
            add_memory_entry(question_text, f"Computed correlation with target {target}.", [path])
            return {"answer": {"target": target, "correlations": corrs[:10]}, "artifact": path, "type": "correlation"}
        else:
            path = os.path.join(OUTPUT_DIR, "correlation_heatmap.png")
            plot_correlation_heatmap(df, numeric_cols, save_as=path)
            add_memory_entry(question_text, "Generated correlation heatmap.", [path])
            return {"answer": "Correlation heatmap generated.", "artifact": path, "type": "correlation"}
    
    # Conclusões
    if any(word in q for word in ["conclusão", "conclusões", "insights", "resumo final"]):
        mem = load_memory()
        all_summaries = [entry["summary"] for entry in mem["analyses"]]
        conclusion = f"Baseado em {len(all_summaries)} análises realizadas: " + "; ".join(all_summaries[:5])
        return {"answer": conclusion, "type": "conclusion"}
    
    # fallback
    add_memory_entry(question_text, "Question not matched; returning basic summary.", [])
    basic = {"rows": int(len(df)), "columns": len(df.columns), "columns_list": df.columns.tolist()}
    return {"answer": f"Pergunta não reconhecida. Resumo básico: {basic}", "type": "basic"}