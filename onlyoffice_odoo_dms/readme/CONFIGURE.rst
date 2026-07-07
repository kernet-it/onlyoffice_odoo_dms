Configuration is inherited from the base ``onlyoffice_odoo`` module.

#. Go to *Settings → ONLYOFFICE* and enter the ONLYOFFICE Docs URL.
#. Optionally configure the JWT secret and header to match your ONLYOFFICE
   Docs `config file <https://api.onlyoffice.com/docs/docs-api/additional-api/signature/>`_.
#. If your network prevents direct server-to-server requests via public
   addresses, set separate internal/external URLs in the ONLYOFFICE settings.

No additional configuration is required for the DMS integration itself.

**Per-directory public link access**

Open any DMS directory form view and set the *Public Link* field to the
desired ONLYOFFICE role. Files in that directory (and sub-directories that
inherit the setting) will be accessible via their portal share link with the
configured role.

**Per-group ONLYOFFICE roles**

Open a DMS Access Group and set the *ONLYOFFICE Role* field. All users in
that group will receive that role for files covered by the group.
