import pathlib

# Fix 1: These JSPs define function $(x){return document.getElementById(x);} which overwrites
# Prototype.js's $ after it loads. When Prototype fires dom:loaded it calls $(document)
# internally — the overwritten $ passes document to getElementById which returns null,
# causing TypeError: Cannot read properties of null (reading 'dispatchEvent') in
# fireEvent_DOM, which prevents the dom:loaded event from firing and leaves the
# data-entry form without its save/submit controls.
#
# Fix: make the wrapper pass non-strings through unchanged so Prototype's internal
# calls work correctly while page code that passes element IDs as strings still works.

OLD_DOLLAR = "function $(x){return document.getElementById(x);}"
NEW_DOLLAR = "function $(x){if(!x||typeof x!=='string')return x;return document.getElementById(x);}"

dollar_jsps = [
    "web/src/main/webapp/WEB-INF/jsp/include/home-header.jsp",
    "web/src/main/webapp/WEB-INF/jsp/managestudy/viewSectionDataEntry.jsp",
    "web/src/main/webapp/WEB-INF/jsp/submit/doubleDataEntry.jsp",
    "web/src/main/webapp/WEB-INF/jsp/submit/initialDataEntryNw.jsp",
]

for path in dollar_jsps:
    p = pathlib.Path(path)
    if not p.exists():
        print(f"SKIP (not found): {path}")
        continue
    t = p.read_text()
    if OLD_DOLLAR in t:
        p.write_text(t.replace(OLD_DOLLAR, NEW_DOLLAR, 1))
        print(f"Patched $ override: {path}")
    else:
        print(f"Already patched or pattern not found: {path}")

# Fix 2: When GROUP_REPEAT_MAX is left blank in the XLS, the parser defaults to 1
# (same as GROUP_REPEAT_NUMBER). The repetition-model.js then sees repeat-max="1"
# with repeat-start="1" and immediately hits the cap, making the Add button do nothing.
#
# Fix: only emit repeat-max when it actually exceeds repeat-start so that the JS
# defaults to Infinity (unlimited) for blank/default repeat-max values.

OLD_REPMAX = 'repeat-max="<c:out value="${repeatMax}"/>"'
NEW_REPMAX = '<c:if test="${repeatMax > repeatNumber}">repeat-max="<c:out value="${repeatMax}"/>"</c:if>'

repmax_jsps = [
    "web/src/main/webapp/WEB-INF/jsp/managestudy/viewSectionDataEntry.jsp",
    "web/src/main/webapp/WEB-INF/jsp/submit/initialDataEntryNw.jsp",
    "web/src/main/webapp/WEB-INF/jsp/submit/doubleDataEntry.jsp",
    "web/src/main/webapp/WEB-INF/jsp/submit/administrativeEditing.jsp",
]

for path in repmax_jsps:
    p = pathlib.Path(path)
    if not p.exists():
        print(f"SKIP (not found): {path}")
        continue
    t = p.read_text()
    if OLD_REPMAX in t:
        p.write_text(t.replace(OLD_REPMAX, NEW_REPMAX, 1))
        print(f"Patched repeat-max: {path}")
    else:
        print(f"Already patched or not found: {path}")
