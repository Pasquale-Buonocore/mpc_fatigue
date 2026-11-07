# Guida Windows — WSL2 ed esperimenti

## Quale ambiente viene usato

Il progetto gira in Ubuntu 20.04 amd64 dentro WSL2. **PowerShell** esegue i
comandi Windows; **Bash** è la shell dentro Ubuntu. Non incollare comandi Bash
in PowerShell. Docker Desktop non è necessario per questi esperimenti.
WSL2 usa la virtualizzazione gestita da Windows; `mpc-fatigue-ubuntu` è una sua
distribuzione, distinta dall'ambiente interno `docker-desktop`.

Il file `ext4.vhdx` contiene Ubuntu e le dipendenze Linux. In questa configurazione
è su E:, mentre il repository rimane una cartella Windows accessibile da Linux
tramite `/mnt/e`. Il commit Git non contiene il disco WSL, l'ambiente installato
o il clone del modello Centauro. I dischi Windows montati sono accessibili con i
permessi dell'utente Windows: WSL non costituisce isolamento dai file personali.

## Stato delle verifiche

Questa guida distingue l'esecuzione del solver dalla visualizzazione. Alla
redazione, **il robot non compare in RViz sul PC dell'utente: il problema resta
aperto**. Il worktree contiene correzioni a configurazione RViz, mesh e posa
iniziale; sono stati controllati nodi e trasformazioni ROS, ma questo non prova
che la finestra mostri correttamente il robot. Vedere la diagnostica in fondo.

| Esperimento | Evidenza disponibile | Visualizzazione |
|---|---|---|
| Cinematica Pilz 3DOF, 6DOF e due bracci | Solver eseguiti con successo | Da confermare sul PC dell'utente |
| Dinamica Pilz 3DOF | Script termina; OCP localmente infeasible | Non valida una traiettoria ammissibile |
| Forza Pilz 3DOF e 6DOF | IK converge; OCP successivo localmente infeasible | Non valida una traiettoria ammissibile |
| Box1 | OCP converge con warm start; CSV e otto PNG prodotti | Grafici generati; RViz da confermare |
| Box2 | Lettura CSV e grafici eseguiti; OCP originale non converge nelle prove | CSV di Box1 non è una soluzione Box2 |
| MPC principale Centauro | Tre OCP convergenti con posa adattata | Launch senza RViz; riproduzione completa non validata |
| Altre varianti | Nessuna verifica completa | Catalogo in fondo |

Le procedure seguenti sono per simulazione e calcolo offline. Non configurano
un collegamento a robot fisici. Noetic ha raggiunto la fine del supporto nel
2025: viene utilizzato per compatibilità con questo progetto storico.

## A. Usare il PC già configurato

Non ripetere l'installazione se la distribuzione esiste. **PowerShell:**

```powershell
wsl --list --verbose
wsl -d mpc-fatigue-ubuntu
```

Atteso: una distribuzione di versione 2 e una shell Linux (normalmente `root`).
Il solo comando `wsl` potrebbe aprire `docker-desktop`, che è ancora predefinita.

| Elemento | Posizione sul PC configurato |
|---|---|
| Disco Linux | `E:\Codex\mpc_fatigue_runtime\Ubuntu-20.04\ext4.vhdx` |
| Repository | `E:\CartelleCondivise\GitHub_project\mpc_fatigue` |
| Workspace, dentro WSL | `/root/catkin_ws` |
| Ambiente Python, dentro WSL | `/root/micromamba/envs/mpc-py` |
| Modello derivato, dentro WSL | `/root/external/centauro_14dof.urdf` |

### Preparazione di ogni terminale

Aprire un terminale PowerShell per ciascun terminale A/B richiesto, entrarvi con
`wsl -d mpc-fatigue-ubuntu`, poi eseguire questo blocco **Bash** in ciascuno:

