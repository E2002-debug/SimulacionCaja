import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import os

# ---------- CONFIG ----------
EXCEL_FILE = "openbox.xlsx"   # archivo generado por openbox.py
ALPHA = 0.05                  # para IC 95%
OUTPUT_DIR = "openbox_reports"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------- CARGAR DATOS ----------
df = pd.read_excel(EXCEL_FILE, sheet_name=0)

print("Columnas cargadas:", df.columns.tolist())

# Validar que la columna %SLA exista
if "%SLA" not in df.columns:
    raise ValueError("❌ La columna '%SLA' no se encuentra en el Excel. Revise el archivo.")

# ---------- RESUMEN POR s ----------
group = df.groupby("s")
summary_rows = []

columnas_metricas = ["CT", "%SLA", "rho", "T_prom", "W", "Wq", "L", "Lq"]

for s, g in group:
    n = len(g)
    row = {"s": s, "n": n}
    
    for col in columnas_metricas:
        vals = g[col].values

        mean = np.mean(vals)
        std = np.std(vals, ddof=1)
        se = std / np.sqrt(n)

        # valor t para IC95
        t = stats.t.ppf(1 - ALPHA/2, df=n-1) if n > 1 else np.nan
        ci_low = mean - t*se if n > 1 else np.nan
        ci_high = mean + t*se if n > 1 else np.nan

        row[f"{col}_mean"] = mean
        row[f"{col}_std"] = std
        row[f"{col}_se"] = se
        row[f"{col}_ci_low"] = ci_low
        row[f"{col}_ci_high"] = ci_high

    summary_rows.append(row)

summary_df = pd.DataFrame(summary_rows).sort_values("s")
summary_df.to_excel(os.path.join(OUTPUT_DIR, "resumen_por_s.xlsx"), index=False)

print("✔ Resumen por s guardado en:", os.path.join(OUTPUT_DIR, "resumen_por_s.xlsx"))

# ---------- FUNCIÓN PARA GUARDAR GRÁFICOS ----------
def save_plot(x, y, yerr, xlabel, ylabel, title, filename):
    plt.figure(figsize=(7, 5))
    plt.errorbar(x, y, yerr=yerr, fmt='o-', capsize=5)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=150)
    plt.close()

# ---------- GRÁFICOS ----------
xs = summary_df["s"]

# CT vs s
save_plot(
    xs,
    summary_df["CT_mean"],
    summary_df["CT_se"] * stats.t.ppf(1 - ALPHA/2, df=summary_df["n"] - 1),
    "Número de cajas (s)",
    "Costo Total (CT)",
    "CT vs s (media ± IC95%)",
    "CT_vs_s.png"
)

# SLA vs s
save_plot(
    xs,
    summary_df["%SLA_mean"],
    summary_df["%SLA_se"] * stats.t.ppf(1 - ALPHA/2, df=summary_df["n"] - 1),
    "Número de cajas (s)",
    "% SLA (<= 8 min)",
    "%SLA vs s (media ± IC95%)",
    "SLA_vs_s.png"
)

# rho vs s
save_plot(
    xs,
    summary_df["rho_mean"],
    summary_df["rho_se"] * stats.t.ppf(1 - ALPHA/2, df=summary_df["n"] - 1),
    "Número de cajas (s)",
    "Utilización ρ",
    "ρ vs s (media ± IC95%)",
    "rho_vs_s.png"
)

# W vs s
save_plot(
    xs,
    summary_df["W_mean"],
    summary_df["W_se"] * stats.t.ppf(1 - ALPHA/2, df=summary_df["n"] - 1),
    "Número de cajas (s)",
    "W (min)",
    "W vs s (media ± IC95%)",
    "W_vs_s.png"
)

print("✔ Gráficos guardados en:", OUTPUT_DIR)

# ---------- EXPORTAR MATRICES ----------
df.to_excel(os.path.join(OUTPUT_DIR, "matriz_completa.xlsx"), index=False)
summary_df.to_excel(os.path.join(OUTPUT_DIR, "estadisticas_resumidas.xlsx"), index=False)

print("✔ Archivos exportados correctamente.")

# ---------- RESUMEN TEXTUAL ----------
with open(os.path.join(OUTPUT_DIR, "resumen_texto.txt"), "w", encoding="utf8") as f:
    f.write("RESUMEN POR s (media, std, IC95%)\n\n")
    f.write(summary_df.to_string(index=False))
    f.write("\n\nObservaciones:\n")
    f.write("- Si Wq ≈ 0 → no hay colas en la mayoría de configuraciones.\n")
    f.write("- Si rho << 1 → hay subutilización.\n")
    f.write("- Comparar CT_mean para elegir el s óptimo.\n")

print("✔ Resumen textual generado.")
