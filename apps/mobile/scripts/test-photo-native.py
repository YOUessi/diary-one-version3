#!/usr/bin/env python3
"""Real ImageIO encoder regression, followed by the existing offline BFF admission gate.
Requires macOS/Xcode, Pillow and BFF Python dependencies. Never calls a model/server.
Usage: python scripts/test-photo-native.py OUTPUT_DIR [SIMULATOR_UDID]
"""
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys
from PIL import Image, ImageDraw, ImageOps

app = Path(__file__).resolve().parents[1]
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
inputs, outputs = out / 'inputs', out / 'outputs'
inputs.mkdir(exist_ok=True); outputs.mkdir(exist_ok=True)
rows, expected = [], {}
def pattern(size):
    im = Image.new('RGB', size)
    draw = ImageDraw.Draw(im)
    w,h=size
    for xy,c in [((0,0,w//2,h//2),(220,30,40)),((w//2,0,w,h//2),(30,190,40)),((0,h//2,w//2,h),(40,60,210)),((w//2,h//2,w,h),(220,190,30))]:
        draw.rectangle(xy,fill=c)
    return im

def case(name, source, image=None, spatial='ASPECT_FIT_LETTERBOX', **extras):
    rows.append(dict(name=name,source=str(source),destination=str(outputs/(name+'.jpg')),spatial=spatial,**extras))
    expected[name]=(image,spatial)

for name,size in [('landscape',(1920,1080)),('portrait',(1080,1920)),('square',(1000,1000)),('camera12mp',(4032,3024)),('portrait3to4',(3024,4032)),('screenshot',(1206,2622)),('panorama',(6000,800))]:
    im=pattern(size);source=inputs/(name+'.jpg');im.save(source,quality=95)
    case(name,source,im)
im=pattern((1600,900));source=inputs/'progressive.jpg';im.save(source,quality=95,progressive=True)
case('progressive',source,im)
for orientation in range(1,9):
    im=pattern((640,400));exif=Image.Exif();exif[274]=orientation;exif[315]='PRIVATE_TEST_AUTHOR'
    source=inputs/('orientation%d.jpg'%orientation);im.save(source,exif=exif)
    with Image.open(source) as decoded: image=ImageOps.exif_transpose(decoded).convert('RGB')
    case('orientation%d'%orientation,source,image)
im=pattern((900,500)).convert('RGBA');im.putalpha(128);source=inputs/'transparent.png';im.save(source)
background=Image.new('RGBA',im.size,'black');background.alpha_composite(im)
case('transparent',source,background.convert('RGB'))
source=inputs/'heic-seed.png';im=pattern((1600,900));im.save(source)
case('heic',inputs/'camera.heic',im,heicSeed=str(source))
case('center-crop',inputs/'landscape.jpg',pattern((1920,1080)),spatial='CENTER_CROP_ASPECT_FILL')
(inputs/'corrupt.jpg').write_bytes(b'not an image')
(inputs/'truncated.jpg').write_bytes((inputs/'landscape.jpg').read_bytes()[:2000])
case('corrupt',inputs/'corrupt.jpg');case('truncated',inputs/'truncated.jpg');case('missing',inputs/'not-there.jpg')
case('invalid-mode',inputs/'landscape.jpg',spatial='STRETCH')
case('write-failure',inputs/'landscape.jpg');rows[-1]['destination']=str(out/'missing-parent/output.jpg')
requests=out/'requests.json'; requests.write_text(json.dumps(rows,indent=2))
binary=out/'image-check'
args=['xcrun','swiftc','-parse-as-library',str(app/'modules/diary-one-vision/ios/EvidenceFrameNormalizer.swift'),str(app/'scripts/evidence-image-main.swift'),'-o',str(binary)]
if len(sys.argv)>2:
    sdk=subprocess.check_output(['xcrun','--sdk','iphonesimulator','--show-sdk-path'],text=True).strip()
    args+=['-sdk',sdk,'-target','arm64-apple-ios16.4-simulator']
subprocess.run(args,check=True)
command=[str(binary),str(requests),str(out/'native-results.json')]
if len(sys.argv)>2: command=['xcrun','simctl','spawn',sys.argv[2]]+command
with (out/'native-output.log').open('w') as log:
    subprocess.run(command,check=True,stdout=log,stderr=subprocess.STDOUT)
results=json.loads((out/'native-results.json').read_text())
sys.path.insert(0,str(app.parents[1]/'services/bff'))
from shared.result_admit import apply_admission
fixture=runpy.run_path(str(app.parents[1]/'services/bff/tests/test_result_contract.py'))['fixture']
checks=[]
for row in results:
    name=row['name']; wanted,spatial=expected[name]
    path=outputs/(name+'.jpg')
    if wanted is None:
        assert row['ok'] is False,(name,row)
        assert not path.exists(), name
        checks.append(dict(name=name,expected_failure=True,passed=True)); continue
    assert row['ok'],row
    with Image.open(path) as image:
        assert image.format=='JPEG' and image.size==(768,1024),(name,image.format,image.size)
        image.load()
        assert 315 not in image.getexif() and 34853 not in image.getexif(),name
        assert image.getexif().get(274,1)==1,name
        # Independent geometric/pixel oracle: checks orientation, centering, aspect and black padding.
        if spatial=='CENTER_CROP_ASPECT_FILL': ref=ImageOps.fit(wanted,(768,1024))
        else:
            inner=ImageOps.contain(wanted,(768,1024));ref=Image.new('RGB',(768,1024),'black')
            ref.paste(inner,((768-inner.width)//2,(1024-inner.height)//2))
        samples=[(int(x*768),int(y*1024)) for x in [.05,.2,.35,.65,.8,.95] for y in [.05,.2,.35,.65,.8,.95]]
        max_delta=max(max(abs(a-b) for a,b in zip(image.getpixel(p)[:3],ref.getpixel(p)[:3])) for p in samples)
        assert max_delta<40,(name,max_delta)
    result,raw=fixture();manifest=json.loads(raw);frame=manifest['assets'][0]['frames'][0]
    frame['relative_path']='outputs/'+name+'.jpg';frame['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    raw=json.dumps(manifest).encode();result['bundle_manifest_sha256']=hashlib.sha256(raw).hexdigest()
    _,admission=apply_admission(result,manifest_bytes=raw,bundle_dir=out,bundle_version='DIARY_ONE_APP_LIBRARY_BUNDLE_V04',allow_mock=False)
    assert admission['publish_admit'],(name,admission)
    checks.append(dict(name=name,passed=True,actual_format='JPEG',actual_size=[768,1024],pixel_max_delta=max_delta,
                       source_metadata_removed=True,bff_admitted=True,sha256=frame['sha256']))
report=dict(scope='Production ImageIO implementation executed on '+('iOS Simulator' if len(sys.argv)>2 else 'macOS')+'; synthetic images and BFF result fixture; no physical iPhone or cloud/model calls.',
            native_source_sha256=hashlib.sha256((app/'modules/diary-one-vision/ios/EvidenceFrameNormalizer.swift').read_bytes()).hexdigest(),
            total=len(checks),passed=len(checks),valid_images=sum('bff_admitted' in r for r in checks),checks=checks)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='checks'},indent=2))