```bash
export MPC_CATKIN_WS=/root/catkin_ws
export MPC_CONDA_ENV=/root/micromamba/envs/mpc-py
export REPO="$MPC_CATKIN_WS/src/mpc_fatigue"
export CENTAURO_URDF=/root/external/centauro_14dof.urdf
export MPC_RESULTS=/mnt/e/Codex/mpc_fatigue_runtime/results/manuali
source "$MPC_CATKIN_WS/install/setup.bash"
run_mpc() { bash "$REPO/scripts/run-python-wsl.sh" "$@"; }
mkdir -p "$MPC_RESULTS"
cd "$REPO"
```

`REPO` segue il collegamento ai sorgenti su E:. Il wrapper, pur chiamandosi
`run-python-wsl.sh`, è uno script Bash che seleziona ROS e il Python corretto.

### Grafica WSL e risultati

La procedura grafica assume Windows con WSLg disponibile. **PowerShell:**

```powershell
wsl --version
```

**Bash:**

```bash
printf 'DISPLAY=%s\nWAYLAND_DISPLAY=%s\n' "$DISPLAY" "$WAYLAND_DISPLAY"
ls /mnt/wslg
```

Se WSLg non è disponibile, la visualizzazione richiede un server grafico
configurato separatamente: non è coperto né validato da questa guida. I test
numerici e `MPLBACKEND=Agg` non richiedono finestre. Per aggiornare WSL usare
`wsl --update` da PowerShell, chiudendo prima gli esperimenti.

