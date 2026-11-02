"""Generate the Word report (embedding supplied PNG evidence) and submission ZIP.
Uses only the Python standard library. Run again after collecting screenshots.
"""
from pathlib import Path
from xml.sax.saxutils import escape
import struct
import zipfile

ROOT = Path(__file__).resolve().parent
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
sections = [
    ('Activity 1 — docker ps -a', 'docker ps -a',
     'Lists all containers, including running and stopped containers, with their IDs, image references, commands, status, published ports and names.', '01-docker-ps-a.png'),
    ('Activity 1 — docker stop', 'docker stop lab8-hello',
     'Requests a graceful stop of the running lab8-hello container. Docker sends the configured stop signal (normally SIGTERM), then forcefully terminates it if the timeout expires. The container remains listed by docker ps -a. The argument is a container name or ID; the handout calls it an image name.', '02-docker-stop.png'),
    ('Activity 1 — docker logs', 'docker logs lab8-hello',
     'Displays the container’s captured standard output and standard error, including Flask startup and request messages. Logs remain available after this container stops. The argument is a container name or ID.', '03-docker-logs.png'),
    ('Activity 2 — Lab 5 API image', 'awa34/lab8-ali_rida_awad:0.0.1.RELEASE',
     'Runs the Lab 5 Flask and SQLite CRUD API on container and host port 5000. Routes: GET /api/users, GET /api/users/<user_id>, POST /api/users/add, PUT /api/users/update, DELETE /api/users/delete/<user_id>.', '04-image-v1.png'),
    ('Activity 2 — Names API image', 'awa34/lab8-ali_rida_awad:0.0.2.RELEASE',
     'Runs Flask on container and host port 3000. GET /get_users queries the users table and returns a JSON array of every user name, ordered by user_id. The submitted database is empty, so the initial response is []. Both containers share the same database when launched with build_and_run.sh.', '05-image-v2.png'),
]
parts = []
relationships = []
media = {}
def paragraph(text, bold=False, size=22):
    parts.append(f'<w:p><w:r><w:rPr><w:b w:val="{int(bold)}"/><w:sz w:val="{size}"/></w:rPr><w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>')
paragraph('EECE 435L — Lab 8: Docker and Containers', True, 32)
paragraph('Ali Rida Awad | AUB username: awa34', True)
missing = [s[3] for s in sections if not (ROOT/'evidence'/s[3]).exists()]
paragraph('Evidence status: ' + ('INCOMPLETE — add the real screenshots listed below before uploading.' if missing else 'All five screenshot files embedded. Review their contents before uploading.'), True)
paragraph('Implementation uses Python 3.12 Alpine and pinned Flask dependencies. The handout’s Docker Desktop example uses tags 0.0.1.RELEASE and 0.0.2.RELEASE; these valid tags resolve the colon typo in its prose. Repository names use lowercase and the space in Ali Rida is represented by an underscore.')
for index, (heading, command, explanation, filename) in enumerate(sections, 1):
    paragraph(heading, True, 27)
    paragraph(command, True)
    paragraph(explanation)
    path = ROOT/'evidence'/filename
    if not path.exists():
        paragraph('SCREENSHOT PENDING: evidence/' + filename, True)
        continue
    data = path.read_bytes()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError(f'{path} must be a PNG image')
    width, height = struct.unpack('>II', data[16:24])
    cx = 5486400
    cy = int(cx * height / width)
    # Fit tall screenshots within the page, retaining aspect ratio.
    if cy > 6858000:
        cx = int(cx * 6858000 / cy)
        cy = 6858000
    rid = f'rId{index}'
    media[filename] = data
    relationships.append(f'<Relationship Id="{rid}" Type="{R}/image" Target="media/{filename}"/>')
    parts.append(f'''<w:p><w:r><w:drawing><wp:inline xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"><wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="{index}" name="Screenshot {index}"/><a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr><pic:cNvPr id="{index}" name="{filename}"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>''')
paragraph('Validation', True, 27)
paragraph((ROOT/'evidence/local-verification.txt').read_text() if (ROOT/'evidence/local-verification.txt').exists() else 'Run python3 verify.py to validate the applications locally.')
paragraph('Docker build/run and Docker Desktop screenshots could not be verified in the authoring environment because Docker is backed by Podman with an inaccessible runtime directory. Collect real evidence on a working Docker host using the included instructions. Local Flask tests do not establish Docker build success.')
paragraph('References', True)
paragraph('Lab 8-Docker,containers, and images.docx (provided handout, including the embedded image-tag example).')
paragraph('Docker image reference format: https://docs.docker.com/reference/cli/docker/image/tag/')
xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="{W}" xmlns:r="{R}"><w:body>{''.join(parts)}<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1000" w:right="1000" w:bottom="1000" w:left="1000"/></w:sectPr></w:body></w:document>'''
with zipfile.ZipFile(ROOT/'Lab8_Report.docx', 'w', zipfile.ZIP_DEFLATED) as archive:
    archive.writestr('[Content_Types].xml', '''<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Default Extension="png" ContentType="image/png"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>''')
    archive.writestr('_rels/.rels', f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="{R}/officeDocument" Target="word/document.xml"/></Relationships>')
    archive.writestr('word/document.xml', xml)
    archive.writestr('word/_rels/document.xml.rels', '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'+''.join(relationships)+'</Relationships>')
    for name, data in media.items():
        archive.writestr('word/media/'+name, data)
with zipfile.ZipFile(ROOT/'Lab8_Submission.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(ROOT.rglob('*')):
        if path.is_file() and path.suffix != '.zip' and '__pycache__' not in path.parts and not path.name.endswith('.pyc'):
            archive.write(path, path.relative_to(ROOT))
print('Generated Lab8_Report.docx and Lab8_Submission.zip.')
print('Missing screenshots: ' + (', '.join(missing) if missing else 'none'))
