import pathlib

f = pathlib.Path('web/src/main/java/org/akaza/openclinica/control/admin/CreateCRFVersionServlet.java')
t = f.read_text()

# Fix 1: null-check version bean (null when session expires after container restart)
t = t.replace(
    'CRFVersionBean version = (CRFVersionBean) session.getAttribute("version");',
    'CRFVersionBean version = (CRFVersionBean) session.getAttribute("version");\n'
    '        if (version == null) {\n'
    '            version = new CRFVersionBean();\n'
    '        }',
    1
)

# Fix 2: null-check nib before calling getVersionName (nib is null when uploadFile fails silently)
t = t.replace(
    '                String s = ((NewCRFBean) session.getAttribute("nib")).getVersionName();',
    '                NewCRFBean nib = (NewCRFBean) session.getAttribute("nib");\n'
    '                if (nib == null) {\n'
    '                    Validator.addError(errors, "excel_file", resword.getString("you_have_to_provide_spreadsheet"));\n'
    '                    request.setAttribute("formMessages", errors);\n'
    '                    forwardPage(Page.CREATE_CRF_VERSION);\n'
    '                    return;\n'
    '                }\n'
    '                String s = nib.getVersionName();',
    1
)

# Fix 3: null-check items in isItemSame (nib.getItems() can return null)
t = t.replace(
    '        Set names = items.keySet();\n        Iterator it = names.iterator();\n        while (it.hasNext()) {\n            String name = (String) it.next();\n            ItemBean newItem = (ItemBean) idao.findByNameAndCRFId(name, version.getCrfId());',
    '        if (items == null) {\n            return diffItems;\n        }\n'
    '        Set names = items.keySet();\n        Iterator it = names.iterator();\n        while (it.hasNext()) {\n            String name = (String) it.next();\n            ItemBean newItem = (ItemBean) idao.findByNameAndCRFId(name, version.getCrfId());',
    1
)

f.write_text(t)
print("CreateCRFVersionServlet patched")

# Fix CoreSecureController: remove hardcoded Content-Encoding: gzip header.
# CoreSecureController sets this header but the body is never actually compressed —
# it relied on CompressingFilter to do the compression, which we removed.
g = pathlib.Path('web/src/main/java/org/akaza/openclinica/control/core/CoreSecureController.java')
u = g.read_text()
u = u.replace('        response.setHeader("Content-Encoding", "gzip");\n', '', 1)
g.write_text(u)
print("CoreSecureController patched")