Aprire in Esplora file `E:\Codex\mpc_fatigue_runtime\results\manuali` per gli
output delle procedure. I risultati precedentemente verificati sono in
`E:\Codex\mpc_fatigue_runtime\results\box1-verified-2026-11-07` e
`centauro-reachable-2026-11-07`. I file interni Linux sono esplorabili da
`\\wsl.localhost\mpc-fatigue-ubuntu\`. Non modificare direttamente `ext4.vhdx`.

## B. Configurare un nuovo PC su E:

Saltare questa sezione sul PC già configurato. È richiesta virtualizzazione
hardware e spazio libero su E: per una distribuzione che cresce con gli utilizzi
(l'ambiente preparato occupava circa 9.2 GiB, oltre ai sorgenti e risultati).
La GUI è stata usata tramite WSLg; un nuovo PC può richiedere driver o aggiornamenti.

### WSL e importazione Ubuntu — PowerShell

In PowerShell amministratore, se WSL manca:

```powershell
wsl --install --no-distribution
wsl --update
```

Riavviare Windows se richiesto. Poi, in PowerShell:

```powershell
wsl --list --verbose
$runtime = 'E:\Codex\mpc_fatigue_runtime'
New-Item -ItemType Directory -Force "$runtime\Ubuntu-20.04" | Out-Null
$baseUrl = 'https://cdimage.ubuntu.com/ubuntu-base/releases/20.04/release'
$archive = 'ubuntu-base-20.04.5-base-amd64.tar.gz'
Invoke-WebRequest "$baseUrl/$archive" -OutFile "$runtime\$archive" -UseBasicParsing
Invoke-WebRequest "$baseUrl/SHA256SUMS" -OutFile "$runtime\SHA256SUMS" -UseBasicParsing
$expected = ((Get-Content "$runtime\SHA256SUMS" | Where-Object { $_ -match ' ubuntu-base-20.04.5-base-amd64.tar.gz$' }) -split '\s+')[0]
$actual = (Get-FileHash "$runtime\$archive" -Algorithm SHA256).Hash
if (-not $expected -or $actual -ine $expected) { throw 'Checksum Ubuntu non valido' }
wsl --import mpc-fatigue-ubuntu "$runtime\Ubuntu-20.04" "$runtime\$archive" --version 2
```

Non usare `--unregister` e non reimportare sopra una distribuzione esistente.
L'import crea il disco su E: e usa inizialmente l'utente Linux root.
Se Git per Windows è installato, clonare in una cartella nuova:

```powershell
New-Item -ItemType Directory -Force 'E:\CartelleCondivise\GitHub_project' | Out-Null
git clone https://github.com/ADVRHumanoids/mpc_fatigue.git E:\CartelleCondivise\GitHub_project\mpc_fatigue
wsl -d mpc-fatigue-ubuntu
```

Il clone ufficiale può non contenere le modifiche locali descritte qui. Trasferire
anche il commit `0e6b834` e il worktree aggiornato tramite un branch pubblicato o
una copia completa dei sorgenti. Verificare in Bash prima della build:

```bash
test -f /mnt/e/CartelleCondivise/GitHub_project/mpc_fatigue/scripts/run-python-wsl.sh
test -f /mnt/e/CartelleCondivise/GitHub_project/mpc_fatigue/python/mpc_fatigue/pynocchio_casadi.py
```

Se Git per Windows manca, installare le dipendenze seguenti in WSL e usare
`git clone` da Bash con destinazione `/mnt/e/CartelleCondivise/GitHub_project/mpc_fatigue`.

### Installazione dentro WSL — Bash come root

Tutti i comandi da qui alla fine della guida sono Bash. Ubuntu Base è minimale;
i pacchetti saranno installati nel disco Linux su E:.

### Dipendenze ROS e strumenti di sistema

Eseguire soltanto su un ambiente nuovo. I comandi richiedono Ubuntu 20.04 amd64;
non cambiare semplicemente il nome della distribuzione su Ubuntu 22.04/24.04.

```bash
cat /etc/os-release
dpkg --print-architecture
apt-get update
apt-get install -y ca-certificates curl git bzip2 gnupg locales lsb-release build-essential cmake
curl -fL https://github.com/ros-infrastructure/ros-apt-source/releases/download/1.3.0/ros-apt-source_1.3.0.focal_all.deb -o /tmp/mpc-ros-apt-source.deb
dpkg -i /tmp/mpc-ros-apt-source.deb
apt-get update
apt-get install -y ros-noetic-desktop ros-noetic-controller-manager ros-noetic-joint-state-controller ros-noetic-joint-state-publisher ros-noetic-robot-state-publisher ros-noetic-xacro libeigen3-dev python3-catkin-pkg python3-rospkg
```

È usata la release `ros-apt-source` 1.3.0 per Focal, presente nell'ambiente
configurato. Se APT o il download falliscono, fermarsi e consultare le fonti
ufficiali; evitare di mescolare pacchetti di altre versioni Ubuntu/ROS.

### Ambiente Python isolato

Le versioni di riferimento sono Python 3.8.20, CasADi 3.6.5, Pinocchio 3.2.0,
NumPy 1.24.4 e Matplotlib 3.7.3. Le dipendenze ROS restano nel Python di sistema;
il wrapper rende disponibili i relativi moduli al Python micromamba.

```bash
mkdir -p "$HOME/bin"
curl -fL https://micro.mamba.pm/api/micromamba/linux-64/latest -o /tmp/mpc-micromamba.tar.bz2
tar -xjf /tmp/mpc-micromamba.tar.bz2 -C "$HOME" bin/micromamba
export MAMBA_ROOT_PREFIX="$HOME/micromamba"
"$HOME/bin/micromamba" create -y -n mpc-py -c conda-forge --strict-channel-priority \
  python=3.8.20 casadi=3.6.5 pinocchio=3.2.0 numpy=1.24.4 matplotlib=3.7.3 \
  pyyaml rospkg catkin_pkg pybind11 pip
