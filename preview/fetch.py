from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib, json, subprocess
from urllib.parse import quote
from zipfile import ZipFile

site = Path('_site')
site.mkdir()
with ZipFile('preview/overrides.zip') as overrides:
    overrides.extractall(site)

origin = "https://yaad-owner-review.netlify.app"
assets = json.loads(Path('preview/assets.json').read_text())
def copy_asset(item):
    file, expected = item
    url = origin + '/' + quote(file, safe='/')
    modes = [[], ['--resolve', 'yaad-owner-review.netlify.app:443:75.2.60.5']]
    for mode in modes:
        result = subprocess.run(['curl', '-fsSL', '--retry', '2', '--connect-timeout', '8',
            '--max-time', '45', *mode, url], capture_output=True)
        if result.returncode == 0 and hashlib.sha256(result.stdout).hexdigest() == expected:
            target = site / file
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(result.stdout)
            return
    raise RuntimeError('Could not verify hosted asset: ' + file)
with ThreadPoolExecutor(max_workers=12) as pool:
    for number, _ in enumerate(pool.map(copy_asset, assets.items()), 1):
        if number % 100 == 0 or number == len(assets):
            print(f'Verified {number}/{len(assets)} assets', flush=True)
