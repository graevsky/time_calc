# time_calc

`time_calc` is a cross-platform shell time calculator for Windows, macOS, and Linux.

It works with 24-hour `HHMM` values without `:` and wraps around midnight automatically.

Examples:

```text
time_calc --sum
1000
0040
0115
c
Result: 1155
```

```text
time_calc --diff
0020
0110
c
Result: 2310
```

```text
time_calc --delta
1000
2330
c
Direct: 1330
Via 12h: 0130
Via 24h: 1030
```

## Install

### Windows

Run from PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

The installer ensures `setuptools` and `wheel` are available, then runs `python -m pip install --user --upgrade .` and adds the user scripts directory to your `PATH` if needed.
If `time_calc` is not visible in the current PowerShell session yet, open a new terminal window or run:

```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "User") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "Machine")
```

### macOS / Linux

Run from the project directory:

```sh
chmod +x ./install.sh
./install.sh
```

The installer ensures `setuptools` and `wheel` are available, then runs `python3 -m pip install --user --upgrade .` and updates shell startup files if needed.

### Termux

```sh
pkg install git python
git clone https://github.com/graevsky/time_calc.git
cd time_calc
chmod +x ./install.sh
./install.sh
```

If `time_calc` is not visible immediately, close and reopen Termux.

## Usage

```text
time_calc --help
time_calc --sum [HHMM ...]
time_calc --diff [HHMM ...]
time_calc --delta [HHMM HHMM]
```

- `--sum`: sums any number of times modulo 24 hours.
- `--diff`: subtracts each next time from the first one modulo 24 hours.
- `--delta`: compares exactly two times and shows:
  - `Direct`: absolute difference within the same day.
  - `Via 12h`: the alternative distance if the route goes through a 12-hour boundary.
  - `Via 24h`: the alternative distance if the route goes through midnight.

If you do not pass times on the command line, the program switches to interactive input mode. Enter one `HHMM` value per line and type `c` to finish.