```

Non serve attivare micromamba per eseguire gli esempi: il wrapper seleziona
l'interprete e le librerie. Il binding C++ legacy per Python 2.7 resta
**disabilitato**; viene installato il bridge Python con la stessa API.
La risoluzione di questi pacchetti dipende dalla disponibilità del canale
conda-forge; questa guida non fornisce un lockfile completo dei pacchetti transitivi.

### Collegare i sorgenti alla workspace — Bash

```bash
export MPC_CATKIN_WS=/root/catkin_ws
export MPC_CONDA_ENV=/root/micromamba/envs/mpc-py
mkdir -p "$MPC_CATKIN_WS/src"
ln -s /mnt/e/CartelleCondivise/GitHub_project/mpc_fatigue "$MPC_CATKIN_WS/src/mpc_fatigue"
export REPO="$MPC_CATKIN_WS/src/mpc_fatigue"
export CENTAURO_URDF=/root/external/centauro_14dof.urdf
```

Creare il link solo se non esiste. `ln` non deve sovrascrivere una directory
sorgente. Dopo la build, usare la «Preparazione di ogni terminale» della sezione A.

### Compilazione

In una shell Bash pulita, senza un ambiente conda attivato:

```bash
source /opt/ros/noetic/setup.bash
cd "$MPC_CATKIN_WS"
catkin_make install
source "$MPC_CATKIN_WS/install/setup.bash"
rospack find mpc_fatigue
```

L'ultimo comando deve risolvere il pacchetto nella workspace scelta. Ripetere
`catkin_make install` dopo modifiche a codice, launch, URDF o configurazioni:
ROS può leggere la copia installata, non il file appena modificato nei sorgenti.

### Modello Centauro esterno

Necessario solo per Centauro. Il repository del progetto contiene i modelli
Pilz, ma non quello usato nello studio Centauro originale.

```bash
mkdir -p "$HOME/external"
git clone https://github.com/ADVRHumanoids/iit-centauro-ros-pkg.git "$HOME/external/iit-centauro-ros-pkg"
git -C "$HOME/external/iit-centauro-ros-pkg" checkout 171690217a59a30e7c5bb5b30e19dc5f523a70d4
python3 "$REPO/scripts/prepare-centauro-model.py" \
  "$HOME/external/iit-centauro-ros-pkg/centauro_urdf/urdf/centauro.urdf" \
  "$CENTAURO_URDF"
