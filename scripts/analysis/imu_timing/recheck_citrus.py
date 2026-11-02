"""Exploratory: camera-IMU offset from VO rotation against the gyroscope, 3-D version with controls.
Over intervals of about 0.3 s, the VO rotation vector is compared with the gyroscope integrated over the same interval shifted
by tau, after one rotation fit (Kabsch). tau > 0: the IMU stamps a motion later than the camera (t_imu = t_cam + tau, Kalibr's
convention). Only intervals with real rotation are used, so vibration does not dominate."""
import sys; sys.path.insert(0,'/data/imoroz/PAPER/vslam-paper/notes/patterns-20261030/scripts')
sys.path.insert(0,'/data/imoroz/PAPER/vslam-paper/scripts')
from common import *
import outage_error as E
from scipy.spatial.transform import Rotation as Rot
BASE=ROOT/'data/traj-cache/runs/data/imoroz/vslam-benchmark/results/vo'; IMU=ROOT/'data/traj-cache/imu'
def load_imu(p):
    d=pd.read_csv(p,comment='#',header=None).to_numpy(float); t=d[:,0]/1e9; g=d[:,1:4]
    o=np.argsort(t,kind='stable'); t,g=t[o],g[o]; k=np.r_[True,np.diff(t)>0]; t,g=t[k],g[k]
    g=g-np.median(g,axis=0)
    return t,np.vstack([np.zeros(3),np.cumsum(0.5*(g[1:]+g[:-1])*np.diff(t)[:,None],axis=0)])
def ivals(tr,dt=0.3):
    t=tr[:,0]; rate=np.median(np.diff(t)); n=max(1,int(round(dt/rate)))
    R=Rot.from_quat(tr[:,4:8]/np.linalg.norm(tr[:,4:8],axis=1,keepdims=True))
    rel=R[:-n].inv()*R[n:]; v=rel.as_rotvec()
    return t[:-n],t[n:],v
def gyro(it,ic,a,b): return np.stack([np.interp(b,it,ic[:,i])-np.interp(a,it,ic[:,i]) for i in range(3)],1)
def kabsch(x,y):
    u,_,vt=np.linalg.svd(x.T@y); d=np.sign(np.linalg.det(vt.T@u.T)); return vt.T@np.diag([1,1,d])@u.T
def score(a,b,v,it,ic,R,tau):
    g=gyro(it,ic,a+tau,b+tau)@R.T; x=g.ravel()-g.mean(); y=v.ravel()-v.mean()
    return (x*y).sum()/np.sqrt((x*x).sum()*(y*y).sum())
def est(a,b,v,it,ic,thr,taus=None):
    taus=np.arange(-.15,.1505,.002) if taus is None else taus
    m=(a>it[0]+.3)&(b<it[-1]-.3)&(b-a<3.)&(np.linalg.norm(v,axis=1)>thr)&(np.linalg.norm(v,axis=1)<1.5)
    a,b,v=a[m],b[m],v[m]
    if len(a)<30: return np.nan,np.nan,len(a),None
    best=None
    for _ in range(3):
        cur=0. if best is None else best
        R=kabsch(gyro(it,ic,a+cur,b+cur),v)
        cs=np.array([score(a,b,v,it,ic,R,x) for x in taus]); k=cs.argmax(); best=taus[k]
    fine=np.arange(best-.004,best+.0041,.0005); cf=np.array([score(a,b,v,it,ic,R,x) for x in fine])
    return fine[cf.argmax()],cf.max(),len(a),(a,b,v,R)
def boot(st,it,ic,n=100,seed=1):
    a,b,v,R=st; rng=np.random.default_rng(seed); blk=((a-a[0])//30).astype(int); ids=np.unique(blk); out=[]
    idx={i:np.flatnonzero(blk==i) for i in ids}; taus=np.arange(-.15,.1505,.002)
    for _ in range(n):
        w=np.concatenate([idx[i] for i in rng.choice(ids,len(ids))])
        cs=[score(a[w],b[w],v[w],it,ic,R,x) for x in taus]; out.append(taus[int(np.argmax(cs))])
    return np.percentile(out,[2.5,97.5])*1e3
from pathlib import Path

W=Path('/data/imoroz/vslam-timing-corrected-20261031')
PLAN=[(ds,s,W/f'datasets/.timing-imu/{ds}__{s}/corrected/data.csv') for ds,s in [('citrusfarm','seq07'),('citrusfarm','seq04')]]
rows=[]
for ds,seq,p in PLAN:
    it,ic=load_imu(p)
    for alg in ('okvis2','cuvslam','orbslam3','okvis2x','svo_pro'):
        f=sorted(glob.glob(str(BASE/ds/seq/alg/'run*/trajectory.txt')))
        if not f: continue
        a,b,v=ivals(E.table(f[0])); tau,c,n,st=est(a,b,v,it,ic,.02)
        if st is None: continue
        rows.append(dict(ds=ds,seq=seq,alg=alg,tau=round(tau*1e3,2),corr=round(c,4),n=n))
r=pd.DataFrame(rows); r.to_csv(W/'timing-campaign/run/recheck_citrus.csv',index=False)
g=r.groupby(['ds','seq'],sort=False).agg(tau=('tau','median'),lo=('tau','min'),hi=('tau','max'))
g['pass']=g.tau.abs()<=1.5; print(g.to_string()); print('GATE4','PASS' if g['pass'].all() else 'FAIL')
