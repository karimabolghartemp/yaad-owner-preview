from pathlib import Path, PurePosixPath
import hashlib,json,subprocess,stat
from zipfile import ZipFile
cfg=json.loads(Path('preview/release.json').read_text())
archive=Path('preview-site.zip')
subprocess.run(['curl','--fail','--location','--retry','3','--connect-timeout','15','--max-time','300',cfg['url'],'--output',str(archive)],check=True)
if hashlib.sha256(archive.read_bytes()).hexdigest()!=cfg['sha256']:raise RuntimeError('Preview archive verification failed')
expected=json.loads(Path('preview/assets.json').read_text());site=Path('_site');site.mkdir()
with ZipFile(archive) as z:
 if set(z.namelist())!=set(expected):raise RuntimeError('Unexpected archive files')
 for entry in z.infolist():
  name=PurePosixPath(entry.filename)
  if name.is_absolute() or '..' in name.parts or stat.S_ISLNK(entry.external_attr>>16):raise RuntimeError('Invalid archive path')
  data=z.read(entry)
  if hashlib.sha256(data).hexdigest()!=expected[entry.filename]:raise RuntimeError('Invalid asset: '+entry.filename)
  dest=site/entry.filename;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
print(f'Assembled and verified {len(expected)} public preview files')
