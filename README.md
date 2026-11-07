# MPC Fatigue

Progetto di ricerca sulla pianificazione del movimento e sulla manipolazione
cooperativa considerando limiti di coppia, distribuzione delle forze e
riscaldamento dei motori. Il repository è un pacchetto ROS1 catkin e contiene
esperimenti Python con CasADi/Pinocchio, nodi ROS e modelli dei robot Pilz.

## Robot ed esperimenti

- **Pilz 3DOF e 6DOF:** cinematica inversa, dinamica e ottimizzazione della forza.
- **Due bracci Pilz:** manipolazione di una scatola, ripartizione delle forze e
  vincoli di coppia variabili nel tempo.
- **Centauro:** controllo predittivo (MPC), modelli termici e varianti con attrito.
  Il modello URDF Centauro è esterno al repository.

Gli script rappresentano diverse fasi della ricerca: non tutte le varianti sono
validate o convergono con i parametri predefiniti. Le guide riportano lo stato
verificato di ciascun percorso e i problemi conosciuti.

## Struttura

| Cartella | Contenuto |
|---|---|
| `python/` | Esperimenti raggruppati per robot e librerie condivise |
| `talkers/` | Pubblicazione ROS e riproduzione delle soluzioni |
| `urdf/`, `meshes/` | Descrizioni e geometrie dei robot Pilz |
| `launch/`, `config/` | Avvio ROS e configurazione RViz |
| `src/`, `include/`, `bindings/` | Nodo C++ e binding originale opzionale |
| `plotter/`, `Centauro_solutions/` | Risultati, CSV, immagini e materiali della ricerca |
| `scripts/`, `test/` | Supporto all'esecuzione e test automatici |

## Guide operative

- [Guida Windows: ambiente WSL2, configurazione ed esperimenti](docs/GUIDA_WINDOWS.md)
- [Guida Linux: Ubuntu 20.04, configurazione ed esperimenti](docs/GUIDA_LINUX.md)

Per contribuire al progetto, leggere [Repository Guidelines](AGENTS.md).
