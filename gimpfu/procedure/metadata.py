
from procedure.formal_param import GimpfuFormalParam


# v3 _registered_plugins_ is a dictionary of GimpfuProcedureMetadata

class GimpfuProcedureMetadata():

    def __init__(self,
       blurb, help, author, copyright,
       date, label, imagetypes,
       plugin_type, params, results,
       function, menu, domain,
       on_query, on_run):
         self.BLURB=blurb
         self.HELP= help
         self.AUTHOR= author
         self.COPYRIGHT=copyright
         self.DATE= date
         self.MENUITEMLABEL= label
         self.IMAGETYPES= imagetypes
         self.PLUGIN_TYPE= plugin_type
         self.RESULTS= results
         self.FUNCTION= function
         self.MENUPATH= menu
         self.DOMAIN= domain
         self.ON_QUERY= on_query
         self.ON_RUN= on_run

         self.PARAMS= []
         for param in params:
             # assert param is a tuple
             self.PARAMS.append(GimpfuFormalParam(*param))
