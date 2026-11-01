"""Frame-to-frame VO angular rate vs gyro, high-passed, over the whole recording (no rotation threshold). 
tau>0: IMU stamps a motion later than the camera. Controls: planted shift, known sequences, low-motion-only subsets."""
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
A=['cuvslam','okvis2','orbslam3','basalt']
rows=[]
rows+=run('euroc_mav','MH_01_easy',['cuvslam','okvis2'],B+'imu/euroc_mav/MH_01_easy/data.csv')
rows+=run('citrusfarm','seq07',['cuvslam','okvis2'],B+'imu/citrusfarm/seq07/data.csv',lows=(None,0.15,0.08))
rows+=run('citrusfarm','seq04',['cuvslam','okvis2'],B+'imu/citrusfarm/seq04/data.csv',lows=(None,0.15))
rows+=run('hortimulti','strawberry02',['cuvslam','okvis2'],B+'imu/hortimulti/strawberry02/data.csv',lows=(None,0.15))
rows+=run('rosariov2','sequence1',['cuvslam','okvis2'],B+'imu/rosariov2/sequence1/data.csv')
rows+=run('zed2i','field1_110426_full_10fps_q90',A,B+'imu/zed2i/field1_110426_full_10fps_q90/data.csv',wins=(1.0,2.0,4.0))
rows+=run('zed2i','field1_110426_full_10fps_q90',['cuvslam','orbslam3'],B+'imu/zed2i/field1_110426_full_10fps_q90/data.csv',plants=(0.02,-0.02))
pd.DataFrame(rows).to_csv(sys.argv[1]+'/tau_band.csv',index=False)
