import pandas as pd

def clamp(x):
  return max(0, min(x, 255))

def rgb_to_hex(r, g, b):
    return "#{0:02x}{1:02x}{2:02x}".format(clamp(r), clamp(g), clamp(b))

def get_color_evolution(evolution_value):
    #base green = min 180
    #base rouge = max 170
    if str(evolution_value).lower() == "nan":
        return rgb_to_hex(200, 200, 200)
    if evolution_value <= 0:
        return rgb_to_hex(200, 200, 200)
    else:
        pctgreen = min(25, evolution_value)/25
        return rgb_to_hex(round(170*(1-pctgreen)), round(255 - 75*(pctgreen)), 0)

def intify(value):
    try:
        return round(float(value))
    except ValueError:
        return "-"

def compute_evolution(value, base, returntype):
    try:
        val_evolution = ((value - base) / base) * 100
        txt_evolution = "{:0.1f}".format(val_evolution) + " %"
    except ValueError:
        val_evolution = 0
        txt_evolution = "-"
    except ZeroDivisionError:
        val_evolution = 0
        txt_evolution = "-"
    if returntype is str:
        return txt_evolution
    else:
        return val_evolution

merge_file_list = [
    "countries_ohsome_power_line_length_km_1.csv",
    "countries_ohsome_power_line_length_km_2.csv"
]

df0 = pd.read_csv(merge_file_list[0])

for file in merge_file_list[1:]:
    dft = pd.read_csv(file)
    df0 = df0.merge(dft, left_on="isoa2", right_on="isoa2")

list_dates = [myd for myd in list(df0.columns) if myd != "isoa2"]
list_dates.sort()

df_data = pd.read_csv("wikidata_countries_info_formatted.csv")

df = df_data.merge(df0, left_on="codeiso2", right_on="isoa2")

for myd in list_dates:
    df[myd + "/val_evolution"] = df.apply(lambda x: compute_evolution(x[myd], x["2025-01-01"], float), axis=1)
    df[myd + "/txt_evolution"] = df.apply(lambda x: compute_evolution(x[myd], x["2025-01-01"], str), axis=1)

colsname = " !! ".join([f"Power line length (in km)<br>on {myd}" + (" !! Growth since<br>2025-01-01" if myd!='2025-01-01' else "") for myd in list_dates])
wikistring = "{| class='wikitable sortable' \n|-\n! Country !! " + colsname + " \n"
val_evolution = {}
txt_evolution = {}
for row in df.to_dict(orient='records'):
    base20250101 = row.get('2025-01-01')
    extracols = " || ".join([f"{intify(row.get(myd))} \n|style='background:"
                             + get_color_evolution(row.get(myd + "/val_evolution")) + "'| "
                             + row.get(myd + "/txt_evolution") for myd in list_dates[1:]])
    if (intify(base20250101) != "-") and (intify(base20250101)!=0) :
        wikistring += f"|-\n| [[Power networks/{row.get('name')}|{row.get('name')}]] || {intify(base20250101)} || "
        wikistring += extracols + "\n"
wikistring += "\n|}"

with open("power_line_length_wikitable.txt", "w") as text_file:
    text_file.write(wikistring)

print(wikistring)

print("Countries with more than 5% evolution :")
df_select = df[df["2025-07-01/val_evolution"]>5]
print(df_select["codeiso2"].unique().tolist())