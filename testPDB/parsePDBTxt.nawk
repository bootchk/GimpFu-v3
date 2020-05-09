# parse a dump of the pdb, into PDB procedure signatures
# dump the pdb by calling pdb.dump_to_file(f)
# lloyd konneker May 2020

# Implements a small state machine


# captures signature in associative array <signatures>
function captureType() {
  # capture type on second following line
  getline; getline
  type = stripQuotes($1)
  signatures[currentProc] = signatures[currentProc]  " " type
}

function appendToSignature(text) {
  signatures[currentProc] = signatures[currentProc]  text
}

function stripQuotes(text) {
  gsub("\"", " ", text)
  return text
}




BEGIN {state = "null"}

END {
  for (key in signatures) { print signatures[key] }
}

/\(register-procedure / {
   name = stripQuotes($2)
   # print name
   currentProc = name
   signatures[name] = name " : "
   state = "proc"
   next
   }

# match opening left paren
# since parens anywhere, match beginning of line and whitespace

/^\s*\(/ {
   switch ( state )  {
     case "proc":
        state = "inParamSet"
        break
     case "inParamSet":
        state = "inParam"
        captureType()
        break
      case "afterInParams":
        appendToSignature(" => ")
        state = "outParamSet"
        break
      case "outParamSet":
         state = "outParam"
         captureType()
         break
      default:
        print "unknown state open paren"
   }
   next
}

# match closing right paren

/^\s*\)/ {
   switch ( state )  {
     case "proc":
        print "Parse error"
        break
     case "inParam":
        state = "inParamSet"
        break
      case "outParam":
         state = "outParamSet"
         break
       case "inParamSet":
         state = "afterInParams"
         break
       case "outParamSet":
          state = "afterOutParams"
          break
        case "afterOutParams":
        case "afterInParams":
          state = "null"
          break
        default:
          print "unknown state close paren"
  }
   next
}
