import re, pathlib

f = pathlib.Path('OpenClinica/WEB-INF/web.xml')
t = f.read_text()

# Remove <filter> definition block for compressFilter
t = re.sub(
    r'\n    <filter>\n        <filter-name>compressFilter</filter-name>[\s\S]*?    </filter>',
    '',
    t
)
# Remove all <filter-mapping> blocks for compressFilter
t = re.sub(
    r'\n    <filter-mapping>\n        <filter-name>compressFilter</filter-name>[\s\S]*?    </filter-mapping>',
    '',
    t
)

f.write_text(t)
print("compressFilter removed from web.xml")