```

Se il clone esiste già, non ripetere `git clone`; controllare prima la revisione
con `git -C ... rev-parse HEAD`. La trasformazione deve ricevere ogni volta il
**modello pubblico originale**, non il file già trasformato.
Il modello derivato mantiene 14 giunti delle braccia, blocca gli altri e aggiunge
`mass1_ee` e `mass2_ee` ai frame `ball1_tip` e `ball2_tip`. Non ricostruisce il
modello originale mancante. Non è necessario compilare tutto il pacchetto esterno
per questi test numerici; il caricamento delle sue mesh in RViz non è configurato.

## Convenzioni per eseguire gli esperimenti

**In ogni terminale Bash**, eseguire il blocco «Preparazione di ogni terminale»
della propria piattaforma. Definisce `REPO`, `CENTAURO_URDF`, `MPC_RESULTS` e la
funzione `run_mpc`, e carica ROS. Le variabili di un terminale non passano agli altri.

Usare un solo esperimento alla volta. Chiudere solver e launch precedenti con
`Ctrl+C`, attendere la chiusura e poi avviare il successivo. Il launch avvia il
master ROS se necessario: non serve un altro `roscore`. Il terminale A resta
occupato dal launch; il terminale B esegue il calcolo. Gli esempi a esecuzione
continua richiedono `Ctrl+C`; non chiudere il launch mentre il solver lo sta usando.

Indice: [Pilz 3DOF](#pilz-3dof), [Pilz 6DOF](#pilz-6dof),
[due Pilz e Box](#due-pilz-e-box), [Centauro](#mpc-centauro),
[test](#test-automatici), [varianti storiche](#catalogo-delle-varianti-storiche).

### Pilz 3DOF

**Terminale A — modello e RViz:**

```bash
roslaunch mpc_fatigue pilz_rviz_3DOF.launch
```

È configurata una vista con Grid, RobotModel e `prbt_base_link` come Fixed Frame.
La posa iniziale dovrebbe essere pubblicata prima del solver; la visibilità
effettiva resta da confermare. Non occorre una GUI per i test numerici in fondo.

**Terminale B — cinematica inversa:**

```bash
run_mpc "$REPO/python/Pilz_3_DOF/inverse_kinematics_pilz_3DOF.py"
```

Atteso: IPOPT converge e stampa gli angoli; il publisher invia una breve sequenza
su `topic_position_from_invkin`. La sola convergenza non conferma l'animazione.
Il programma termina; nel launch 3DOF il publisher conserva l'ultima posa.

**Terminale B — dinamica, in alternativa alla cinematica:**

```bash
run_mpc "$REPO/python/Pilz_3_DOF/inverse_dynamics_pilz_3DOF.py"
```

**Terminale B — forza, come esperimento separato:**

```bash
run_mpc "$REPO/python/Pilz_3_DOF/force_optimization_pilz_3DOF.py"
```

Dinamica e forza hanno completato l'esecuzione Python nelle prove, ma l'OCP ha
riportato `Infeasible_Problem_Detected` / «local infeasibility». Nel test di forza
il primo solve di IK converge: controllare anche il **secondo** solve.
I grafici o i messaggi pubblicati dopo un solve fallito non sono risultati
ammissibili. Questi script non hanno il controllo di fallimento del nuovo MPC
Centauro. Matplotlib può tenere il terminale occupato fino alla chiusura delle
finestre; non viene creato automaticamente un CSV di output per questi esempi.

### Pilz 6DOF

**Terminale A:**

```bash
roslaunch mpc_fatigue pilz_rviz_6DOF.launch
```

**Terminale B — cinematica inversa:**

```bash
run_mpc "$REPO/python/Pilz_6_DOF/inverse_kinematics_pilz_6DOF.py"
```

**Terminale B — forza, in un'esecuzione distinta:**

```bash
run_mpc "$REPO/python/Pilz_6_DOF/force_optimization_pilz_6DOF.py"
```

La cinematica inversa è stata eseguita con successo. Per la forza, IK converge
ma l'OCP successivo risulta localmente infeasible. Nessuna validazione della
traiettoria va dedotta dalla presenza dei grafici. Il launch 6DOF apre RViz senza
la vista salvata del 3DOF: applicare i controlli manuali nella diagnostica.

### Due Pilz e Box

**Terminale A, comune a queste procedure:**

```bash
roslaunch mpc_fatigue 2_pilz_rviz_6DOF.launch
```

Carica `robot_description`, `robot_description_1` e `robot_description_2`.
Anche questo launch richiede configurazione manuale di RViz se la vista è vuota.

**Terminale B — cinematica inversa dei due bracci:**

```bash
run_mpc "$REPO/python/2_pilz_6_DOF/inverse_kinematics.py"
```

Atteso: due solve IK convergenti e pubblicazione delle posizioni. Le eventuali
finestre Matplotlib vanno chiuse per terminare il processo.

**Terminale B — Box1 completo con warm start:**

```bash
mkdir -p "$MPC_RESULTS/box1"
MPC_INITIAL_GUESS_CSV="$REPO/plotter/solution.csv" \
MPC_PLOTTER_DIR="$MPC_RESULTS/box1" \
run_mpc "$REPO/python/2_pilz_6_DOF/Box_Pilz_6DOF.py"
```

Il CSV di esempio contiene 1512 valori. Con questo warm start Box1 ha completato
l'OCP con `Optimal Solution Found`, errore dei vincoli circa `2.9e-12`, CSV e otto
PNG. L'esecuzione senza warm start non era conclusa al limite di prova di 120 s;
non esiste una durata massima garantita. Il programma tenta anche la riproduzione
ROS: la visualizzazione resta da confermare. Output: `box1/solution.csv` e
`box1/figure_folder/`. Il CSV di esempio versionato è soltanto input.

**Terminale B — Box2 completo, tentativo sperimentale:**

```bash
mkdir -p "$MPC_RESULTS/box2"
MPC_INITIAL_GUESS_CSV="$REPO/plotter/solution.csv" \
MPC_PLOTTER_DIR="$MPC_RESULTS/box2" \
run_mpc "$REPO/python/2_pilz_6_DOF/Box_Pilz_6DOF2.py"
```

Box2 ha vincoli più stretti. Non è confermata la convergenza con questo CSV:
la prova diretta era ancora in corso dopo 180 s. Prove diagnostiche con coppie
rilassate sono convergite fino a 7.5 Nm aggiuntivi, ma non a 7 Nm; quei risultati
non validano i vincoli originali. Gli script Box possono comunque salvare il
candidato restituito da un solver fallito: controllare il suo stato prima di usare
il CSV. Interrompere con `Ctrl+C` se necessario.

**Terminale B — sola lettura e grafici da CSV:**

```bash
mkdir -p "$MPC_RESULTS/riproduzione"
cp -n "$REPO/plotter/solution.csv" "$MPC_RESULTS/riproduzione/solution.csv"
MPC_RUN_OCP=0 MPC_PLOTTER_DIR="$MPC_RESULTS/riproduzione" \
run_mpc "$REPO/python/2_pilz_6_DOF/Box_Pilz_6DOF.py"
```

Per la modalità equivalente della seconda variante:

```bash
MPC_RUN_OCP=0 MPC_PLOTTER_DIR="$MPC_RESULTS/riproduzione" \
run_mpc "$REPO/python/2_pilz_6_DOF/Box_Pilz_6DOF2.py"
```

Entrambe hanno prodotto grafici da CSV. Questa modalità evita l'OCP principale,
ma gli script eseguono ancora l'IK iniziale e richiedono ROS e i modelli caricati.
Il CSV di Box1 resta una soluzione di Box1 anche quando è disegnato da Box2.
`cp -n` conserva un file già presente: scegliere una cartella nuova per usare
un CSV diverso. Per un'esecuzione senza finestre aggiungere `MPLBACKEND=Agg`
agli assegnamenti prima di `run_mpc`; i Box salvano comunque i PNG.

### MPC Centauro

Prerequisito: modello ridotto generato nella fase di configurazione.
La posa corrente del centro scatola è `[0.8, 0, 0.8]` m; larghezza 0.5 m,
carico 5 kg. La posa precedente `[1.1, 0, 1.2]` non era raggiunta dal modello
pubblico. Il modello e la posa adattati non riproducono esattamente lo studio.

**Terminale A:**

```bash
roslaunch mpc_fatigue centauro_public_model.launch model:="$CENTAURO_URDF"
```

Questo launch carica il parametro e avvia `robot_state_publisher`.
**Non apre RViz e non include un riproduttore della traiettoria.**

**Terminale B — tre iterazioni e uscita automatica:**

```bash
run_mpc "$REPO/python/Centauro_script/mpc_principal.py" _max_iterations:=3
```

Atteso: stampa di IK, `Solving OCP 0`, `1`, `2`, tre `Optimal Solution Found`
dell'OCP e termine del processo. Il solver pubblica su `to_unroller_topic`;
l'inizializzazione pubblica anche `to_robot_topic`. Senza un unroller funzionante
non è garantita l'animazione delle traiettorie ottime. I due unroller del repository
sono varianti storiche e non sono parte di questa procedura validata.

Tre iterazioni sono state eseguite con violazione massima dei vincoli circa
`0.000113`, sotto la tolleranza impostata di `0.001`. Il test di posa controlla
le mani entro `1e-5` m. Il main corrente solleva un errore se IK o OCP falliscono.
Non salva automaticamente un CSV della traiettoria. Per conservare la console:

```bash
set -o pipefail
run_mpc "$REPO/python/Centauro_script/mpc_principal.py" _max_iterations:=3   2>&1 | tee "$MPC_RESULTS/centauro.log"
```

Per l'esecuzione continua omettere `_max_iterations:=3`; fermarla con `Ctrl+C`.
I parametri si trovano in `python/Libraries/MPC_parameters.py`. Prima di cambiarli
conservare una copia dei valori e ripetere il test di posa e la prova finita.

## Test automatici

Non serve avviare un launch per questa suite:

```bash
MPC_CENTAURO_URDF="$CENTAURO_URDF" \
run_mpc -m unittest discover -s "$REPO/test" -p 'test_*.py' -v
```

Con il modello presente: **3 test e `OK`**. Senza il modello esterno, omettere
l'assegnamento `MPC_CENTAURO_URDF`: il test Centauro sarà saltato, non superato.
La suite controlla bridge numerico contro Pinocchio, lettura/dimensione del CSV
di warm start e raggiungibilità della posa Centauro con limiti dei giunti.
Non verifica RViz, la riproduzione ROS, la convergenza di tutti gli OCP o
l'accuratezza fisica del modello rispetto al robot reale.

## Diagnostica

Eseguire i comandi in un terminale con la preparazione iniziale già caricata.

| Sintomo | Controllo | Interpretazione / azione |
|---|---|---|
| Nessun master | `rosnode list` | Se non raggiungibile, tenere aperto il launch corretto nel terminale A. Non avviare il solver prima del caricamento. |
| Avvio di esperimenti diversi | `rosnode list` e `rosparam list` | Fermare launch precedenti: i parametri dei robot sono globali e possono essere sovrascritti. |
| Pacchetto non trovato | `rospack find mpc_fatigue` | Controllare workspace, build `install` e `source` in quel terminale. |
| `rospy` o `mpc_fatigue` non trovato | `run_mpc -c "import rospy; import mpc_fatigue.pynocchio_casadi; print('OK')"` | Usare il wrapper e verificare `MPC_CATKIN_WS`/`MPC_CONDA_ENV`. |
| Errore di librerie CasADi/Pinocchio | `run_mpc -c "import casadi, pinocchio; import pinocchio.casadi; print(casadi.__version__, pinocchio.__version__)"` | Attese 3.6.5 e 3.2.0. Non mischiare installazioni pip e conda o usare un altro Python. |
| RViz aperto ma vuoto | In RViz: Displays → Global Options → Fixed Frame | Per Pilz usare `prbt_base_link`; aggiungere RobotModel, Robot Description `robot_description`, Visual Enabled. Espandere Status per leggere l'errore esatto. |
| Mesh non trovate | `rospack find mpc_fatigue` e `rg 'package://manipulator' "$REPO/urdf"` (se `rg` disponibile) | Il worktree corrente usa `package://mpc_fatigue/meshes/`. Se viene caricato il vecchio modello, ricompilare e riavviare il launch. |
| Parti del robot mancanti / TF rosso | `rostopic list` e `rosrun tf tf_echo prbt_base_link prbt_flange` | Controllare joint states e i nomi dei giunti; non basta che il parametro URDF esista. |
| Nessun movimento | `rostopic echo -n 1 /topic_position_from_invkin` | Avviare il solver. Nel launch 3DOF controllare anche `/joint_states`; gli altri launch ascoltano direttamente il topic del solver. |
| Robot molto lontano o fuori inquadratura | RViz: Views / camera Orbit | Ripristinare una vista centrata sul robot; zoomare non risolve errori di mesh o TF. |
| `Infeasible_Problem_Detected` | Ultimo `EXIT:` di IPOPT e violazione dei vincoli | Il programma è partito, ma non ha prodotto una soluzione ammissibile. Non trattare il CSV/grafico come validato. |
| Warm start rifiutato | Messaggio «initial guess has ... values» | Il CSV non corrisponde a numero di nodi/variabili dell'esperimento; non tagliarlo arbitrariamente. |
| Grafici non appaiono | Verificare `MPLBACKEND` | `Agg` è intenzionalmente senza finestre; rimuoverlo per Matplotlib interattivo. |

