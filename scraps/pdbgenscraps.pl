#if ( $post_prelude_var ) {
        # generate code to init local var to value of class Array attribute foo.length of next arg
        # Unfortunately, next_var was cast to <type>** in the prelude, recast it back to GObject
        # e.g. num_foo = ((cast gtype) foo).length;
        # e.g. num_foo = (<gtype> *)foo->length;
        # pdbgen.pl ensures there is a next arg i.e. next_var_name is not empty
        # OLD $result .= "  $post_prelude_var = (GimpObjectArray**)" . $next_var_name . "->length;\n"
#            $result .= "  $post_prelude_var = ((GimpObjectArray*)g_value_get_boxed(gimp_value_array_index(args, " . ($argc - 1) . ")))->length;\n";
#}
