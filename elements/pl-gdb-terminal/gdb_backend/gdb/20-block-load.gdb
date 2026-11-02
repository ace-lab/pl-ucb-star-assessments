# Stop students from pointing gdb at some other executable.
set confirm off
define file
  echo Loading a different program is disabled in this environment.\n
end
define exec-file
  echo Loading a different program is disabled in this environment.\n
end
set confirm on
