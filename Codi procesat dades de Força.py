import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import csv
from scipy.signal import lfilter
import sys
import os
from pathlib import PurePath
import argparse

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Grafica")
os.makedirs(OUTPUT_DIR, exist_ok=True)
#############################################################################

#SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))

###########################################################################

def parse_arguments():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_directory = os.path.join(script_dir, "directory")
    if not os.path.isdir(default_directory):
        default_directory = script_dir

    parser = argparse.ArgumentParser(description="Crea gràfics a partir de les dades contingudes en fitxers txt contiguts dins una carpeta donada. Pel bon funcionament del programa, és recomana que dins la carpeta hi hagi un màxim de 3 fitxers txt.")
    parser.add_argument("directory", nargs="?", type=str, default=default_directory, help="Ruta de la carpeta a on és troben els fitxers txt. Si no es passa, s'usarà la carpeta 'directory' o la del script.")
    parser.add_argument("-f", "--figures", action="store_true", help="Dibuixa un gràfic diferent per a cada fitxer de dades.")
    parser.add_argument("-a", "--adjacent", action="store_true", help="Crea una figura forma per diferents subgràfics adjunts, que comparteixen l'eix X.")
    parser.add_argument("-s", "--superposed", action="store_true", help="Representa gràficament tots els fitxers de dades en un únic gràfic.")
    parser.add_argument("-m", "--show_maxs", action="store_true", help="Marca els màxims absoluts en els gràfics amb un punt vermell.")
    args = parser.parse_args()
    if not os.path.isdir(args.directory):
        parser.error(f"El directori no existeix: {args.directory}")
    return args

#############################################################################
class GetData():

    def __init__(self, path):
        self.files = self.scan_directory(path) # Llista de fitxers txt que es troben en el directori path
        self.max_yvalue = 0
        self.yvalues = []
        self.max_yvalues = {} # Diccionari amb els valors de màxima força de cada fitxer.
        
    def scan_directory(self, path):
        """
        Escanetja la carpeta o directori donat i retorna una llista amb
        les rutes dels fitxers txt que conté.
        """
        file_list = []
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in {".venv", "Grafica", "__pycache__"} and not d.startswith(".")]
            for i in files:
                if i.lower().endswith(".txt"):
                    file_list.append(os.path.join(root, i))
        return sorted(file_list)

    def open_csv(self, path:str):
        """
        Llegeix un document txt com si fos un csv.
        Retorna dues llistes, la primera amb les dades de temps
        i la segona amb les dades de força en Z.
        """
        Time = []
        Fz = []
        csv.field_size_limit(sys.maxsize)
        with open(path, newline="", encoding="latin-1") as csvfile:
            reader = csv.reader(csvfile, delimiter="\t")
            for row in reader:
                if len(row) < 14:
                    continue
                try:
                    row[13] = row[13].replace(",",".")
                    row[0] = row[0].strip("+")
                    a = row[0]+"."+row[1]
                    a = a.replace("0", "", 1)
                    Time.append(a)
                    Fz.append(row[13])
                except IndexError:
                    continue

        Fz = list(float(i) for i in Fz[2:])
        Time = self.convert_time_data(list(i for i in Time[2:]))
        return Time, Fz

    def convert_time_data(self, time_data:list):
        """
        Converteix els valors de la llista self.time_ a segons.
        Transforma els format HH:MM:SS.ssss a segons.
        """
        time_list = []
        for t in time_data:
            a = list(float(i) for i in t.split(":"))
            time_list.append(a[0]*3600 + a[1]*60 + a[2])      
        return time_list

    def filter_force(self, force_data:list):
        """
        Filtra els valors de la força
        """
        if not force_data:
            return []
        a = 1
        b = [0.2, 0.2, 0.2, 0.2, 0.2]
        try:
            fz_filtered = lfilter(b, a, force_data)
        except ValueError:
            fz_filtered = force_data
        return fz_filtered

    def get_data(self, path):
        """
        Obté les dades de temps i força
        """
        time_data, force_data = self.open_csv(path)
        force_data = self.filter_force(force_data)
        return time_data, force_data

    def get_max_value(self, time:list, force:list):
        """
        Obté el valor màxim de la força i l'instant
        de temps a on ocorr.
        """
        if force is None or time is None or len(force) == 0 or len(time) == 0:
            return [0, 0]
        max_force = max(force)
        if hasattr(force, "argmax"):
            position = int(force.argmax())
        else:
            position = max(range(len(force)), key=force.__getitem__)
        time_value = time[position]
        return [time_value, max_force]
        

