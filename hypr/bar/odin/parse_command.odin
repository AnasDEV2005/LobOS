package main
import "core:fmt"
import "core:os/os2"
import "core:strings"






main :: proc() {

  full_path := "./commands.txt"

  cmd := fmt.tprintf("cat %s", full_path)

  state, stdout, stderr, err := os2.process_exec({command={"sh", "-c", cmd}}, context.allocator)

  if stderr != nil {
    fmt.eprintln("Error reading commands file: ", err)
    os2.exit(0)
  }
  
  if len(os2.args) != 2 {
    fmt.eprintln("error executing shortcut")
    os2.exit(0)
  }

  string := fmt.tprintf("%s", stdout)

  lines := strings.split(string, "\n")

  arg := os2.args[1]

  is_shortcut := false

  for l in lines {
    tmp := strings.split(l, ":")

    if len(tmp) < 2 { continue }
    fmt.eprintfln("%s", tmp)
    key := tmp[0]
    cmd := tmp[1]

    if arg != key {
      continue
    } else {
      is_shortcut = true
      state, stdout, stderr, err = os2.process_exec({command={"sh", "-c", cmd}}, context.allocator)
      
      a := fmt.tprintf("%s", stdout)
      fmt.eprintfln("%s", a)
    }
  }

  if !is_shortcut {

    state, stdout, stderr, err = os2.process_exec({command={"sh", "-c", arg}}, context.allocator)
    
    if stderr != nil {
      fmt.eprintln("Error reading commands file: ", err)
      os2.exit(0)
    }

    a := fmt.tprintf("%s", stdout)
    fmt.eprintfln("%s", a)
  }


}
