This module will integrate CAS with OpenERP.
============================================

To enable Single Sign Out, we need to check the ticket validity for every request,to do so, the web corelib.js needs to be changed.

Steps
-----
#. Open **corelib.js** under addons/web/static/src/js/corelib.js.
#. Rename **rpc: function(url, params, options)** to **do_rpc: function (url, params, options)** in **JsonRPC** class.
#. Add functions in addons/upcas/corelib.js to JsonRpc class in addons/web/static/src/js/corelib.js.
#. Done.
