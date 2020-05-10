# parse a dump of the pdb, into PDB procedure signatures

# Input is a text file dump of the pdb, created by calling pdb.dump_to_file(f)

# Output is a JSON file and another format that looks like type signatures

# TODO !!! The JSON has an extra comma after the last procedure

# lloyd konneker May 2020



# Implements a small state machine

# note that both the input and the JSON do not omit empty containers
# e.g. a list of out params always, even if list is empty






# captures signature in associative array <signatures>

function captureTypeSig(type) {
  signatures[currentProc] = signatures[currentProc]  " " type
}

function appendToSignature(text) {
  signatures[currentProc] = signatures[currentProc]  text
}

function stripQuotes(text) {
  gsub("\"", " ", text)
  return text
}

function captureProcNameSig(name) {
  name = stripQuotes(name)
  signatures[name] = name " : "
}






# translates to JSON
# JSON is dict[name] of dict[inParams list[types], outParams list[types]]

function captureProcNameJSON(name) {
  print name ":"
  # always a dictionary of params, keyed by "in" and "out"
  print indent "{"
}

function closeProcJSON() {
  # close dict of params
  # comma between procs
  print indent "},"
  # don't close ProcSet    print "}"
}

# JSON does not allow trailing commas, JSON5 does
function captureTypeJSON(type, shouldPrefixComma) {
  # types are in a comma delimited list
  if (shouldPrefixComma == "true") {
    print indent indent ", " type
  }
  else {
    print indent indent type
  }

}



# chooses or doubles up on format of output
# JSON is written immediately, signature is dumped at END


# signature list has no open and close delimiter, only json
function openProcSet() { print "{" }
function closeProcSet() { print "}" }


function captureProcName(name) {
  captureProcNameSig(name)
  captureProcNameJSON(name)
}

function closeProc() {
  closeProcJSON()
}

function openParamSet(inOut) {
   # just JSON
   # key, and start list
   print indent "\""  inOut  "\": ["
}

function closeParamSet(shouldAddComma) {
   # signature
   if (shouldAddComma == "true") {
    appendToSignature(" => ")
   }

   # JSON
   # close list
   if (shouldAddComma == "true") {
    print indent indent "],"
   }
   else {
    print indent indent "]"
   }
}

function captureType(shouldPrefixComma) {
  # capture type on second following line
  # it is already quoted
  getline; getline
  type = $1

  captureTypeSig(stripQuotes(type))
  captureTypeJSON(type, shouldPrefixComma)
}








BEGIN {
  state = "null"
  openProcSet()
  indent = "   "
}

END {
  closeProcSet()

  # append signatures to JSON file
  #for (key in signatures) { print signatures[key] }
}

/\(register-procedure / {
   captureProcName($2)

   currentProc = stripQuotes($2)
   state = "proc"
   next
   }

# match opening left paren
# since parens anywhere, match beginning of line and whitespace

/^\s*\(/ {
   switch ( state )  {
     case "proc":
        state = "inParamSet"
        openParamSet("in")
        break

     case "inParamSet":
        state = "inParam"
        captureType("false")
        break
      case "outParamSet":
         state = "outParam"
         captureType()
         break

      case "afterInParam":
        state = "inParam"
        captureType("true")
        break
      case "afterOutParam":
        state = "outParam"
        captureType("true")
        break

      case "afterInParamSet":
        openParamSet("out")
        state = "outParamSet"
        break
      case "afterOutParamSet":
        print "Parse error: open paren after out params"
        break

      default:
        print "found open paren in unknown state " state
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
        state = "afterInParam"
        break
      case "outParam":
         state = "afterOutParam"
         break

     case "afterInParam":
        state = "afterInParamSet"
        closeParamSet("true")
        break
      case "afterOutParam":
         state = "afterOutParamSet"
         closeParamSet("false")
         break

       case "inParamSet":
         state = "afterInParamSet"
         closeParamSet("true")
         break
       case "outParamSet":
          state = "afterOutParamSet"
          closeParamSet("false")
          break

        case "afterOutParamSet":
        case "afterInParamSet":
          closeProc()
          state = "null"
          break
        default:
          print "found close paren in unknown state: " state
  }
   next
}