class MakePlot(GetData):

    def __init__(self, path, show_max):
        """
        path: str
        Ruta de la carpeta o directori on es troben els fitxers txt
        amb les dades de força de la kistler.

        show_max: bool
        Si és True, marcara amb punts vermells els màxims de cada gràfic.
        Si és False, no farà res.
        """
        super().__init__(path)
        self.show_max = show_max

    def make_plot(self):
        """
        Crea una figura o finestra diferent per a cada fitxer de dades.
        Retorna un diccionari amb els valors de temps i força màxim de cada gràfic.
        """
        colors = self.set_color()
        c = 0
        for document in self.files:
            fig, ax = plt.subplots()
            time_data, force_data = self.get_data(document)
            ax.plot(time_data, force_data, linewidth=0.7, color=colors[c % len(colors)])
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Fz Max(N)")
            ax.set_xlim(left=0, auto=True)
            ax.set_ylim(bottom=0)
            ax.xaxis.set_major_locator(ticker.MultipleLocator(250))
            ax.set_title(PurePath(document).stem)
            max_value = self.get_max_value(time_data, force_data)
            self.max_yvalues[PurePath(document).stem]=self.get_max_value(time_data, force_data)
            if self.show_max:
                ax.plot(max_value[0], max_value[1], marker="o", color="red")
            c += 1
            

    def make_adjacent_plots(self):
        """
        Crea una figura o finestra amb tres gràfics adjecents que comperteixen l'eix X.
        Retorna un diccionari amb els valors de temps i força màxim de cada gràfic.
        """
        if not self.files:
            print(f"No s'han trobat fitxers txt al directori: {self.files}")
            return
        colors = self.set_color()
        c = len(self.files)
        fig, ax = plt.subplots(c, 1, sharex=True, figsize=(10, 3 * c), layout='constrained')
        for i in range(c):
            time_data, force_data = self.get_data(self.files[i])
            ax[i].plot(time_data, force_data, linewidth=0.7, color=colors[i % len(colors)])
            ax[i].set_xlabel("Time (s)")
            ax[i].set_ylabel("Fz Max(N)")
            ax[i].set_xlim(left=0, auto=True)
            ax[i].set_ylim(bottom=0)
            ax[i].xaxis.set_major_locator(ticker.MultipleLocator(250))
            max_value = self.get_max_value(time_data, force_data)
            self.max_yvalues[PurePath(self.files[i]).stem] = max_value
            if self.show_max:
                ax[i].plot(max_value[0], max_value[1], marker="o", color="red")
        fig.savefig(os.path.join(OUTPUT_DIR, "adjacent_plots.png"), dpi=300, bbox_inches="tight")
            
    def make_superposed_plot(self):
        """
        Dibuixa en un mateix gràfic totes les corbes de dades dels fitxers de dades donats.
        Retorna un diccionari amb els valors de temps i força màxim de cada gràfic.
        """
        if not self.files:
            print(f"No s'han trobat fitxers txt al directori: {self.files}")
            return
        fig, ax = plt.subplots(figsize=(12, 6))
        colors = self.set_color()
        c = 0
        for document in self.files:
            time_data, force_data = self.get_data(document)
            label = self.clean_label(PurePath(document).stem)
            ax.plot(time_data, force_data, linewidth=2, color=colors[c % len(colors)], label=label)
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Fz Max(N)")
            ax.set_xlim(left=0, auto=True)
            ax.set_ylim(bottom=0, auto=True)
            ax.xaxis.set_major_locator(ticker.MultipleLocator(250))
            max_value = self.get_max_value(time_data, force_data)
            self.max_yvalues[PurePath(document).stem] = max_value
            if self.show_max:
                ax.plot(max_value[0], max_value[1], marker="o", color="red", markersize=6)
            c += 1
        ax.legend(title="Fitxer", loc="best", fontsize=10)
        fig.savefig(os.path.join(OUTPUT_DIR, "superposed_plot.png"), dpi=300, bbox_inches="tight")

            
    def set_color(self):
        return ["black", "dodgerblue", "firebrick", "darkgreen", "darkorange", "mediumvioletred", "teal", "gold"]

    def clean_label(self, label:str):
        return label.lstrip("_").replace("_", " ")


#######################################################################
args = vars(parse_arguments())

path = args["directory"] # Nom de la carpeta donada.

a = MakePlot(path, args["show_maxs"]) # Crida la funció MakePlot

if not (args["figures"] or args["adjacent"] or args["superposed"]):
    args["superposed"] = True

if args["figures"]:
    #Crea una finestra o figura indepent per a cada fitxers.
    a.make_plot()
    
if args["adjacent"]:
    #Crea una figura amb diferents gràfics adjecents que comperteixen l'eix de les X.
    #1 gràfic per fitxer.
    a.make_adjacent_plots()

if args["superposed"]:
    #Crea un únic gràfic i dibuixa les corbes de dades de cada fitxer.
    a.make_superposed_plot()

print("Màxims per fitxer:")
for nome, (temps, forza) in a.max_yvalues.items():
    print(f"{nome}: temps={temps}, força={forza}")
backend = plt.get_backend().lower()
if backend not in {"agg", "pdf", "ps", "svg", "cairo"}:
    try:
        plt.show()
    except Exception:
        pass
