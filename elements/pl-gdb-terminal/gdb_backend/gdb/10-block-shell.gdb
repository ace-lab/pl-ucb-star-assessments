# Disable commands that run other programs or load other scripts.
# (`!` and `|` are aliases that cannot be redefined; SHELL=/bin/false covers them.)
set confirm off
define shell
  echo The shell command is disabled in this environment.\n
end
define pipe
  echo The pipe command is disabled in this environment.\n
end
define edit
  echo The edit command is disabled in this environment.\n
end
define make
  echo The make command is disabled in this environment.\n
end
define source
  echo The source command is disabled in this environment.\n
end
set confirm on
