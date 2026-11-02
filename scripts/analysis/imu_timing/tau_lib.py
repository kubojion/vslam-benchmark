"""Offset of IMU against camera from VO rotation. Functions of tau_band_engineer.py and tau_check_engineer.py, unchanged."""
import numpy as np,glob,sys,pandas as pd
from scipy.spatial.transform import Rotation as Rot
from scipy.ndimage import uniform_filter1d
B='/data/imoroz/PAPER/vslam-paper/data/traj-cache/'
def load_imu(p):
    d=pd.read_csv(p,comment='#',header=None).to_numpy(float); t=d[:,0]/1e9; g=d[:,1:4]
    o=np.argsort(t,kind='stable'); t,g=t[o],g[o]; k=np.r_[True,np.diff(t)>0]; t,g=t[k],g[k]
    g=g-np.median(g,axis=0)
    return t,np.vstack([np.zeros(3),np.cumsum(0.5*(g[1:]+g[:-1])*np.diff(t)[:,None],axis=0)])
def load_tr(p):
    d=np.loadtxt(p,comments='#'); d=d[np.argsort(d[:,0])]; d=d[np.r_[True,np.diff(d[:,0])>1e-6]]; return d
def intervals(tr,maxdt=0.25):
    t=tr[:,0]; q=tr[:,4:8]; q=q/np.linalg.norm(q,axis=1,keepdims=True); R=Rot.from_quat(q)
    v=(R[:-1].inv()*R[1:]).as_rotvec(); a,b=t[:-1],t[1:]; m=(b-a)<maxdt
    return a[m],b[m],v[m]
def gyro(it,ic,a,b): return np.stack([np.interp(b,it,ic[:,i])-np.interp(a,it,ic[:,i]) for i in range(3)],1)
def hp(x,dt,win_s):
    n=max(3,int(round(win_s/np.median(dt)))); return x-uniform_filter1d(x,n,axis=0,mode='nearest')
def kabsch(x,y):
    u,_,vt=np.linalg.svd(x.T@y); d=np.sign(np.linalg.det(vt.T@u.T)); return vt.T@np.diag([1,1,d])@u.T
TAUS=np.arange(-.12,.1201,.002)
def curve(a,b,v,it,ic,R,dt,win,mask):
    cs=[]; y=hp(v/dt[:,None],dt,win)
    for tau in TAUS:
        g=hp(gyro(it,ic,a+tau,b+tau)@R.T/dt[:,None],dt,win)
        cs.append(((g[mask]*y[mask]).sum(),(g[mask]**2).sum(),(y[mask]**2).sum()))
    return np.array(cs)
