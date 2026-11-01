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
PLAN=[]
for s in ('seq04','seq07'):
    PLAN+= [('citrusfarm',s,'fed to estimators',IMU/'citrusfarm'/s/'data.csv',.02),('citrusfarm',s,'ZED built-in IMU',IMU/'raw/citrusfarm'/s/'zed_imu.csv',.02),('citrusfarm',s,'MicroStrain host clock',IMU/'raw/citrusfarm'/s/'microstrain_host_clock.csv',.02)]
for s in ('strawberry02','strawberry03'):
    PLAN+= [('hortimulti',s,'fed to estimators',IMU/'hortimulti'/s/'data.csv',.02),('hortimulti',s,'raw IMU clock',IMU/'raw/hortimulti'/s/'microstrain_imu_clock.csv',.02)]
for s in ('sequence1','sequence5'):
    PLAN+= [('rosariov2',s,'fed to estimators',IMU/'rosariov2'/s/'data.csv',.02),('rosariov2',s,'raw original',IMU/'raw/rosariov2'/s/'data.csv',.02)]
for s in ('MH_01_easy','MH_03_medium','MH_05_difficult'):
    PLAN+= [('euroc_mav',s,'fed to estimators',IMU/'euroc_mav'/s/'data.csv',.02)]
PLAN+= [('zed2i','field1_110426_full_10fps_q90','fed to estimators',IMU/'zed2i/field1_110426_full_10fps_q90/data.csv',.02),('zed2i','field1_110426_full_10fps_q90','fed, turning only',IMU/'zed2i/field1_110426_full_10fps_q90/data.csv',.06)]
rows=[]
for ds,seq,lab,p,thr in PLAN:
    it,ic=load_imu(p)
    for alg in ('okvis2','cuvslam','orbslam3','okvis2x','svo_pro'):
        f=sorted(glob.glob(str(BASE/ds/seq/alg/'run*/trajectory.txt')))
        if not f: continue
        a,b,v=ivals(E.table(f[0])); tau,c,n,st=est(a,b,v,it,ic,thr)
        if st is None: continue
        lo,hi=boot(st,it,ic,60) if alg in('okvis2','cuvslam') else (np.nan,np.nan)
        pl=None
        if alg=='cuvslam' or ds=='euroc_mav':
            pl=est(a,b,v,it+0.020,ic,thr)[0]*1e3
        rows.append(dict(ds=ds,seq=seq,imu=lab,alg=alg,tau=tau*1e3,corr=c,n=n,lo=lo,hi=hi,planted20=pl)); print(rows[-1],flush=True)
r=pd.DataFrame(rows); r.to_csv(OUT/'timing2.csv',index=False)
print(r.groupby(['ds','seq','imu'],sort=False).agg(tau=('tau','median'),spread=('tau',lambda x:x.max()-x.min()),corr=('corr','median'),n=('n','median'),lo=('lo','median'),hi=('hi','median'),planted=('planted20','median')).round(2).to_string())
