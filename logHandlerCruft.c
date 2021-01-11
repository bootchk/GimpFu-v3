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
