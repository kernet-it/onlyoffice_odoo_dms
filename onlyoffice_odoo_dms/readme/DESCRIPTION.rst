Integrates `ONLYOFFICE Docs <https://www.onlyoffice.com/docs>`_ with the
`OCA DMS <https://github.com/OCA/dms>`_ module. Allows viewing and editing
DMS files directly in Odoo using the ONLYOFFICE editor, with fine-grained
per-file and per-user role control on top of DMS permissions.

Features:

* Open and edit office files (docx, xlsx, pptx, pdf) embedded in the DMS module.
* Fine-grained ONLYOFFICE role control: Viewer, Commenter, Reviewer, Editor,
  Form Filling, Custom Filter.
* Per-user role overrides on individual DMS files.
* Role inheritance from DMS access groups via a dedicated *ONLYOFFICE Role* field.
* Public share-link access with configurable ONLYOFFICE roles per directory.
* Create blank office documents directly inside a DMS directory.
