**Opening a file in ONLYOFFICE**

#. Navigate to *Documents → Files* (DMS).
#. Click *Edit in ONLYOFFICE* on a supported file (docx, xlsx, pptx, pdf) to
   open it in edit mode, or *Preview in ONLYOFFICE* for view-only mode.
#. The effective role for the current user determines what actions are
   available inside the editor (edit, comment, review, form-fill, etc.).

**Creating a new document**

#. Open a DMS directory.
#. Click *New → ONLYOFFICE Document* (or Spreadsheet / Presentation / PDF).
#. The new file is created in the directory with you as the initial editor.

**Managing per-user roles**

#. Open a DMS file form view.
#. Go to the *ONLYOFFICE Access* tab.
#. Add rows to *ONLYOFFICE User Roles* to override the role for specific users.
   This takes precedence over any group-level or DMS-permission-based role.

**Role resolution order**

1. Per-user override (``onlyoffice.dms.file.access.user`` record).
2. Most permissive role from applicable DMS access groups (``oo_role`` field).
3. DMS permission fallback: write access → *Editor*, read-only → *Viewer*,
   no access → *None*.