Il warning KDL sull'inerzia del link base non dimostra da solo la causa del
robot invisibile. Per segnalare il problema raccogliere: comando esatto, output
del launch, errore Displays → RobotModel → Status, risultato di `rosnode list`
e del controllo TF. La diagnosi visiva resta aperta.

## Catalogo delle varianti storiche

I nomi seguenti sono relativi a `python/`. Non sono percorsi alternativi
certificati: leggere prima i flag `Check`, gli import e le operazioni su file.

| Gruppo / script | Requisiti e stato |
|---|---|
| `Pilz_3_DOF/inverse_dynamics_pilz_3DOF_working.py` | Variante di dinamica; il nome `working` non è una verifica attuale. Launch 3DOF, non validata interamente. |
| `2_pilz_6_DOF/unconstrained_2_pilz.py` | Due URDF separati, launch a due bracci; corrette alcune incompatibilità Python 3, nessuna prova completa. |
| `2_pilz_6_DOF/second_pilz_constrained.py` | Variante con vincoli sul secondo braccio; non validata. |
| `2_pilz_6_DOF/both_robots_torque_limited_2_pilz.py` | Vincoli su entrambi i bracci; non validata. |
| `Centauro_script/CentaurOCP.py`, `Centauro_dynamics.py`, `MPC_script.py`, `new_mpc.py` | Modello Centauro a 14 giunti e frame delle mani; presenti percorsi `/home/user/workspace/...` e CSV in modalità binaria. Alcune chiamate `SaveCsv` non corrispondono alle firme attuali. Non pronte come ricette autonome. |
| `Centauro_script/MPCwithThermal.py`, `RepeatedMPCwithThermal.py`, `RepeatedMPCwithThermal_original.py`, `RepeatedMPCwithThermal_week.py` | Varianti termiche con flag e formati storici; richiedono revisione di percorsi, CSV e parametri. Non validate. |
| `Centauro_script/RepeatedMPCwithThermal_confriction.py`, `RepeatedMPCwithThermal_confriction_localforce.py` | Varianti con attrito/forze; dipendenze da CSV e initial guess esterni, percorsi fissi. Non validate. |
| `Centauro_script/mpc_withfrictioncone.py`, `mpc_week.py` | Varianti MPC con attrito; salvataggi su percorsi storici. Non validate. |
| `Centauro_script/unroller_node.py` | Riproduzione, marker e temperature; non verificata con la procedura MPC corrente. |
| `talkers/Centauros/unroller_node.py` | Scheletro differente: inizializza variabili dopo `rospy.spin()` e pubblica un tipo diverso da JointState. Non usarlo come riproduttore pronto. |
| `talkers/Centauros/mpc_principal.py` | Copia storica distinta dal main documentato in `python/Centauro_script/`. |
| `Libraries/TemperatureModel.py`, `Tmodel_library.py`, `Centauro_Inverse_Kinematic.py` | Supporto termico/IK e prove isolate; non equivalgono a un esperimento end-to-end validato. |
| `my_python_script.py` e altri talker | Esempi/supporto; non aggiungono una procedura di ricerca verificata. |

