"""Fit offset(t) = a + b t on the whole Sielinko recording, t in seconds since the first IMU stamp."""
import sys,json; sys.path.insert(0,'/data/imoroz/vslam-timing-corrected-20261031/scripts/analysis/imu_timing')
from tau_lib import *
imu='/data/imoroz/vslam-benchmark/datasets/zed2i/'+Z+'/mav0/imu0/data.csv'; I=load_imu(imu); N=16
W={}
for alg in SYS:
    w,t0=windows(traj('zed2i',Z,alg),I,N); W[alg]=w; print(alg,np.round(w[:,1],1).tolist(),flush=True)
t=np.mean([W[a][:,0] for a in SYS],axis=0)-t0; med=np.median([W[a][:,1] for a in SYS],axis=0)
from scipy.stats import theilslopes
# Theil-Sen over every system and window, intercept median(y-bx): spurious peaks in single windows must not steer the line.
x=np.concatenate([W[k][:,0]-t0 for k in SYS]); y=np.concatenate([W[k][:,1] for k in SYS])
b,a,_,_=theilslopes(y,x,method='joint'); res=med-(a+b*t); mad=float(np.median(abs(y-(a+b*x))))
print('window median',np.round(med,1).tolist()); print('t_s',np.round(t,0).tolist())
print('a_ms',a,'b_ms_per_s',b,'median abs resid ms',mad,'offset at start, end',a,a+b*t[-1],'n points',len(x))
json.dump(dict(method='Theil-Sen, 4 systems x 16 equal-count windows, VO against gyroscope',a_s=a/1e3,b_s_per_s=b/1e3,t_origin='first IMU stamp',windows=N,systems=SYS,window_centers_s=t.tolist(),window_median_ms=med.tolist(),median_abs_residual_ms=mad),open(sys.argv[1],'w'),indent=1)
