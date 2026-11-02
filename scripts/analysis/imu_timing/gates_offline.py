"""Offline gates of PLAN Update 3 and section 7: re-measure corrected files, Sielinko quarters, section 3 controls."""
import sys,json; sys.path.insert(0,'/data/imoroz/vslam-timing-corrected-20261031/scripts/analysis/imu_timing')
from tau_lib import *
W='/data/imoroz/vslam-timing-corrected-20261031/datasets/.timing-imu/'; O={}
# Sielinko: 0 +/- 5 ms in every quarter, every system
I=load_imu(W+'zed2i__'+Z+'/drift/data.csv'); q={}
for a in SYS:
    w,_=windows(traj('zed2i',Z,a),I,4); q[a]=np.round(w[:,1],1).tolist(); print('sielinko drift quarters',a,q[a],flush=True)
O['sielinko_quarters_ms']=q; O['sielinko_gate']=all(abs(x)<=5 for v in q.values() for x in v)
# Section 3 controls on the unchanged data, as the engineer ran them
def one(ds,seq,alg,imu,**k):
    r=estimate(traj(ds,seq,alg),load_imu(imu),**k); return round(r[0],2),round(r[1],3)
Ca=B+'imu/'; ctl={}
for name,ds,seq,alg,k in [('euroc','euroc_mav','MH_01_easy','cuvslam',{}),('euroc','euroc_mav','MH_01_easy','okvis2',{}),
  ('seq07','citrusfarm','seq07','cuvslam',{}),('seq07','citrusfarm','seq07','okvis2',{}),('seq07_slow','citrusfarm','seq07','cuvslam',{'lowrate':.08}),('seq07_slow','citrusfarm','seq07','okvis2',{'lowrate':.08}),
  ('seq04','citrusfarm','seq04','cuvslam',{}),('seq04','citrusfarm','seq04','okvis2',{}),('seq04_slow','citrusfarm','seq04','cuvslam',{'lowrate':.15}),('seq04_slow','citrusfarm','seq04','okvis2',{'lowrate':.15}),
  ('horti','hortimulti','strawberry02','cuvslam',{}),('horti','hortimulti','strawberry02','okvis2',{}),('rosario','rosariov2','sequence1','cuvslam',{}),('rosario','rosariov2','sequence1','okvis2',{})]:
    ctl.setdefault(name,[]).append(one(ds,seq,alg,Ca+f'{ds}/{seq}/data.csv',nboot=20,**k)); print(name,alg,ctl[name][-1],flush=True)
zi=Ca+f'zed2i/{Z}/data.csv'
for alg in ('cuvslam','orbslam3'):
    b0=one('zed2i',Z,alg,zi,nboot=20)[0]
    for pl in (.02,-.02):
        ctl.setdefault('plant',[]).append((alg,pl*1e3,round(one('zed2i',Z,alg,zi,plant=pl,nboot=20)[0]-b0,2))); print('plant',ctl['plant'][-1],flush=True)
O['controls']=ctl; json.dump(O,open(sys.argv[1],'w'),indent=1,default=float)
