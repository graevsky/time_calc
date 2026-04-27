#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN=python
else
  echo "Python 3 is required to install time_calc." >&2
  exit 1
fi

"$PYTHON_BIN" -m pip install --user --no-build-isolation --upgrade "$SCRIPT_DIR"

SCRIPTS_DIR=$("$PYTHON_BIN" -c 'import sysconfig; print(sysconfig.get_path("scripts", scheme=sysconfig.get_preferred_scheme("user")))')
PATH_LINE="export PATH=\"$SCRIPTS_DIR:\$PATH\""

add_path_line() {
  target_file=$1

  if [ ! -f "$target_file" ]; then
    : > "$target_file"
  fi

  if ! grep -F "$SCRIPTS_DIR" "$target_file" >/dev/null 2>&1; then
    printf '\n# Added by time_calc installer\n%s\n' "$PATH_LINE" >> "$target_file"
  fi
}

shell_name=$(basename "${SHELL:-sh}")
case "$shell_name" in
  zsh)
    add_path_line "$HOME/.zshrc"
    add_path_line "$HOME/.zprofile"
    ;;
  bash)
    add_path_line "$HOME/.bashrc"
    add_path_line "$HOME/.bash_profile"
    ;;
  *)
    add_path_line "$HOME/.profile"
    ;;
esac

echo "Installed time_calc into $SCRIPTS_DIR."
if printf '%s' ":$PATH:" | grep -F ":$SCRIPTS_DIR:" >/dev/null 2>&1; then
  echo "time_calc is ready to use."
else
  echo "Open a new terminal or run:"
  echo "  $PATH_LINE"
fi

echo "Try: time_calc --help"