## Fonti e riproducibilità

- [Sorgente APT ufficiale ROS e release](https://github.com/ros-infrastructure/ros-apt-source)
- [Installazione storica Noetic su Ubuntu](https://wiki.ros.org/noetic/Installation/Ubuntu)
- [Fine del supporto Noetic](https://discourse.ros.org/t/ros-noetic-end-of-life-may-31-2025/43160)
- [Installazione ufficiale micromamba](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html)
- [Modello pubblico Centauro](https://github.com/ADVRHumanoids/iit-centauro-ros-pkg)

Le prove citate sono quelle eseguite nell'ambiente WSL configurato nel novembre
2026. Le istruzioni per una nuova installazione sono ricavate da quell'ambiente
e dalle fonti ufficiali; non è stata eseguita qui una reinstallazione completa.

Per i problemi specifici di WSL consultare anche:
[installazione WSL](https://learn.microsoft.com/en-us/windows/wsl/install),
[importazione di distribuzioni](https://learn.microsoft.com/en-us/windows/wsl/use-custom-distro),
[applicazioni GUI](https://learn.microsoft.com/en-us/windows/wsl/tutorials/gui-apps),
[archivio ufficiale Ubuntu Base](https://cdimage.ubuntu.com/ubuntu-base/releases/20.04/release/).
