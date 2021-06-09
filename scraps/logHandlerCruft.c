/* Ensure GLib default handler prints all log messages for domain "scriptfu".
 * ScriptFu is a plugin and uses libgimp.
 * So libgimp's log handler is active.
 * This handles scriptfu specific logging.
 * Otherwise, scriptfu logging would be to the "app" domain,
 * which could only be enabled by G_MESSAGES_DEBUG=all.
 * This lets G_MESSAGES_DEBUG=scriptfu enable only messages from ScriptFu.
 */



/*
 * Handler for scriptfu logging events.
 * Signature is GLogFunc
 */
static void
scriptfu_log_func (const gchar    *log_domain,
                   GLogLevelFlags  flags,
                   const gchar    *message,
                   gpointer        data)
{
  const gchar *level;

  switch (flags & G_LOG_LEVEL_MASK)
    {
    case G_LOG_LEVEL_WARNING:
      level = "WARNING";
      break;
    case G_LOG_LEVEL_CRITICAL:
      level = "CRITICAL";
      break;
    case G_LOG_LEVEL_ERROR:
      level = "ERROR";
      break;
    default:
      level = "FATAL";
      break;
    }

  /* Print message canonical to what GLib's default handler would. */
  g_printerr ("%s: %s: %s\n", log_domain, level, message);
}

void set_scriptfu_log_handler(void)
{
  g_log_set_handler (SCRIPTFU_LOG_DOMAIN,
                     G_LOG_LEVEL_MESSAGE,
                     scriptfu_log_func,
                     NULL);
}
// TODO should be WARNING???





/* get new name if deprecated, else proc_name remains the same. */
/*
{
  GValue           value    = G_VALUE_INIT;
  GimpValueArray  *args;
  GimpValueArray  *values = NULL;
  gchar           *new_proc_name;

  args = gimp_value_array_new (1);
  g_value_init (&value, G_TYPE_STRING);
  g_value_set_string (&value, proc_name);
  debug_gvalue(&value);
  gimp_value_array_append (args, &value);

  values = gimp_pdb_run_procedure_array (gimp_get_pdb (),
                              "python-fu-map-pdb-name",
                              args);
  if (! values)
     return script_error (sc, "Failed call to deprecate", 0);
  new_proc_name = GIMP_VALUES_GET_STRING (values, 1);
  // new_proc_name points into values
  g_debug ("New proc name: %s", proc_name);
  if (strcmp(proc_name, new_proc_name) != 0)
  {
    g_debug ("Deprecating: %s to:%s", proc_name, new_proc_name);
    // Is deprecated
    // Free old name and replace with copy of new name
    g_free (proc_name);
    proc_name = g_strdup (new_proc_name);
  }

  gimp_value_array_unref (values);
  gimp_value_array_unref (args);
}
*/
