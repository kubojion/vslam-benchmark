#!/usr/bin/env python3
"""Re-link an isolated shutdown repair from preserved build objects; no estimator execution."""
from pathlib import Path
import re,shlex,subprocess,hashlib,json,difflib,sys
r=Path(__file__).resolve().parents[2];orb=r/'src/ORB_SLAM3'
if len(sys.argv)!=2:raise SystemExit('usage: build_orb_shutdown.py /absolute/fresh/output')
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
source=orb/'src/System.cc';old=source.read_text();begin=old.index('    /*if(mpViewer)',old.index('void System::Shutdown()'));end=old.index('    if(!mStrSaveAtlasToFile.empty())',begin)
replacement='''    if(mpViewer)
        mpViewer->RequestFinish();

    // Stop owned workers before reading the map or unloading runtime libraries.
    // The global BA worker is managed inside LoopClosing; wait for its recorded
    // completion after the loop-closing thread can no longer start another one.
    if(mptLocalMapping && mptLocalMapping->joinable())
        mptLocalMapping->join();
    if(mptLoopClosing && mptLoopClosing->joinable())
        mptLoopClosing->join();
    while(mpLoopCloser->isRunningGBA())
        usleep(5000);
    if(mpViewer && mptViewer && mptViewer->joinable())
        mptViewer->join();

'''
new=old[:begin]+replacement+old[end:]
(out/'System.cc.original').write_text(old);(out/'System.cc').write_text(new)
(out/'applied.patch').write_text(''.join(difflib.unified_diff(old.splitlines(keepends=True),new.splitlines(keepends=True),fromfile='a/src/System.cc',tofile='b/src/System.cc')))
flags=(orb/'build/CMakeFiles/ORB_SLAM3.dir/flags.make').read_text()
compile=['/usr/bin/c++']
for key in ['CXX_DEFINES','CXX_INCLUDES','CXX_FLAGS']:
 compile+=shlex.split(re.search(r'^'+key+r' = (.*)$',flags,re.M)[1])
compile+=['-o',str(out/'System.cc.o'),'-c',str(out/'System.cc')]
link=shlex.split((orb/'build/CMakeFiles/ORB_SLAM3.dir/link.txt').read_text())
link[link.index('-o')+1]=str(out/'libORB_SLAM3.so')
obj='CMakeFiles/ORB_SLAM3.dir/src/System.cc.o';assert obj in link
link[link.index(obj)]=str(out/'System.cc.o')
inputs=[]
for arg in link:
 if arg.endswith('.o') and arg!=str(out/'System.cc.o'):
  p=orb/'build'/arg;inputs.append(dict(path=str(p.relative_to(r)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(out/'build-recipe.json').write_text(json.dumps(dict(compile=compile,link=link,cwd=str(orb/'build'),retained_object_inputs=inputs,original_system_sha256=hashlib.sha256(source.read_bytes()).hexdigest()),indent=2)+'\n')
for label,cmd in [('compile',compile),('link',link)]:
 with (out/(label+'.log')).open('w') as log:subprocess.run(cmd,cwd=orb/'build',stdout=log,stderr=subprocess.STDOUT,check=True)
print('Built isolated library',out/'libORB_SLAM3.so')
