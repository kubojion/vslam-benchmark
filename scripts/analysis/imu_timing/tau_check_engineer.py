import numpy as np,glob,sys,pandas as pd
sys.argv=['x',sys.argv[1]]
src=open(sys.argv[1]+'/tau_band.py').read().split("A=['cuvslam'")[0]
exec(src)
from scipy.signal import butter,sosfiltfilt
Z='field1_110426_full_10fps_q90'
def rs(ds,seq,alg,imu):
    f=sorted(glob.glob(B+f'runs/data/imoroz/vslam-benchmark/results/vo/{ds}/{seq}/{alg}/run*/trajectory.txt'))[0]
    return load_tr(f),load_imu(imu)
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
T5=np.arange(-.5,.5001,.01); T1=np.arange(-.12,.1201,.002)
def report(name,ds,seq,alg,imu):
    T,I=rs(ds,seq,alg,imu); it,ic=I; a,b,v,dt=prep(T,I); R=R0(a,b,v,it,ic)
    # refine R at the provisional peak
    p,_=peak(T1,wide(a,b,v,dt,it,ic,R,T1)); R=kabsch(gyro(it,ic,a+p/1e3,b+p/1e3),v)
    c=wide(a,b,v,dt,it,ic,R,T5); srt=np.sort(c)[::-1]; side=c[np.abs(T5)>.2]
    p,cp=peak(T1,wide(a,b,v,dt,it,ic,R,T1))
    print(f"{name} {alg}: peak {p:.1f} ms corr {cp:.3f} | wide-scan best {T5[c.argmax()]*1e3:.0f} ms | outside +-200 ms: max {side.max():.3f}, sd {side.std():.3f} -> z={(cp-side.mean())/side.std():.1f}",flush=True)
    # per axis
    ax=[peak(T1,wide(a,b,v,dt,it,ic,R,T1,axis=i)) for i in range(3)]
    print('   per axis',[(round(x,1),round(c_,3)) for x,c_ in ax],flush=True)
    # split in 4 time quarters
    q=np.quantile(a,[0,.25,.5,.75,1]); qs=[]
    for i in range(4):
        m=(a>=q[i])&(a<q[i+1]); qs.append(round(peak(T1,wide(a,b,v,dt,it,ic,R,T1,mask=m))[0],1))
    print('   quarters',qs,flush=True)
    # by rate: forward-gap filter: sample spacing groups and rotation-activity groups
    wr=np.linalg.norm(v,axis=1)/dt; sm=uniform_filter1d(wr,int(5/np.median(dt)))
    q2=np.quantile(sm,[0,.5,.9,1]); print('   by activity (low50,mid40,top10)',[round(peak(T1,wide(a,b,v,dt,it,ic,R,T1,mask=(sm>=q2[i])&(sm<=q2[i+1])))[0],1) for i in range(3)],flush=True)
    # band: use highpass windows narrower to emphasise higher frequency, and lowpass difference
    bands=[]
    for w1,w2 in [(4,1.0),(1.0,.4)]:
        y=(hp(v/dt[:,None],dt,w2)-hp(v/dt[:,None],dt,w1)); cs=[]
        for t in T1:
            g0=gyro(it,ic,a+t,b+t)@R.T/dt[:,None]; g=hp(g0,dt,w2)-hp(g0,dt,w1)
            cs.append((g*y).sum()/np.sqrt((g*g).sum()*(y*y).sum()))
        bands.append(tuple(np.round(peak(T1,np.array(cs)),3)))
    print('   bands 0.25-1Hz , 1-2.5Hz',bands,flush=True)
    return p
imuz=B+f'imu/zed2i/{Z}/data.csv'
for alg in ['orbslam3','cuvslam','okvis2','basalt']:
    report('SIELINKO','zed2i',Z,alg,imuz)
report('CITRUS07','citrusfarm','seq07','cuvslam',B+'imu/citrusfarm/seq07/data.csv')
report('EUROC','euroc_mav','MH_01_easy','cuvslam',B+'imu/euroc_mav/MH_01_easy/data.csv')