def estimate(traj,imu,win=2.0,lowrate=None,plant=0.0,nboot=200,seed=1):
    it,ic=imu; a,b,v=intervals(traj); it=it+plant
    m=(a>it[0]+.3)&(b<it[-1]-.3); a,b,v=a[m],b[m],v[m]; dt=b-a
    w=np.linalg.norm(v,axis=1)/dt
    # drop tracking glitches
    keep=w<np.percentile(w,99.9)
    a,b,v,dt=a[keep],b[keep],v[keep],dt[keep]; w=w[keep]
    mask=np.ones(len(a),bool)
    if lowrate: # keep only samples in slow-turning spans, mimicking a slow vehicle
        sm=uniform_filter1d(w,int(5/np.median(dt)))
        mask=sm<lowrate
    best=0.
    for _ in range(3):
        R=kabsch(gyro(it,ic,a+best,b+best)[mask],v[mask])
        C=curve(a,b,v,it,ic,R,dt,win,mask); c=C[:,0]/np.sqrt(C[:,1]*C[:,2]); best=TAUS[c.argmax()]
    # per-block bootstrap of the correlation curve
    blk=((a-a[0])//30).astype(int); ids=np.unique(blk[mask]); rows=[]
    y=hp(v/dt[:,None],dt,win); G=[hp(gyro(it,ic,a+t,b+t)@R.T/dt[:,None],dt,win) for t in TAUS]
    S=np.zeros((len(TAUS),ids.max()+1,3))
    for i,g in enumerate(G):
        for j,arr in enumerate(((g*y).sum(1),(g*g).sum(1),(y*y).sum(1))):
            np.add.at(S[i,:,j],blk[mask],arr[mask])
    rng=np.random.default_rng(seed); out=[]
    for _ in range(nboot):
        w_=rng.choice(ids,len(ids)); s=S[:,w_,:].sum(1); cc=s[:,0]/np.sqrt(s[:,1]*s[:,2]); 
        k=cc.argmax()
        if 0<k<len(TAUS)-1:
            d=(cc[k-1]-cc[k+1])/(2*(cc[k-1]-2*cc[k]+cc[k+1])); out.append(TAUS[k]+d*0.002)
        else: out.append(TAUS[k])
    k=c.argmax(); pk=TAUS[k]
    if 0<k<len(TAUS)-1: pk=TAUS[k]+(c[k-1]-c[k+1])/(2*(c[k-1]-2*c[k]+c[k+1]))*0.002
    return pk*1e3,c.max(),int(mask.sum()),np.percentile(out,2.5)*1e3,np.percentile(out,97.5)*1e3,(c.max()-np.median(c))
def run(ds,seq,algs,imu_path,lows=(None,),wins=(2.0,),plants=(0.0,)):
    I=load_imu(imu_path); rows=[]
    for alg in algs:
        f=sorted(glob.glob(B+f'runs/data/imoroz/vslam-benchmark/results/vo/{ds}/{seq}/{alg}/run*/trajectory.txt'))
        if not f: continue
        T=load_tr(f[0])
        for lr in lows:
          for w in wins:
            for pl in plants:
                r=estimate(T,I,win=w,lowrate=lr,plant=pl)
                rows.append(dict(ds=ds,seq=seq[:14],alg=alg,win=w,low=lr,plant=pl*1e3,tau=round(r[0],1),corr=round(r[1],3),n=r[2],lo=round(r[3],1),hi=round(r[4],1)))
                print(rows[-1],flush=True)
    return rows
def prep(T,I,maxdt=.25):
    it,ic=I; a,b,v=intervals(T,maxdt); m=(a>it[0]+1)&(b<it[-1]-1); a,b,v=a[m],b[m],v[m]; dt=b-a
    w=np.linalg.norm(v,axis=1)/dt; k=w<np.percentile(w,99.9)
    return a[k],b[k],v[k],dt[k]
def R0(a,b,v,it,ic): return kabsch(gyro(it,ic,a,b),v)
def wide(a,b,v,dt,it,ic,R,taus,win=2.0,mask=None,axis=None):
    y=hp(v/dt[:,None],dt,win); out=[]
    m=np.ones(len(a),bool) if mask is None else mask
    for t in taus:
        g=hp(gyro(it,ic,a+t,b+t)@R.T/dt[:,None],dt,win)
        if axis is None: x,z=g[m].ravel(),y[m].ravel()
        else: x,z=g[m,axis],y[m,axis]
        out.append((x*z).sum()/np.sqrt((x*x).sum()*(z*z).sum()))
    return np.array(out)
def peak(taus,c):
    k=c.argmax()
    if 0<k<len(taus)-1:
        return (taus[k]+(c[k-1]-c[k+1])/(2*(c[k-1]-2*c[k]+c[k+1]))*(taus[1]-taus[0]))*1e3,c[k]
    return taus[k]*1e3,c[k]
T1=np.arange(-.12,.1201,.002)
Z='field1_110426_full_10fps_q90'
SYS=['orbslam3','cuvslam','okvis2','basalt']
def traj(ds,seq,alg):
    return load_tr(sorted(glob.glob(B+f'runs/data/imoroz/vslam-benchmark/results/vo/{ds}/{seq}/{alg}/run*/trajectory.txt'))[0])
def setup(T,I):
    it,ic=I; a,b,v,dt=prep(T,I); R=R0(a,b,v,it,ic)
    p,_=peak(T1,wide(a,b,v,dt,it,ic,R,T1)); R=kabsch(gyro(it,ic,a+p/1e3,b+p/1e3),v)
    return it,ic,a,b,v,dt,R
def windows(T,I,n):
    it,ic,a,b,v,dt,R=setup(T,I); q=np.quantile(a,np.linspace(0,1,n+1)); out=[]
    for i in range(n):
        m=(a>=q[i])&(a<q[i+1]); out.append(((q[i]+q[i+1])/2,)+peak(T1,wide(a,b,v,dt,it,ic,R,T1,mask=m)))
    return np.array(out),it[0]
