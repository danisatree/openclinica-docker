import pathlib

# These JSPs define function $(x){return document.getElementById(x);} which overwrites
# Prototype.js's $ after it loads. When Prototype fires dom:loaded it calls $(document)
# internally — the overwritten $ passes document to getElementById which returns null,
# causing TypeError: Cannot read properties of null (reading 'dispatchEvent') in
# fireEvent_DOM, which prevents the dom:loaded event from firing and leaves the
# data-entry form without its save/submit controls.
#
# Fix: make the wrapper pass non-strings through unchanged so Prototype's internal
# calls work correctly while page code that passes element IDs as strings still works.

OLD = "function $(x){return document.getElementById(x);}"
NEW = "function $(x){if(!x||typeof x!=='string')return x;return document.getElementById(x);}"

jsps = [
    "web/src/main/webapp/WEB-INF/jsp/include/home-header.jsp",
    "web/src/main/webapp/WEB-INF/jsp/managestudy/viewSectionDataEntry.jsp",
    "web/src/main/webapp/WEB-INF/jsp/submit/doubleDataEntry.jsp",
    "web/src/main/webapp/WEB-INF/jsp/submit/initialDataEntryNw.jsp",
]

for path in jsps:
    p = pathlib.Path(path)
    if not p.exists():
        print(f"SKIP (not found): {path}")
        continue
    t = p.read_text()
    if OLD in t:
        p.write_text(t.replace(OLD, NEW, 1))
        print(f"Patched: {path}")
    else:
        print(f"Already patched or pattern not found: {path}")
